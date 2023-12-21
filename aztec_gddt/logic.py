from copy import deepcopy, copy
from typing import Callable
from uuid import uuid4

from random import choice

from cadCAD_tools.types import VariableUpdate  # type: ignore

from aztec_gddt.helper import *
from aztec_gddt.types import *

from scipy.stats import bernoulli, uniform, norm  # type: ignore


def generic_policy(_1, _2, _3, _4) -> dict:
    """Function to generate pass through policy

    Args:
        _1
        _2
        _3
        _4

    Returns:
        dict: Empty dictionary
    """
    return {}

#######################################
## General system helper functions.  ##
#######################################


def replace_suf(variable: str, default_value=0.0) -> Callable:
    """Creates replacing function for state update from string

    Args:
        variable (str): The variable name that is updated

    Returns:
        function: A function that continues the state across a substep
    """
    return lambda _1, _2, _3, state, signal: (variable, signal.get(variable, default_value))


def add_suf(variable: str, default_value=0.0) -> Callable:
    """Creates replacing function for state update from string

    Args:
        variable (str): The variable name that is updated

    Returns:
        function: A function that continues the state across a substep
    """
    return lambda _1, _2, _3, state, signal: (variable, signal.get(variable, default_value) + state[variable])


#######################################
## Overall functions, not attached   ##
## to any particular phase.          ##
#######################################

def p_evolve_time(params: AztecModelParams, _2, _3, _4) -> SignalTime:
    """Policy function giving the change in number of blocks. 

    Args:
         params (AztecModelParams): The current parameters of the model.

    Returns:
        Signal: 
            a dictionary of variables that can be used in an update
    """
    return {'delta_blocks': params['timestep_in_blocks']}


def s_block_time(params: AztecModelParams, _2, _3,
                 state: AztecModelState,
                 signal: SignalTime) -> VariableUpdate:
    """State update function advancing block time.  

    Args:
         params (AztecModelParams): The current parameters of the model.
         state (AztecModelState): The current state of the model.
         signal (Signal): The Signal, generated in p_evolve_time, of how many blocks to advance time. 

    Returns:
        VariableUpdate:
            A two-element tuple that all state update functions must return.
    """
    return ('time_l1', state['time_l1'] + signal['delta_blocks'])  # type: ignore


def s_delta_blocks(_1, _2, _3, _4, signal: SignalTime) -> VariableUpdate:
    """
    State update function for change in block number. 

    Args: 
        signal (Signal): The Signal, generated in p_evolve_time, of how many blocks to advance time. 

    Returns: 
        VariableUpdate
    """
    return ('delta_blocks', signal.get('delta_blocks', 0))


def s_current_process_time(_1,
                           _2,
                           _3,
                           state: AztecModelState,
                           signal: SignalTime) -> VariableUpdate:
    """
    State update function for change in block number. 

    Args: 
        signal (Signal): The Signal, generated in p_evolve_time, of how many blocks to advance time. 

    Returns: 
        VariableUpdate
    """
    updated_process: Process | None = copy(state['current_process'])
    if updated_process is not None:
        # type: ignore
        updated_process.duration_in_current_phase += signal.get('delta_blocks', 0)
    else:
        pass

    return ('current_process', updated_process)


def s_gas_fee_l1(params: AztecModelParams,
                 _2,
                 _3,
                 state: AztecModelState,
                 signal: SignalEvolveProcess) -> VariableUpdate:
    """
    Logic for submitting new proposals.
    """
    return ('gas_fee_l1', state['gas_fee_l1'])


def s_gas_fee_blob(params: AztecModelParams,
                   _2,
                   _3,
                   state: AztecModelState,
                   signal: SignalEvolveProcess) -> VariableUpdate:
    """
    Logic for submitting new proposals.
    """
    return ('gas_fee_blob', state['gas_fee_blob'])


