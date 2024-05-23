from aztec_gddt.helper import *
from aztec_gddt.types import *
from uuid import uuid4
from copy import deepcopy, copy
from random import choice
from scipy.stats import uniform
from .functional_parameterizations import determine_profitability


def s_gas_fee_l1(p: AztecModelParams, _2, _3, s, _5):
    key = "gas_fee_l1"
    random_value = value_from_param_timeseries_suf(p, s, "gas_fee_l1_time_series", key)
    past_value = s[key]
    value = round(
        p["past_gas_weight_fraction"] * past_value
        + (1 - p["past_gas_weight_fraction"]) * random_value
    )
    return (key, value)


def s_gas_fee_blob(p: AztecModelParams, _2, _3, s, _5):
    key = "gas_fee_blob"
    random_value = value_from_param_timeseries_suf(
        p, s, "gas_fee_blob_time_series", key
    )
    past_value = s[key]
    value = round(
        p["past_gas_weight_fraction"] * past_value
        + (1 - p["past_gas_weight_fraction"]) * random_value
    )
    return (key, value)


def p_init_process(
    params: AztecModelParams, _2, _3, state: AztecModelState
) -> SignalEvolveProcess:
    """
    Function for starting a new process which is activated is there is no current process,
    if the current process is in the finalized state or if it is in the skipped state. In those
    cases the new process will be one in the pending proposals state.

    Args:
         params (AztecModelParams): The current parameters of the model.
         state (AztecModelState): The current state of the model.

    Returns:
         Signal: The new process to be considered in the system.

    """

    if state["current_process"] is None:
        # Assumption: Lack of active process implies a new one being initiated
        do_init_process = True
    else:
        # Else, check if the current one is finalized
        do_init_process = state["current_process"].phase == SelectionPhase.finalized
        do_init_process |= state["current_process"].phase == SelectionPhase.skipped

    if do_init_process:
        new_process = Process(
            uuid=uuid4(),
            phase=SelectionPhase.pending_proposals,
            leading_sequencer=None,
            uncle_sequencers=None,
            current_phase_init_time=state["time_l1"],
            duration_in_current_phase=0,
            proofs_are_public=False,
            block_content_is_revealed=False,
            commit_bond_is_put_down=False,
            rollup_proof_is_commited=False,
            process_aborted=False,
        )
    else:
        new_process = None

    return {"update_process": new_process}


def p_select_proposal(
    params: AztecModelParams, _2, _3, state: AztecModelState
) -> SignalEvolveProcess:
    """
    First check if there is a valid process which is pending proposals and if so then
    select a sequencer from list of eligible sequencers, and determine uncle sequencers.

    Args:
        params (AztecModelParams): The current parameters of the model.
        state (AztecModelState): The current state of the model.

    Returns:
         Signal: The new process to be considered in the system.
    """

    process = state["current_process"]
    updated_process: Optional[Process] = None

    max_phase_duration = params["phase_duration_proposal_max_blocks"]

    if process is None:
        return {"update_process": updated_process}
    if process.phase != SelectionPhase.pending_proposals:
        return {"update_process": updated_process}

    remaining_time = max_phase_duration - process.duration_in_current_phase
    if remaining_time < 0:
        raw_proposals: dict[TxUUID, Proposal] = proposals_from_tx(state["transactions"])

        proposals = {
            k: p
            for k, p in raw_proposals.items()
            if p.when >= process.current_phase_init_time
        }

        if len(proposals) > 0:
            number_uncles: int = min(len(proposals) - 1, params["uncle_count"])

            ranked_proposals: list[Proposal] = sorted(
                proposals.values(), key=lambda p: p.score, reverse=True
            )

            winner_proposal: Proposal = ranked_proposals[0]
            if len(ranked_proposals) > 1:
                uncle_proposals: list[Proposal] = ranked_proposals[
                    1 : number_uncles + 1
                ]
            else:
                uncle_proposals = []

            updated_process = copy(process)
            updated_process.current_phase_init_time = state["time_l1"]

            updated_process.phase = SelectionPhase.pending_commit_bond
            updated_process.duration_in_current_phase = 0
            updated_process.leading_sequencer = winner_proposal.who
            updated_process.uncle_sequencers = [p.who for p in uncle_proposals]
            updated_process.tx_winning_proposal = winner_proposal.uuid
        else:
            updated_process = copy(process)
            updated_process.phase = SelectionPhase.skipped
            updated_process.duration_in_current_phase = 0

    return {"update_process": updated_process}


