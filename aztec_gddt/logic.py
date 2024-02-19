from copy import deepcopy, copy
from typing import Callable
from uuid import uuid4

from random import choice

from cadCAD_tools.types import VariableUpdate  # type: ignore

from aztec_gddt.helper import *
from aztec_gddt.types import *

from scipy.stats import bernoulli, uniform, norm  # type: ignore
from random import random

def generic_policy(_1, _2, _3, _4) -> dict:
    """
    Function to generate pass through policy

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
    """
    Creates replacing function for state update from string

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

def p_evolve_time(params: AztecModelParams, _2, _3, state: AztecModelState) -> SignalTime:
    """
    Policy function giving the change in number of blocks. 

    Args:
         params (AztecModelParams): The current parameters of the model.

    Returns:
        Signal: 
            a dictionary of variables that can be used in an update
    """
    return {'delta_l1_blocks': params['timestep_in_blocks']}



def p_evolve_time_dynamical(params: AztecModelParams, _2, _3, state: AztecModelState) -> SignalTime:
    """
    Policy function giving the change in number of blocks. 

    Args:
         params (AztecModelParams): The current parameters of the model.

    Returns:
        Signal: 
            a dictionary of variables that can be used in an update
    """
    return {'delta_l1_blocks': state['advance_l1_blocks']}


def s_block_time(params: AztecModelParams, _2, _3,
                 state: AztecModelState,
                 signal: SignalTime) -> VariableUpdate:
    """
    State update function advancing block time.  

    Args:
         params (AztecModelParams): The current parameters of the model.
         state (AztecModelState): The current state of the model.
         signal (Signal): The Signal, generated in p_evolve_time, of how many blocks to advance time. 

    Returns:
        VariableUpdate:
            A two-element tuple that all state update functions must return.
    """
    return ('time_l1', state['time_l1'] + signal['delta_l1_blocks'])  # type: ignore



def s_delta_l1_blocks(_1, _2, _3, _4, signal: SignalTime) -> VariableUpdate:
    """
    State update function for change in block number. 

    Args: 
        signal (Signal): The Signal, generated in p_evolve_time, of how many blocks to advance time. 

    Returns: 
        VariableUpdate
    """
    return ('delta_l1_blocks', signal.get('delta_l1_blocks', 0))

def s_reset_advance(params: AztecModelParams, _2, _3,
                 state: AztecModelState,
                 signal: SignalTime) -> VariableUpdate:
    """
    State update function advancing block time.  

    Args:
         params (AztecModelParams): The current parameters of the model.
         state (AztecModelState): The current state of the model.
         signal (Signal): The Signal, generated in p_evolve_time, of how many blocks to advance time. 

    Returns:
        VariableUpdate:
            A two-element tuple that all state update functions must return.
    """
    return ('advance_l1_blocks', 0)  # type: ignore


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
        updated_process.duration_in_current_phase += signal.get('delta_l1_blocks', 0)
    else:
        pass

    return ('current_process', updated_process)