def p_init_process(params: AztecModelParams,
                   _2,
                   _3,
                   state: AztecModelState) -> SignalEvolveProcess:
    """
    Initializes a specific process. 

    Args:
         params (AztecModelParams): The current parameters of the model.
         state (AztecModelState): The current state of the model.

    Returns:
         Signal: The new process to be considered in the system. 

    """

    #######################################
    ## Logical check to determine if     ##
    ## a new process will be  initiated. ##
    ## Checks to see if current phase    ##
    ## of last process is one of         ##
    ## pending_rollup_proof, skipped,    ##
    ## or reorg.                         ##
    #######################################

    if state['current_process'] is None:
        # XXX: Lack of active process implies on a new one being initiated
        do_init_process = True
    else:
        # Else, check if the current one is finalized
        do_init_process = state['current_process'].phase == SelectionPhase.finalized
        do_init_process |= state['current_process'].phase == SelectionPhase.skipped

    #######################################
    ## Logic to create new process       ##
    #######################################

    if do_init_process:
        new_process = Process(uuid=uuid4(),
                              phase=SelectionPhase.pending_proposals,
                              leading_sequencer=None,
                              uncle_sequencers=None,
                              current_phase_init_time=state['time_l1'],
                              duration_in_current_phase=0,
                              proofs_are_public=False,
                              block_content_is_revealed=False,
                              commit_bond_is_put_down=False,
                              rollup_proof_is_commited=False,
                              process_aborted=False)
    else:
        new_process = None

    return {'update_process': new_process}


def p_select_proposal(params: AztecModelParams,
                      _2,
                      _3,
                      state: AztecModelState) -> SignalEvolveProcess:
    """
    Select a sequencer from list of eligible sequencers, and
    determine uncle sequencers. 

    Args:
        params (AztecModelParams): The current parameters of the model.
        state (AztecModelState): The current state of the model.

    Returns:
         Signal: The new process to be considered in the system. 
    """

    #######################################
    ## Decide which processes are valid  ##
    ## 1. current phase of process must  ##
    ##    be pending proposals           ##
    ## 2. the duration is greater than   ##
    ##    proposal duration.             ##
    #######################################
    process = state['current_process']
    updated_process: Optional[Process] = None

    if process is None:
        pass
    else:
        if process.phase == SelectionPhase.pending_proposals:
            if process.duration_in_current_phase > params['phase_duration_proposal']:
                # TODO: filter out invalid proposals
                # J: Which invalid proposals are we expecting here? Anything "spam/invalid" would just be ignored, not sure we need to sim that, unless for blockspace
                # TODO: Above seems incorrect - if duration of phase exceeds duration, the next phase starts.
                proposals: dict[TxUUID, Proposal] = proposals_from_tx(
                    state['transactions'])
                if len(proposals) > 0:
                    # TODO: check if true
                    number_uncles: int = min(
                        len(proposals) - 1, params['uncle_count'])

                    ranked_proposals: list[Proposal] = sorted(proposals.values(),
                                                              key=lambda p: p.score,
                                                              reverse=True)

                    winner_proposal: Proposal = ranked_proposals[0]
                    if len(ranked_proposals) > 1:
                        uncle_proposals: list[Proposal] = ranked_proposals[1:number_uncles+1]
                    else:
                        uncle_proposals = []

                    updated_process = copy(process)
                    updated_process.phase = SelectionPhase.pending_reveal
                    updated_process.duration_in_current_phase = 0
                    updated_process.leading_sequencer = winner_proposal.uuid
                    updated_process.uncle_sequencers = [
                        p.uuid for p in uncle_proposals]
                else:
                    # TODO: check what happens if there are no proposals
                    updated_process = copy(process)
                    updated_process.phase = SelectionPhase.skipped
                    updated_process.duration_in_current_phase = 0
            else:
                pass
        else:
            pass

    return {'update_process': updated_process}