def p_commit_bond(
    params: AztecModelParams,
    _2,
    history: list[list[AztecModelState]],
    state: AztecModelState,
) -> SignalEvolveProcess:
    process: Process | None = state["current_process"]
    updated_process: Optional[Process] = None
    new_transactions = list()
    advance_blocks = 0
    transfers: list[Transfer] = []
    bond_amount = params["commit_bond_amount"]
    commit_duration = params["phase_duration_commit_bond_max_blocks"]

    if process is None:
        return {
            "update_process": updated_process,
            "new_transactions": new_transactions,
            "advance_l1_blocks": advance_blocks,
            "transfers": transfers,
        }
    if process.phase != SelectionPhase.pending_commit_bond:
        return {
            "update_process": updated_process,
            "new_transactions": new_transactions,
            "advance_l1_blocks": advance_blocks,
            "transfers": transfers,
        }

    remaining_time = commit_duration - process.duration_in_current_phase
    if remaining_time < 0:
        # Move to Proof Race mode if duration is expired
        updated_process = copy(process)
        updated_process.phase = SelectionPhase.proof_race
        updated_process.entered_race_mode = True
        updated_process.duration_in_current_phase = 0

        # Slash leading sequencer if no commit bond is put down.
        slashed_amount = params["slash_params"].failure_to_commit_bond
        transfers.append(
            Transfer(
                source=updated_process.leading_sequencer,
                destination="burnt",
                amount=slashed_amount,
                kind=TransferKind.slash_sequencer,
                to_sequencer=True,
            )
        )
    else:
        # NOTE: Costs now include gas fees and safety buffer.
        gas: Gas = params["gas_estimators"].commitment_bond(state)
        fee = gas * state["gas_fee_l1"]

        expected_rewards, expected_costs, payoff_reveal = determine_profitability(
            "Commit Bond", params, fee
        )

        if payoff_reveal >= 0:

            # If duration is not expired, do  a trial to see if bond is commited
            agent_decides_to_reveal_commit_bond = bernoulli_trial(
                probability=trial_probability(
                    params["phase_duration_commit_bond_max_blocks"],
                    params["final_probability"],
                )
            )

            block_is_uncensored = check_for_censorship(params, state)

            if agent_decides_to_reveal_commit_bond and block_is_uncensored:
                updated_process = copy(process)
                lead_seq: Agent = state["agents"][process.leading_sequencer]
                proposal_uuid = process.tx_winning_proposal
                proving_market_is_used = bernoulli_trial(
                    params["proving_marketplace_usage_probability"]
                )

                if proving_market_is_used:
                    provers: list[AgentUUID] = [
                        a_id
                        for (a_id, a) in state["agents"].items()
                        if a.is_prover and a.balance >= bond_amount
                    ]

                    if len(provers) > 0:
                        prover: AgentUUID = choice(provers)
                    else:
                        if lead_seq.balance >= bond_amount:
                            prover = updated_process.leading_sequencer
                        else:
                            prover = None
                else:
                    if lead_seq.balance >= bond_amount:
                        prover = updated_process.leading_sequencer
                    else:
                        prover = None

                if prover is not None:
                    # TODO: double-check this.
                    advance_blocks = remaining_time
                    updated_process.phase = SelectionPhase.pending_reveal
                    updated_process.duration_in_current_phase = 0
                    tx = CommitmentBond(
                        who=prover,
                        when=state["time_l1"],
                        uuid=uuid4(),
                        gas=gas,
                        fee=fee,
                        proposal_tx_uuid=proposal_uuid,
                        prover_uuid=prover,
                        bond_amount=bond_amount,
                    )
                    new_transactions.append(tx)
                    updated_process.tx_commitment_bond = tx.uuid

    return {
        "update_process": updated_process,
        "new_transactions": new_transactions,
        "advance_l1_blocks": advance_blocks,
        "transfers": transfers,
    }