def s_current_process_time_dynamical(_1,
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
    delta_l1_blocks = signal.get('delta_l1_blocks', 0)
    updated_process: Process | None = copy(state['current_process'])
    if updated_process is not None:
        if delta_l1_blocks > 0:
            updated_process.current_phase_init_time += delta_l1_blocks

    return ('current_process', updated_process)


def s_gas_fee_l1(params: AztecModelParams,
                 _2,
                 _3,
                 state: AztecModelState,
                 signal: SignalEvolveProcess) -> VariableUpdate:
    """
    State update function for change in gas fee.
    """
    return ('gas_fee_l1', state['gas_fee_l1'])


def s_gas_fee_blob(params: AztecModelParams,
                   _2,
                   _3,
                   state: AztecModelState,
                   signal: SignalEvolveProcess) -> VariableUpdate:
    """
    State update function for change in blob gas fee.
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

    max_phase_duration = params['phase_duration_proposal'].max

    if process is None:
        pass
    else:
        if process.phase == SelectionPhase.pending_proposals:
            remaining_time = max_phase_duration - process.duration_in_current_phase
            if remaining_time < 0:
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

                    # BUG: do this for all phase evolving logic.
                    # BUG: make sure that this is compatible when the time evolution is dynamical, eg, 1 ts = many blocks
                    updated_process.current_phase_init_time = state['time_l1'] 

                    updated_process.phase = SelectionPhase.pending_commit_bond
                    updated_process.duration_in_current_phase = 0
                    updated_process.leading_sequencer = winner_proposal.who
                    updated_process.uncle_sequencers = [
                        p.who for p in uncle_proposals]
                    updated_process.tx_winning_proposal = winner_proposal.uuid
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
                  history: list[list[AztecModelState]],
                  state: AztecModelState) -> SignalEvolveProcess:
    process: Process | None = state['current_process']
    updated_process: Optional[Process] = None
    new_transactions = list()
    advance_blocks = 0
    transfers: list[Transfer] = []

    max_phase_duration = params["phase_duration_commit_bond"].max

    bond_amount = params['commit_bond_amount']

    if process is None:
        pass
    else:
        if process.phase == SelectionPhase.pending_commit_bond:
            remaining_time = max_phase_duration - process.duration_in_current_phase
            if remaining_time < 0:
                # Move to Proof Race mode if duration is expired
                updated_process = copy(process)
                updated_process.phase = SelectionPhase.proof_race
                updated_process.entered_race_mode = True
                updated_process.duration_in_current_phase = 0

                # and slash leading sequencer
                slashed_amount = params['slash_params'].failure_to_commit_bond
                transfers.append(Transfer(source=updated_process.leading_sequencer,
                                    destination='burnt',
                                    amount=slashed_amount,
                                    kind=TransferKind.slash))
            else:
                # XXX
                expected_rewards = state['cumm_block_rewards'] - history[-1][0]['cumm_block_rewards']
                expected_costs = state['cumm_fee_cashback'] - history[-1][0]['cumm_fee_cashback']
                payoff_reveal = expected_rewards - expected_costs

                if payoff_reveal >= 0:
                    # If duration is not expired, do  a trial to see if bond is commited
                    if bernoulli_trial(probability=params['commit_bond_reveal_probability']) is True and (state['gas_fee_l1'] <= params['gas_threshold_for_tx']):
                        updated_process = copy(process)
                        advance_blocks = remaining_time
                        updated_process.phase = SelectionPhase.pending_reveal
                        updated_process.duration_in_current_phase = 0

                        gas: Gas = params['gas_estimators'].commitment_bond(state)
                        fee = gas * state['gas_fee_l1']
                        proposal_uuid = updated_process.tx_winning_proposal


                        if bernoulli_trial(params['proving_marketplace_usage_probability']) is True:
                            provers: list[AgentUUID] = [
                                                        a_id 
                                                        for (a_id, a) 
                                                        in state['agents'].items() 
                                                        if a.is_prover and a.balance >= bond_amount]
                            # XXX: relays are going to be uniformly sampled
                            prover: AgentUUID = choice(provers)
         
                        else:
                            prover = updated_process.leading_sequencer

                        tx = CommitmentBond(who=prover,
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
                        # Force Race Mode by doing nothing
                        pass
                else:
                    # else, nothing happens
                    pass
        else:
            pass

    return {'update_process': updated_process,
            'new_transactions': new_transactions,
            'advance_l1_blocks': advance_blocks,
            'transfers': transfers}


def p_reveal_content(params: AztecModelParams,
                     _2,
                     history: list[list[AztecModelState]],
                     state: AztecModelState) -> SignalEvolveProcess:
    """
    Advances state of Processes that have revealed block content.
    TODO: check if race mode is taken into consideration. We may want to decouple 
    user actions from the evolving logic.
    """

    # Note: Advances state of Process in reveal phase that have revealed block content.
    process = state['current_process']
    updated_process: Optional[Process] = None
    advance_blocks = 0
    new_transactions = list()
    transfers: list[Transfer] = []
    max_phase_duration = params['phase_duration_reveal'].max

    if process is None:
        pass
    else:
        if process.phase == SelectionPhase.pending_reveal:
            # If the process has blown the phase duration
            remaining_time = max_phase_duration - process.duration_in_current_phase
            if remaining_time < 0:
                updated_process = copy(process)
                updated_process.phase = SelectionPhase.proof_race
                updated_process.entered_race_mode = True
                updated_process.duration_in_current_phase = 0


                # and slash leading sequencer
                slashed_amount = params['slash_params'].failure_to_reveal_block
                transfers.append(Transfer(source=updated_process.leading_sequencer,
                                    destination='burnt',
                                    amount=slashed_amount,
                                    kind=TransferKind.slash))
            else:
                # XXX
                expected_rewards = state['cumm_block_rewards'] - history[-1][0]['cumm_block_rewards']
                expected_costs = state['cumm_fee_cashback'] - history[-1][0]['cumm_fee_cashback']
                payoff_reveal = expected_rewards - expected_costs

                if payoff_reveal >= 0:
                    if bernoulli_trial(probability=params['block_content_reveal_probability']) is True and (state['gas_fee_l1'] <= params['gas_threshold_for_tx']) and (state['gas_fee_blob'] <= params['blob_gas_threshold_for_tx']):
                        updated_process = copy(process)
                        advance_blocks = remaining_time
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
                        pass # Force race mode by doing nothing
                else:
                    pass
        else:
            pass

    return {'update_process': updated_process,
            'new_transactions': new_transactions,
            'advance_l1_blocks': advance_blocks}


def p_submit_proof(params: AztecModelParams,
                   _2,
                   _3,
                   state: AztecModelState) -> SignalEvolveProcess:
    """
    Advances state of Processes that have  submitted rollup proofs.
    """
    process = state['current_process']
    updated_process: Optional[Process] = None
    new_transactions = list()
    advance_blocks = 0
    transfers: list[Transfer] = []

    max_phase_duration = params['phase_duration_rollup'].max

    if process is None:
        pass
    else:
        if process.phase == SelectionPhase.pending_rollup_proof:
            remaining_time = max_phase_duration - process.duration_in_current_phase
            if remaining_time < 0:
                updated_process = copy(process)
                updated_process.phase = SelectionPhase.skipped  # TODO: confirm
                updated_process.duration_in_current_phase = 0
                
                # Determine who should be slashed, and how much. 
                transactions = state['transactions']
                commit_bond_id = updated_process.tx_commitment_bond
                commit_bond = transactions.get(commit_bond_id)
                who_to_slash = commit_bond.prover_uuid
                how_much_to_slash = commit_bond.bond_amount

                # Create a slash_transfer and add it to the transfers. 
                slash_transfer = Transfer(source = who_to_slash,
                                          destination = 'burnt',
                                          amount = how_much_to_slash,
                                          kind = TransferKind.slash)

                transfers.append(slash_transfer)


            else:
                if bernoulli_trial(probability=params['rollup_proof_reveal_probability']) and (state['gas_fee_l1'] <= params['gas_threshold_for_tx']):
                    updated_process = copy(process)
                    advance_blocks = remaining_time
                    updated_process.phase = SelectionPhase.finalized
                    updated_process.duration_in_current_phase = 0

                    who = updated_process.leading_sequencer  # XXX
                    gas: Gas = params['gas_estimators'].content_reveal(state)
                    fee: Gwei = gas * state['gas_fee_l1']

                    tx = RollupProof(who=who,
                                    when=state['time_l1'],
                                    uuid=uuid4(),
                                    gas=gas,
                                    fee=fee)

                    new_transactions.append(tx)
                    updated_process.tx_rollup_proof = tx.uuid

                else:
                    pass  # Nothing changes if no valid rollup
        else:
            pass

    return {'update_process': updated_process,
            'new_transactions': new_transactions,
            'advance_l1_blocks': advance_blocks,
            'transfers': transfers}


def p_race_mode(params: AztecModelParams,
                _2,
                _3,
                state: AztecModelState) -> SignalEvolveProcess:
    """
    Logic for race mode. 
    """
    process = state['current_process']
    updated_process: Optional[Process] = None
    new_transactions: list[TransactionL1] = list()

    if process is None:
        pass
    else:
        if process.phase == SelectionPhase.proof_race:
            if process.duration_in_current_phase > params['phase_duration_race']:
                updated_process = copy(process)
                updated_process.phase = SelectionPhase.skipped
                updated_process.duration_in_current_phase = 0
            else:
                # XXX there is a hard-coded L1 Builder agent
                # who immediatly ends the race mode.
                who = 'l1-builder'
                gas: Gas = params['gas_estimators'].content_reveal(state)
                fee: Gwei = gas * state['gas_fee_l1']
                blob_gas: BlobGas = params['gas_estimators'].content_reveal_blob(
                    state)
                blob_fee: Gwei = blob_gas * state['gas_fee_blob']

                tx_count = params['tx_estimators'].transaction_count(state)
                tx_avg_size = int(state['transactions'][process.tx_winning_proposal].size / tx_count) # type: ignore
                tx_avg_fee_per_size = params['tx_estimators'].transaction_average_fee_per_size(
                    state)
                
                tx_1 = RollupProof(who=who,
                when=state['time_l1'],
                uuid=uuid4(),
                gas=gas,
                fee=fee)

                tx_2 = ContentReveal(who=who,
                                when=state['time_l1'],
                                uuid=uuid4(),
                                gas=gas,
                                fee=fee,
                                blob_gas=blob_gas,
                                blob_fee=blob_fee,
                                transaction_count=tx_count,
                                transaction_avg_size=tx_avg_size,
                                transaction_avg_fee_per_size=tx_avg_fee_per_size)

                new_transactions.append(tx_1)
                new_transactions.append(tx_2)

                updated_process = copy(process)
                updated_process.tx_rollup_proof = tx_1.uuid
                updated_process.block_content_is_revealed = True
                updated_process.tx_content_reveal = tx_2.uuid
                updated_process.phase = SelectionPhase.finalized
                updated_process.duration_in_current_phase = 0
        else:
            pass

    return {'update_process': updated_process,
            'new_transactions': new_transactions}


def s_process(params: AztecModelParams,
              _2,
              _3,
              state: AztecModelState,
              signal: SignalEvolveProcess) -> VariableUpdate:
    """
    Logic for updating process. 
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
                                                   and u.is_sequencer
                                                   and u.staked_amount >= params['slash_params'].minimum_stake}

            for potential_proposer in potential_proposers:
                if bernoulli.rvs(params['proposal_probability_per_user_per_block']):

                    tx_uuid = uuid4()
                    gas: Gas = params['gas_estimators'].proposal(state)
                    fee: Gwei = gas * state['gas_fee_l1']
                    score = uniform.rvs()  # XXX: score is always uniform
                    size = params['tx_estimators'].proposal_average_size(state)
                    public_share = 0.5 # HACK

                    if (state['gas_fee_l1'] <= params['gas_threshold_for_tx']):
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