def p_commit_bond(params: AztecModelParams,
                  _2,
                  _3,
                  state: AztecModelState) -> SignalEvolveProcess:
    process: Process | None = state['current_process']
    updated_process: Optional[Process] = None
    new_transactions = list()

    if process is None:
        pass
    else:
        if process.phase == SelectionPhase.pending_commit_bond:
            # Move to Proof Race mode if duration is expired
            if process.duration_in_current_phase > params['phase_duration_commit_bond']:
                updated_process = copy(process)
                updated_process.phase = SelectionPhase.proof_race
                updated_process.entered_race_mode = True
                updated_process.duration_in_current_phase = 0
            else:
                # If duration is not expired, do  a trial to see if bond is commited
                if bernoulli_trial(probability=params['commit_bond_reveal_probability']) is True:
                    updated_process = copy(process)
                    updated_process.phase = SelectionPhase.pending_reveal
                    updated_process.duration_in_current_phase = 0

                    gas: Gas = params['gas_estimators'].commitment_bond(state)
                    fee = gas * state['gas_fee_l1']
                    proposal_uuid = updated_process.tx_winning_proposal

                    if bernoulli_trial(params['proving_marketplace_usage_probability']) is True:
                        provers: list[AgentUUID] = [
                            a_id for (a_id, a) in state['agents'].items() if a.is_prover]
                        # TODO: what about relays?
                        prover: AgentUUID = choice(provers)
                        bond_amount = 0.0  # TODO: open question
                    else:
                        prover = updated_process.leading_sequencer
                        bond_amount = 0.0  # TODO: open question

                    if state['gas_fee_l1'] <= params['gas_threshold_for_tx']:
                        tx = CommitmentBond(who=updated_process.leading_sequencer,
                                            when=state['time_l1'],
                                            uuid=uuid4(),
                                            gas=gas,
                                            fee=fee,
                                            proposal_tx_uuid=proposal_uuid,
                                            prover_uuid=prover,
                                            bond_amount=bond_amount)
                        new_transactions.append(tx)
                        updated_process.tx_commitment_bond = tx.uuid
                    else:
                        pass
                else:
                    # else, nothing happens
                    pass
        else:
            pass

    return {'update_process': updated_process,
            'new_transactions': new_transactions}


def p_reveal_content(params: AztecModelParams,
                     _2,
                     _3,
                     state: AztecModelState) -> SignalEvolveProcess:
    """
    Advances state of Processes that have revealed block content.
    TODO: check if race mode is taken into consideration. We may want to decouple 
    user actions from the evolving logic.
    """

    # Note: Advances state of Process in reveal phase that have revealed block content.
    process = state['current_process']
    updated_process: Optional[Process] = None
    new_transactions = list()

    if process is None:
        pass
    else:
        if process.phase == SelectionPhase.pending_reveal:
            # If the process has blown the phase duration
            if process.duration_in_current_phase > params['phase_duration_reveal']:
                updated_process = copy(process)
                updated_process.phase = SelectionPhase.proof_race
                updated_process.entered_race_mode = True
                updated_process.duration_in_current_phase = 0
                # TODO: To allow for fixed phase time, we might just add another check here - if duration > params and if content is not revealed -> proof_race
            else:
                if bernoulli_trial(probability=params['block_content_reveal_probability']) is True:
                    updated_process = copy(process)
                    updated_process.phase = SelectionPhase.pending_rollup_proof
                    updated_process.duration_in_current_phase = 0

                    who = updated_process.leading_sequencer  # XXX
                    gas: Gas = params['gas_estimators'].content_reveal(state)
                    fee: Gwei = gas * state['gas_fee_l1']
                    blob_gas: BlobGas = params['gas_estimators'].content_reveal_blob(
                        state)
                    blob_fee: Gwei = blob_gas * state['gas_fee_blob']

                    tx_count = params['tx_estimators'].transaction_count(state)
                    tx_avg_size = int(state['transactions'][process.tx_winning_proposal].size / tx_count) # type: ignore
                    tx_avg_fee_per_size = params['tx_estimators'].transaction_average_fee_per_size(
                        state)

                    if state['gas_fee_l1'] <= params['gas_threshold_for_tx'] & state['gas_fee_blob'] <= params['blob_gas_threshold_for_tx']:
                        tx = ContentReveal(who=who,
                                        when=state['time_l1'],
                                        uuid=uuid4(),
                                        gas=gas,
                                        fee=fee,
                                        blob_gas=blob_gas,
                                        blob_fee=blob_fee,
                                        transaction_count=tx_count,
                                        transaction_avg_size=tx_avg_size,
                                        transaction_avg_fee_per_size=tx_avg_fee_per_size)

                        new_transactions.append(tx)
                        updated_process.tx_content_reveal = tx.uuid
                    else:
                        pass
                else:
                    pass
        else:
            pass

    return {'update_process': updated_process,
            'new_transactions': new_transactions}