def p_reveal_content(
    params: AztecModelParams,
    _2,
    history: list[list[AztecModelState]],
    state: AztecModelState,
) -> SignalEvolveProcess:
    """
    Advances state of Processes that have revealed block content.
    """

    # Note: Advances state of Process in reveal phase that have revealed block content.
    process = state["current_process"]
    updated_process: Optional[Process] = None
    advance_blocks = 0
    new_transactions = list()
    transfers: list[Transfer] = []

    max_reveal_duration = params["phase_duration_reveal_max_blocks"]

    if process is None:
        pass
    else:
        if process.phase == SelectionPhase.pending_reveal:

            # If the process has blown the phase duration
            remaining_time = max_reveal_duration - process.duration_in_current_phase
            if remaining_time < 0:
                updated_process = copy(process)
                updated_process.phase = SelectionPhase.proof_race
                updated_process.entered_race_mode = True
                updated_process.duration_in_current_phase = 0

                # Slash leading sequencer if content is not revealed.
                slashed_amount = params["slash_params"].failure_to_reveal_block
                transfers.append(
                    Transfer(
                        source=updated_process.leading_sequencer,
                        destination="burnt",
                        amount=slashed_amount,
                        kind=TransferKind.slash_sequencer,
                        to_sequencer=True,
                    )
                )
            else:
                # NOTE: Costs now include gas fees and safety buffer.
                gas: Gas = params["gas_estimators"].content_reveal(state)
                fee = gas * state["gas_fee_l1"]

                expected_rewards, expected_costs, payoff_reveal = (
                    determine_profitability("Reveal Content", params, fee)
                )

                agent_expects_profit = payoff_reveal >= 0

                agent_decides_to_reveal_block_content = bernoulli_trial(
                    probability=trial_probability(
                        params["phase_duration_reveal_max_blocks"],
                        params["final_probability"],
                    )
                )

                block_is_uncensored = check_for_censorship(params, state)

                if (
                    agent_expects_profit
                    and agent_decides_to_reveal_block_content
                    and block_is_uncensored
                ):
                    updated_process = copy(process)
                    advance_blocks = remaining_time
                    updated_process.phase = SelectionPhase.pending_rollup_proof
                    updated_process.duration_in_current_phase = 0

                    who = updated_process.leading_sequencer
                    blob_gas: BlobGas = params["gas_estimators"].content_reveal_blob(
                        state
                    )
                    blob_fee: Gwei = blob_gas * state["gas_fee_blob"]

                    tx_count = params["tx_estimators"].transaction_count(state)
                    tx_avg_size = int(
                        state["transactions"][process.tx_winning_proposal].size
                        / tx_count
                    )  # type: ignore
                    tx_avg_fee_per_size = params[
                        "tx_estimators"
                    ].transaction_average_fee_per_size(state)

                    tx = ContentReveal(
                        who=who,
                        when=state["time_l1"],
                        uuid=uuid4(),
                        gas=gas,
                        fee=fee,
                        blob_gas=blob_gas,
                        blob_fee=blob_fee,
                        transaction_count=tx_count,
                        transaction_avg_size=tx_avg_size,
                        transaction_avg_fee_per_size=tx_avg_fee_per_size,
                    )

                    new_transactions.append(tx)
                    updated_process.tx_content_reveal = tx.uuid

    return {
        "update_process": updated_process,
        "new_transactions": new_transactions,
        "advance_l1_blocks": advance_blocks,
    }