def s_advance_blocks(_1, _2, _3, state, signal: SignalEvolveProcess) -> VariableUpdate:
    return ('advance_l1_blocks', signal.get('advance_l1_blocks', 0))


def s_transactions(params: AztecModelParams,
                   _2,
                   _3,
                   state: AztecModelState,
                   signal: SignalEvolveProcess) -> VariableUpdate:
    """
    Logic for new transactions.
    """

    new_tx_list: list[TransactionL1] = signal.get(
        'new_transactions', list())  # type: ignore

    new_tx_dict: dict[TxUUID, TransactionL1] = {
        tx.uuid: tx for tx in new_tx_list}

    new_transactions = {**state['transactions'].copy(), **new_tx_dict}

    return ('transactions', new_transactions)


def s_agent_transfer(params: AztecModelParams,
                     _2,
                     _3,
                     state: AztecModelState,
                     signal: SignalEvolveProcess) -> VariableUpdate:
    """
    Logic for transferring tokens between agents and burn sink.
    """
    updated_agents = state['agents'].copy()
    transfers: Sequence[Transfer] = signal.get('transfers', []) # type: ignore

    for transfer in transfers:
        if transfer.kind == TransferKind.conventional:
            updated_agents[transfer.source].balance -= transfer.amount
            updated_agents[transfer.destination].balance += transfer.amount
        elif transfer.kind == TransferKind.slash:
            updated_agents[transfer.source].staked_amount -= transfer.amount
            updated_agents[transfer.destination].balance += transfer.amount

    return ('agents', updated_agents)
    

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
        total_fees: float = 0
        total_fees += txs[p.tx_winning_proposal].fee
        total_fees += txs[p.tx_content_reveal].fee
        total_fees += txs[p.tx_rollup_proof].fee
        total_fees += txs[p.tx_commitment_bond].fee if p.tx_commitment_bond is not None else 0

        # Blob Fees
        total_fees += txs[p.tx_content_reveal].blob_fee  # type: ignore

        total_fees *= params['gwei_to_tokens']
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

        sequencer_uuid = state['transactions'][p.tx_rollup_proof].who

        if not p.entered_race_mode:
            prover_uuid = txs[p.tx_commitment_bond].prover_uuid  # type: ignore
            relays = [a_id for (a_id, a) in state['agents'].items() if a.is_relay]
            relay_uuid: AgentUUID = choice(relays)
        else:
            prover_uuid = sequencer_uuid
            relay_uuid = sequencer_uuid

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
    Logic for token supply.
    """
    return ('token_supply', TokenSupply.from_state(state))