def p_submit_proof(params: AztecModelParams,
                   _2,
                   _3,
                   state: AztecModelState) -> SignalEvolveProcess:
    """
    Advances state of Processes that have submitted valid proofs.
    """
    process = state['current_process']
    updated_process: Optional[Process] = None
    new_transactions = list()

    if process is None:
        pass
    else:
        if process.phase == SelectionPhase.pending_rollup_proof:
            if process.duration_in_current_phase > params['phase_duration_rollup']:
                updated_process = copy(process)
                updated_process.phase = SelectionPhase.skipped  # TODO: confirm
                updated_process.duration_in_current_phase = 0
            else:
                if process.rollup_proof_is_commited:
                    updated_process = copy(process)
                    updated_process.phase = SelectionPhase.finalized
                    updated_process.duration_in_current_phase = 0

                    who = updated_process.leading_sequencer  # XXX
                    gas: Gas = params['gas_estimators'].content_reveal(state)
                    fee: Gwei = gas * state['gas_fee_l1']

                    if state['gas_fee_l1'] <= params['gas_threshold_for_tx']:
                        tx = RollupProof(who=who,
                                        when=state['time_l1'],
                                        uuid=uuid4(),
                                        gas=gas,
                                        fee=fee)

                        new_transactions.append(tx)
                        updated_process.tx_rollup_proof = tx.uuid
                    else:
                        pass
                else:
                    pass  # Nothing changes if no valid rollup
        else:
            pass

    return {'update_process': updated_process,
            'new_transactions': new_transactions}


def p_race_mode(params: AztecModelParams,
                _2,
                _3,
                state: AztecModelState) -> SignalEvolveProcess:
    process = state['current_process']
    updated_process: Optional[Process] = None

    if process is None:
        pass
    else:
        if process.phase == SelectionPhase.proof_race:
            if process.duration_in_current_phase > params['phase_duration_race']:
                updated_process = copy(process)
                updated_process.phase = SelectionPhase.skipped
                updated_process.duration_in_current_phase = 0
            else:
                if process.block_content_is_revealed & process.rollup_proof_is_commited:
                    updated_process = copy(process)
                    updated_process.phase = SelectionPhase.finalized
                    updated_process.duration_in_current_phase = 0
                    # NOTE: this logic may be changed in the future
                    # to take into account the racing dynamics
                else:
                    pass
        else:
            pass

    return {'update_process': updated_process}


def s_process(params: AztecModelParams,
              _2,
              _3,
              state: AztecModelState,
              signal: SignalEvolveProcess) -> VariableUpdate:
    """

    """
    updated_process = signal.get('update_process', state['current_process'])
    # Update only if there's an relevant signal.
    value = updated_process if updated_process is not None else state['current_process']
    return ('current_process', value)


def s_transactions_new_proposals(params: AztecModelParams,
                                 _2,
                                 _3,
                                 state: AztecModelState,
                                 _5) -> VariableUpdate:
    """
    Logic for submitting new proposals.
    """

    new_transactions = state['transactions'].copy()
    current_process: Process | None = state['current_process']
    new_proposals: dict[TxUUID, Proposal] = dict()
    if current_process is not None:
        if current_process.phase == SelectionPhase.pending_proposals:
            # HACK: all interacting users are potential proposers
            # XXX: an sequencer can propose only once
            proposers: set[AgentUUID] = {
                p.who for p in new_transactions.values()}
            potential_proposers: set[AgentUUID] = {u.uuid
                                                   for u in state['agents'].values()
                                                   if u.uuid not in proposers
                                                   and u.is_sequencer}

            for potential_proposer in potential_proposers:
                if bernoulli.rvs(params['proposal_probability_per_user_per_block']):

                    tx_uuid = uuid4()
                    gas: Gas = params['gas_estimators'].proposal(state)
                    fee: Gwei = gas * state['gas_fee_l1']
                    score = uniform.rvs()  # XXX: score is always uniform
                    size = params['tx_estimators'].proposal_average_size(state)
                    public_share = 0.5 # HACK

                    if state['gas_fee_l1'] <= params['gas_threshold_for_tx']:
                        new_proposal = Proposal(who=potential_proposer,
                                                when=state['time_l1'],
                                                uuid=tx_uuid,
                                                gas=gas,
                                                fee=fee,
                                                score=score,
                                                size=size,
                                                public_composition=public_share)

                        new_proposals[tx_uuid] = new_proposal
                    else:
                        pass
                else:
                    pass
        else:
            new_proposals = dict()
    else:
        new_proposals = dict()

    new_transactions = {**new_transactions, **new_proposals}

    return ('transactions', new_transactions)