def p_submit_proof(
    params: AztecModelParams, _2, _3, state: AztecModelState
) -> SignalEvolveProcess:
    """
    Advances state of Processes that have  submitted rollup proofs.
    """
    process = state["current_process"]
    updated_process: Optional[Process] = None
    new_transactions = list()
    advance_blocks = 0
    transfers: list[Transfer] = []

    phase_max_duration = params["phase_duration_rollup_max_blocks"]

    if process is None:
        pass
    else:
        if process.phase == SelectionPhase.pending_rollup_proof:
            remaining_time = phase_max_duration - process.duration_in_current_phase
            if remaining_time < 0:
                updated_process = copy(process)
                updated_process.phase = SelectionPhase.skipped
                updated_process.duration_in_current_phase = 0

                # Determine who should be slashed, and how much.
                transactions = state["transactions"]
                commit_bond_id = updated_process.tx_commitment_bond
                commit_bond: CommitmentBond = transactions.get(
                    commit_bond_id, None
                )  # type: ignore
                who_to_slash = commit_bond.prover_uuid
                how_much_to_slash = commit_bond.bond_amount

                # Slash the prover for failing to reveal the proof.
                slash_transfer = Transfer(
                    source=who_to_slash,
                    destination="burnt",
                    amount=how_much_to_slash,
                    kind=TransferKind.slash_prover,
                    to_prover=True,
                )
                transfers.append(slash_transfer)

            else:
                gas: Gas = params["gas_estimators"].content_reveal(state)
                fee = gas * state["gas_fee_l1"]

                expected_rewards, expected_costs, payoff_reveal = (
                    determine_profitability("Submit Proof", params, fee)
                )
                agent_expects_profit = payoff_reveal >= 0

                agent_decides_to_reveal_rollup_proof = bernoulli_trial(
                    probability=trial_probability(
                        params["phase_duration_rollup_max_blocks"],
                        params["final_probability"],
                    )
                )

                block_is_uncensored = check_for_censorship(params, state)

                if (
                    agent_decides_to_reveal_rollup_proof
                    and agent_expects_profit
                    and block_is_uncensored
                ):
                    updated_process = copy(process)
                    advance_blocks = remaining_time
                    updated_process.phase = SelectionPhase.finalized
                    updated_process.duration_in_current_phase = 0
                    transactions = state["transactions"]

                    commit_bond_id = updated_process.tx_commitment_bond
                    commit_bond: CommitmentBond = transactions.get(  # type: ignore
                        commit_bond_id, None
                    )  # type: ignore
                    who = commit_bond.prover_uuid
                    gas: Gas = params["gas_estimators"].rollup_proof(  # type: ignore
                        state
                    )  # type: ignore
                    fee: Gwei = gas * state["gas_fee_l1"]  # type: ignore

                    tx = RollupProof(
                        who=who, when=state["time_l1"], uuid=uuid4(), gas=gas, fee=fee
                    )

                    new_transactions.append(tx)
                    updated_process.tx_rollup_proof = tx.uuid

    return {
        "update_process": updated_process,
        "new_transactions": new_transactions,
        "advance_l1_blocks": advance_blocks,
        "transfers": transfers,
    }


def p_race_mode(
    params: AztecModelParams, _2, _3, state: AztecModelState
) -> SignalEvolveProcess:
    """
    Logic for race mode.
    """
    process = state["current_process"]
    updated_process: Optional[Process] = None
    new_transactions: list[TransactionL1] = list()

    max_phase_duration = params["phase_duration_race_max_blocks"]

    # NOTE: Logic of race mode is different.
    # No check here for L1 censorship.

    if process is None:
        pass
    else:
        if process.phase == SelectionPhase.proof_race:
            remaining_time = max_phase_duration - process.duration_in_current_phase
            if remaining_time < 0:
                updated_process = copy(process)
                updated_process.phase = SelectionPhase.skipped
                updated_process.duration_in_current_phase = 0
            else:
                # Assumption: there is a hard-coded L1 Builder agent
                # who immediately ends the race mode.
                who = "l1-builder"
                gas: Gas = params["gas_estimators"].content_reveal(state)
                fee: Gwei = gas * state["gas_fee_l1"]
                blob_gas: BlobGas = params["gas_estimators"].content_reveal_blob(state)
                blob_fee: Gwei = blob_gas * state["gas_fee_blob"]

                tx_count = params["tx_estimators"].transaction_count(state)
                tx_avg_size = int(
                    state["transactions"][process.tx_winning_proposal].size / tx_count
                )  # type: ignore
                tx_avg_fee_per_size = params[
                    "tx_estimators"
                ].transaction_average_fee_per_size(state)

                tx_1 = RollupProof(
                    who=who, when=state["time_l1"], uuid=uuid4(), gas=gas, fee=fee
                )

                tx_2 = ContentReveal(
                    who=who,
                    when=state["time_l1"],
                    uuid=uuid4(),
                    gas=gas,
                    fee=fee,
                    blob_gas=blob_gas,
                    blob_fee=blob_fee,
                    transaction_count=tx_count,
                    transaction_avg_size=tx_avg_size,
                    transaction_avg_fee_per_size=tx_avg_fee_per_size,
                )

                new_transactions.append(tx_1)
                new_transactions.append(tx_2)

                updated_process = copy(process)
                updated_process.tx_rollup_proof = tx_1.uuid
                updated_process.block_content_is_revealed = True
                updated_process.tx_content_reveal = tx_2.uuid
                updated_process.phase = SelectionPhase.finalized
                updated_process.duration_in_current_phase = 0

    return {"update_process": updated_process, "new_transactions": new_transactions}


def s_process(
    params: AztecModelParams,
    _2,
    _3,
    state: AztecModelState,
    signal: SignalEvolveProcess,
):
    """
    Logic for updating process.
    """
    updated_process = signal.get("update_process", state["current_process"])
    # Update only if there's an relevant signal.
    value = updated_process if updated_process is not None else state["current_process"]
    return ("current_process", value)


def s_transactions_new_proposals(
    params: AztecModelParams, _2, _3, state: AztecModelState, _5
):
    """
    Logic for submitting new proposals.
    """

    new_transactions = state["transactions"].copy()
    current_process: Process | None = state["current_process"]
    new_proposals: dict[TxUUID, Proposal] = dict()

    if current_process is None:
        return ("transactions", new_transactions)
    if current_process.phase != SelectionPhase.pending_proposals:
        return ("transactions", new_transactions)

    current_proposers: set[AgentUUID] = {
        p.who
        for p in new_transactions.values()
        if p.when >= current_process.current_phase_init_time
    }
    potential_proposers: set[AgentUUID] = {
        u.uuid
        for u in state["agents"].values()
        if u.uuid not in current_proposers
        and u.is_sequencer
        and u.staked_amount >= params["minimum_stake"]
    }

    for potential_proposer in potential_proposers:
        if bernoulli_trial(
            trial_probability(
                params["phase_duration_proposal_max_blocks"],
                params["final_probability"],
            )
        ):

            tx_uuid = uuid4()
            gas: Gas = params["gas_estimators"].proposal(state)
            fee: Gwei = gas * state["gas_fee_l1"]
            score = uniform.rvs()  # Assumption: score is always uniform
            size = params["tx_estimators"].proposal_average_size(state)
            public_share = 0.5  # Assumption: Share of public function calls

            block_is_uncensored = check_for_censorship(params, state)

            if block_is_uncensored:
                new_proposal = Proposal(
                    who=potential_proposer,
                    when=state["time_l1"],
                    uuid=tx_uuid,
                    gas=gas,
                    fee=fee,
                    score=score,
                    size=size,
                    public_composition=public_share,
                )

                new_proposals[tx_uuid] = new_proposal

    new_transactions = {**new_transactions, **new_proposals}
    return ("transactions", new_transactions)


def s_advance_blocks(_1, _2, _3, state, signal: SignalEvolveProcess):
    return ("advance_l1_blocks", signal.get("advance_l1_blocks", 0))