def s_transactions(params: AztecModelParams,
                   _2,
                   _3,
                   state: AztecModelState,
                   signal: SignalEvolveProcess) -> VariableUpdate:
    """
    Logic for submitting new proposals.
    """

    new_tx_list: list[TransactionL1] = signal.get(
        'new_transactions', list())  # type: ignore

    new_tx_dict: dict[TxUUID, TransactionL1] = {
        tx.uuid: tx for tx in new_tx_list}

    new_transactions = {**state['transactions'].copy(), **new_tx_dict}

    return ('transactions', new_transactions)


def p_block_reward(params: AztecModelParams,
                   _2,
                   _3,
                   state: AztecModelState) -> SignalPayout:
    p: Process = state['current_process']  # type: ignore
    if p.phase == SelectionPhase.finalized:
        reward = params['reward_per_block']
    else:
        reward = 0
    return SignalPayout(block_reward=reward)


def p_fee_cashback(params: AztecModelParams,
                   _2,
                   _3,
                   state: AztecModelState) -> SignalPayout:
    p: Process = state['current_process']  # type: ignore
    if p.phase == SelectionPhase.finalized:

        txs: dict[TxUUID, AnyL1Transaction] = state['transactions']
        # L1 Fees
        total_fees = 0
        total_fees += txs[p.tx_winning_proposal].fee
        total_fees += txs[p.tx_content_reveal].fee
        total_fees += txs[p.tx_rollup_proof].fee
        total_fees += txs[p.tx_commitment_bond].fee

        # Blob Fees
        total_fees += txs[p.tx_content_reveal].blob_fee  # type: ignore
    else:
        total_fees = 0

    return SignalPayout(fee_cashback=total_fees)


def p_fee_from_users(params: AztecModelParams,
                     _2,
                     _3,
                     state: AztecModelState) -> SignalPayout:
    p: Process = state['current_process']  # type: ignore
    if p.phase == SelectionPhase.finalized:
        txs: dict[TxUUID, AnyL1Transaction] = state['transactions']
        total_fees = txs[p.tx_content_reveal].total_tx_fee  # type: ignore
    else:
        total_fees = 0

    return SignalPayout(fee_from_users=total_fees)


def s_agents_rewards(params: AztecModelParams,
                     _2,
                     _3,
                     state: AztecModelState,
                     signal: SignalPayout) -> VariableUpdate:
    """
    TODO
    """

    p: Process = state['current_process']  # type: ignore
    if p.phase == SelectionPhase.finalized:
        txs = state['transactions']
        total_rewards = signal.get(
            'fee_cashback', 0.0) + signal.get('block_reward', 0.0)
        agents: dict[AgentUUID, Agent] = state['agents'].copy()

        rewards_relay = total_rewards * params['rewards_to_relay']
        rewards_prover = total_rewards * params['rewards_to_provers']
        rewards_sequencer = total_rewards - (rewards_relay + rewards_prover)

        # TODO: How to select the winning sequencer when entering race mode?

        sequencer_uuid = p.leading_sequencer

        # TODO: add check for whatever the Process went through race-mode or not.
        if p.entered_race_mode:
            prover_uuid = txs[p.tx_commitment_bond].prover_uuid  # type: ignore
            # TODO: make sure that relays are included. For now, assume no relays
            relay_uuid = sequencer_uuid
        else:
            prover_uuid = sequencer_uuid

        # Disburse Rewards
        agents[sequencer_uuid].balance += rewards_sequencer
        agents[prover_uuid].balance += rewards_prover
        agents[relay_uuid].balance += rewards_relay
        return ('agents', agents)
    else:
        return ('agents', state['agents'])


def s_token_supply(params: AztecModelParams,
                   _2,
                   _3,
                   state: AztecModelState,
                   signal: SignalEvolveProcess) -> VariableUpdate:
    """
    Logic for submitting new proposals.
    """
    return ('token_supply', TokenSupply.from_state(state))