def s_transactions(
    params: AztecModelParams,
    _2,
    _3,
    state: AztecModelState,
    signal: SignalEvolveProcess,
):
    """
    Logic for new transactions.
    """

    new_tx_list: list[TransactionL1] = signal.get(
        "new_transactions", list()
    )  # type: ignore

    new_tx_dict: dict[TxUUID, TransactionL1] = {tx.uuid: tx for tx in new_tx_list}

    new_transactions = {**state["transactions"].copy(), **new_tx_dict}

    return ("transactions", new_transactions)


def s_slashes_to_prover(
    params: AztecModelParams,
    _2,
    _3,
    state: AztecModelState,
    signal: SignalEvolveProcess,
):
    """
    Logic for keeping track of how many slashes have occurred.
    """
    old_slashes_to_prover = state["slashes_to_provers"]
    transfers: Sequence[Transfer] = signal.get("transfers", [])  # type: ignore

    # Calculate the number of slashes of each type to add
    delta_slashes_prover = len(
        [
            transfer
            for transfer in transfers
            if (transfer.kind == TransferKind.slash_prover)
            and (transfer.to_prover == True)
        ]
    )

    updated_slashes_to_prover = old_slashes_to_prover + delta_slashes_prover

    return ("slashes_to_provers", updated_slashes_to_prover)


def s_slashes_to_sequencer(
    params: AztecModelParams,
    _2,
    _3,
    state: AztecModelState,
    signal: SignalEvolveProcess,
):
    """
    Logic for keeping track of how many slashes have occurred.
    """
    old_slashes_to_sequencers = state["slashes_to_sequencers"]
    transfers: Sequence[Transfer] = signal.get("transfers", [])  # type: ignore

    # Calculate the number of slashes of each type to add
    delta_slashes_sequencers = len(
        [
            transfer
            for transfer in transfers
            if transfer.kind == TransferKind.slash_sequencer and transfer.to_sequencer
        ]
    )

    updated_slashes_to_sequencer = old_slashes_to_sequencers + delta_slashes_sequencers

    return ("slashes_to_sequencers", updated_slashes_to_sequencer)


def s_agent_transfer(
    params: AztecModelParams,
    _2,
    _3,
    state: AztecModelState,
    signal: SignalEvolveProcess,
):
    """
    Logic for transferring tokens between agents and burn sink.
    """
    updated_agents = state["agents"].copy()
    transfers: Sequence[Transfer] = signal.get("transfers", [])  # type: ignore

    for transfer in transfers:
        if transfer.kind == TransferKind.conventional:
            updated_agents[transfer.source].balance -= transfer.amount
            updated_agents[transfer.destination].balance += transfer.amount
        elif transfer.kind == TransferKind.slash_sequencer:
            updated_agents[transfer.source].staked_amount -= transfer.amount
            updated_agents[transfer.destination].balance += transfer.amount
        elif transfer.kind == TransferKind.slash_prover:
            updated_agents[transfer.source].balance -= transfer.amount
            updated_agents[transfer.destination].balance += transfer.amount
        else:
            raise Exception(f"Transfer logic is undefined for {transfer.kind}")

        assert (
            updated_agents[transfer.source].balance >= 0
        ), "This transfer resulted in a negative balance"
        assert (
            updated_agents[transfer.source].staked_amount >= 0
        ), "This transfer results in a negative staked amount"

    return ("agents", updated_agents)


def p_block_reward(
    params: AztecModelParams, _2, _3, state: AztecModelState
) -> SignalPayout:
    p: Process = state["current_process"]  # type: ignore
    if p.phase == SelectionPhase.finalized:

        # Assumption: this assumes that the average L2 block duration
        # will be the max L2 block duration
        expected_l2_blocks_per_day = params["l1_blocks_per_day"] / total_phase_duration(
            params
        )
        reward = params["daily_block_reward"] / expected_l2_blocks_per_day
    else:
        reward = 0
    return SignalPayout(block_reward=reward)


def p_fee_cashback(
    params: AztecModelParams, _2, _3, state: AztecModelState
) -> SignalPayout:
    p: Process = state["current_process"]  # type: ignore
    if p.phase == SelectionPhase.finalized:

        txs: dict[TxUUID, AnyL1Transaction] = state["transactions"]
        # L1 Fees
        total_fees: float = 0
        total_fees += txs[p.tx_winning_proposal].fee
        total_fees += txs[p.tx_content_reveal].fee
        total_fees += txs[p.tx_rollup_proof].fee
        total_fees += (
            txs[p.tx_commitment_bond].fee if p.tx_commitment_bond is not None else 0
        )

        # Blob Fees
        total_fees += txs[p.tx_content_reveal].blob_fee  # type: ignore

        total_fees *= params["gwei_to_tokens"]
    else:
        total_fees = 0

    return SignalPayout(fee_cashback=total_fees)


def p_fee_from_users(
    params: AztecModelParams, _2, _3, state: AztecModelState
) -> SignalPayout:
    p: Process = state["current_process"]  # type: ignore
    if p.phase == SelectionPhase.finalized:
        txs: dict[TxUUID, AnyL1Transaction] = state["transactions"]
        total_fees = txs[p.tx_content_reveal].total_tx_fee  # type: ignore
    else:
        total_fees = 0

    return SignalPayout(fee_from_users=total_fees)


def s_total_rewards_provers(
    params: AztecModelParams, _2, _3, state: AztecModelState, signal: SignalPayout
):

    p: Process = state["current_process"]  # type: ignore
    if p.phase == SelectionPhase.finalized:
        txs = state["transactions"]
        total_rewards = signal.get("block_reward", 0.0)

        old_total_rewards_provers = state["total_rewards_provers"]
        delta_rewards_provers = total_rewards * params["rewards_to_provers"]

        sequencer_uuid = state["transactions"][p.tx_rollup_proof].who

        if not p.entered_race_mode:
            prover_uuid = txs[p.tx_commitment_bond].prover_uuid  # type: ignore
            relays = [a_id for (a_id, a) in state["agents"].items() if a.is_relay]
            relay_uuid: AgentUUID = choice(relays)
        else:
            prover_uuid = sequencer_uuid
            relay_uuid = sequencer_uuid

        # Track Rewards
        new_total_rewards_provers = old_total_rewards_provers + delta_rewards_provers
        return ("total_rewards_provers", new_total_rewards_provers)
    else:
        return ("total_rewards_provers", state["total_rewards_provers"])


def s_total_rewards_sequencers(
    params: AztecModelParams, _2, _3, state: AztecModelState, signal: SignalPayout
):
    old_total_rewards_sequencers = state["total_rewards_sequencers"]

    p: Process = state["current_process"]  # type: ignore
    if p.phase == SelectionPhase.finalized:
        txs = state["transactions"]
        total_rewards = signal.get("block_reward", 0.0)
        agents: dict[AgentUUID, Agent] = state["agents"].copy()

        delta_rewards_relay = total_rewards * params["rewards_to_relay"]
        delta_rewards_prover = total_rewards * params["rewards_to_provers"]
        delta_rewards_sequencer = total_rewards - (
            delta_rewards_prover + delta_rewards_relay
        )

        sequencer_uuid = state["transactions"][p.tx_rollup_proof].who

        if not p.entered_race_mode:
            prover_uuid = txs[p.tx_commitment_bond].prover_uuid  # type: ignore
            relays = [a_id for (a_id, a) in state["agents"].items() if a.is_relay]
            relay_uuid: AgentUUID = choice(relays)
        else:
            prover_uuid = sequencer_uuid
            relay_uuid = sequencer_uuid

        # Track Rewards
        new_total_rewards_sequencers = (
            old_total_rewards_sequencers + delta_rewards_sequencer
        )
        return ("total_rewards_sequencers", new_total_rewards_sequencers)
    else:
        return ("total_rewards_sequencers", state["total_rewards_sequencers"])


def s_total_rewards_relays(
    params: AztecModelParams, _2, _3, state: AztecModelState, signal: SignalPayout
):
    old_total_rewards_relays = state["total_rewards_relays"]

    p: Process = state["current_process"]  # type: ignore
    if p.phase == SelectionPhase.finalized:
        txs = state["transactions"]
        total_rewards = signal.get("block_reward", 0.0)
        agents: dict[AgentUUID, Agent] = state["agents"].copy()

        delta_rewards_prover = total_rewards * params["rewards_to_provers"]
        delta_rewards_relay = total_rewards * params["rewards_to_relay"]
        delta_rewards_sequencer = total_rewards - (
            delta_rewards_relay + delta_rewards_prover
        )

        sequencer_uuid = state["transactions"][p.tx_rollup_proof].who

        if not p.entered_race_mode:
            prover_uuid = txs[p.tx_commitment_bond].prover_uuid  # type: ignore
            relays = [a_id for (a_id, a) in state["agents"].items() if a.is_relay]
            relay_uuid: AgentUUID = choice(relays)
        else:
            prover_uuid = sequencer_uuid
            relay_uuid = sequencer_uuid

        # Track Rewards
        new_total_rewards_relays = old_total_rewards_relays + delta_rewards_relay
        return ("total_rewards_relays", new_total_rewards_relays)
    else:
        return ("total_rewards_relays", state["total_rewards_relays"])


def s_agents_rewards(
    params: AztecModelParams, _2, _3, state: AztecModelState, signal: SignalPayout
):

    p: Process = state["current_process"]  # type: ignore
    if p.phase == SelectionPhase.finalized:
        txs = state["transactions"]
        total_rewards = signal.get("block_reward", 0.0)
        agents: dict[AgentUUID, Agent] = state["agents"].copy()

        rewards_relay = total_rewards * params["rewards_to_relay"]
        rewards_prover = total_rewards * params["rewards_to_provers"]
        rewards_sequencer = total_rewards - (rewards_relay + rewards_prover)

        sequencer_uuid = state["transactions"][p.tx_rollup_proof].who

        if not p.entered_race_mode:
            prover_uuid = txs[p.tx_commitment_bond].prover_uuid  # type: ignore
            relays = [a_id for (a_id, a) in state["agents"].items() if a.is_relay]
            relay_uuid: AgentUUID = choice(relays)
        else:
            prover_uuid = sequencer_uuid
            relay_uuid = sequencer_uuid

        # Disburse Rewards
        agents[sequencer_uuid].balance += rewards_sequencer
        agents[prover_uuid].balance += rewards_prover
        agents[relay_uuid].balance += rewards_relay
        return ("agents", agents)
    else:
        return ("agents", state["agents"])


def s_token_supply(
    params: AztecModelParams,
    _2,
    _3,
    state: AztecModelState,
    signal: SignalEvolveProcess,
):
    """
    Logic for token supply.
    """
    return ("token_supply", TokenSupply.from_state(state))


def s_agent_restake(
    params: AztecModelParams,
    _2,
    history,
    state: AztecModelState,
    signal: SignalEvolveProcess,
):
    new_agents = state["agents"].copy()

    sequencers = {k: v for k, v in new_agents.items() if v.is_sequencer}
    for k, v in sequencers.items():
        if v.staked_amount < params["minimum_stake"]:
            # Assumption: Sequencers top-up from balance with 2 more ETH than necessary
            max_amount_to_stake = params["minimum_stake"] - v.staked_amount + 2.0
            amount_to_stake = min(max_amount_to_stake, v.balance)
            v.balance -= amount_to_stake
            v.staked_amount += amount_to_stake

    return ("agents", new_agents)


s_finalized_blocks_count_lambda_function = lambda _1, _2, _3, s, _5: (
    "finalized_blocks_count",
    (
        s["finalized_blocks_count"] + 1
        if s["current_process"].phase == SelectionPhase.finalized
        else s["finalized_blocks_count"]
    ),
)
