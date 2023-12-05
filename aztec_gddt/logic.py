from copy import deepcopy, copy
from typing import Callable
from uuid import uuid4

from cadCAD_tools.types import Signal, VariableUpdate  # type: ignore

from aztec_gddt.helper import *
from aztec_gddt.types import *

from scipy.stats import bernoulli, uniform, norm # type: ignore

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

def p_evolve_time(params: AztecModelParams, _2, _3, _4) -> Signal:
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
                 signal: Signal) -> VariableUpdate:
    """State update function advancing block time.  

    Args:
         params (AztecModelParams): The current parameters of the model.
         state (AztecModelState): The current state of the model.
         signal (Signal): The Signal, generated in p_evolve_time, of how many blocks to advance time. 

    Returns:
        VariableUpdate:
            A two-element tuple that all state update functions must return.
    """
    return ('time_l1', state['time_l1'] + signal['delta_blocks'])


def s_delta_blocks(_1, _2, _3, _4, signal: Signal) -> VariableUpdate:
    """
    State update function for change in block number. 

    Args: 
        signal (Signal): The Signal, generated in p_evolve_time, of how many blocks to advance time. 

    Returns: 
        VariableUpdate
    """
    return ('delta_blocks', signal['delta_blocks'])


def s_current_process_time(_1, _2, _3, state: AztecModelState, signal: Signal) -> VariableUpdate:
    """
    State update function for change in block number. 

    Args: 
        signal (Signal): The Signal, generated in p_evolve_time, of how many blocks to advance time. 

    Returns: 
        VariableUpdate
    """
    updated_process = copy(state['current_process'])
    if updated_process is not None:
        updated_process.duration_in_current_phase += signal['delta_blocks']
    else:
        pass
        
    return ('current_process', updated_process)

##############################
## Pre-Phase                ##
##############################

##############################
## Pre-Phase                ##
##  Completed               ##
##############################

##############################
## Pre-Phase                ##
## In Progress              ##
##############################

##############################
## Pre-Phase                ##
## Not Started              ##
##############################

##############################
## Block Proposal Phase     ##
##############################

##############################
## Block Proposal Phase     ##
## Completed                ##
##############################

##############################
## Block Proposal Phase     ##
## In Progress              ##
##############################

##############################
## Block Proposal Phase     ##
## Not Started              ##
##############################

##############################
## Block Reveal Phase       ##
##############################

##############################
## Block Reveal Phase       ##
## Completed                ##
##############################

##############################
## Block Reveal Phase       ##
## In Progress              ##
##############################

##############################
## Block Reveal Phase       ##
## Not Started              ##
##############################

##############################
## Prover Commitment Phase  ##
##############################

##############################
## Prover Commitment Phase  ##
## Completed                ##
##############################

##############################
## Prover Commitment Phase  ##
## In Progress              ##
##############################

##############################
## Prover Commitment Phase  ##
## Not Started              ##
##############################

##############################
## Proving Phase            ##
##############################

##############################
## Proving Phase            ##
## Completed                ##
##############################

##############################
## Proving Phase            ##
## In Progress              ##
##############################

##############################
## Proving Phase            ##
## Not Started              ##
##############################

##############################
## Finalization Phase       ##
##############################

##############################
## Finalization Phase       ##
## Completed                ##
##############################

##############################
## Finalization Phase       ##
## In Progress              ##
##############################

##############################
## Finalization Phase       ##
## Not Started              ##
##############################



def p_update_interacting_users(params: AztecModelParams,
                               _2,
                               _3,
                               state: AztecModelState) -> Signal:
    """
    Used to determine who drops in and out of interacting users.

    Args:
         params (AztecModelParams): The current parameters of the model.
         state (AztecModelState): The current state of the model.

    Returns:
         Signal: The new process to be considered in the system. 

    """
    # TODO: logic for updating interacting users
    # TODO: Logic: staked_amount > min_stake 
    # staked_amount is updated at end of process due to rewards and slashing
    # right now we only have sequencers -> with the introduction of commitment bond we might introduce second class 
    # commitment bond could be put up by lead sequencer, or by anyone else (e.g. 3rd party marketplace)

    return {"new_interacting_users": None}

def p_init_proposals(params: AztecModelParams,
                   _2,
                   _3,
                   state: AztecModelState) -> Signal:
    """
    Initializes a certain number of proposals. 

    Args:
         params (AztecModelParams): The current parameters of the model.
         state (AztecModelState): The current state of the model.

    Returns:
         Signal: The new process to be considered in the system. 

    """
    
    threshold = params["min_stake"]
    eligible_users = list(filter(lambda x: x.staked_amount > threshold,
                                 state["interacting_users"]))

    for user in eligible_users:
        user.new_score() #Update each user's score parameter individually.

    sorted_eligible_users = sorted(eligible_users,
                                   key = lambda x: x.score) #Sort users based on score.

    num_proposals_to_create = params["num_proposals"] #Determine how many proposals to create.
    new_proposals = [user.create_proposal(state) for 
                     user in sorted_eligible_users[0:num_proposals_to_create]] #Create new proposals.

    return {"proposals_created": new_proposals}



def p_init_process(params: AztecModelParams,
                   _2,
                   _3,
                   state: AztecModelState) -> Signal:
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
        do_init_process = state['current_process'].phase == SelectionPhase.finalized
        do_init_process |= state['current_process'].phase == SelectionPhase.finalized_without_rewards
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
                              finalization_tx_is_submitted=False,
                              process_aborted=False)
    else:
        new_process = None

    return {'update_process': new_process}

def p_select_proposal(params: AztecModelParams,
                      _2,
                      _3,
                      state: AztecModelState) -> Signal:
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
                proposals = state['proposals']
                if len(proposals) > 0:
                    # TODO: check if true
                    number_uncles = min(len(proposals) - 1, params['uncle_count'])

                    ranked_proposals = sorted(proposals,
                                                key=lambda p: p.score,
                                                reverse=True)

                    winner_proposal = ranked_proposals[0]
                    if len(ranked_proposals) > 1:
                        uncle_proposals = ranked_proposals[1:number_uncles+1]
                    else:
                        uncle_proposals = []

                    updated_process = copy(process)
                    updated_process.phase = SelectionPhase.pending_reveal
                    updated_process.duration_in_current_phase = 0
                    updated_process.leading_sequencer = winner_proposal.uuid
                    updated_process.uncle_sequencers = [p.uuid for p in uncle_proposals]
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
                           state: AztecModelState) -> Signal:
    process = state['current_process']
    updated_process: Optional[Process] = None

    if process is None:
        pass
    else:
        if process.phase == SelectionPhase.pending_commit_bond:
            if process.duration_in_current_phase > params['phase_duration_commit_bond']:
                updated_process = copy(process)
                updated_process.phase = SelectionPhase.proof_race
                updated_process.duration_in_current_phase = 0
            else:
                if process.commit_bond_is_put_down:
                    updated_process = copy(process)
                    updated_process.phase = SelectionPhase.pending_reveal
                    updated_process.duration_in_current_phase = 0
                else:
                    pass
        else:
            pass

    return {'update_process': updated_process}


def p_reveal_content(params: AztecModelParams,
                     _2,
                     _3,
                     state: AztecModelState) -> Signal:
    """
    Advances state of Processes that have revealed block content.
    """
    # TODO: How to check if block content was revealed for process? (Add this as a field for the class?)


                         
    # Note: Advances state of Process in reveal phase that have revealed block content.
    process = state['current_process']
    updated_process: Optional[Process] = None

    
    if process is None:
        pass
    else:
        if process.phase == SelectionPhase.pending_reveal:
            # If the process has blown the phase duration
            if process.duration_in_current_phase > params['phase_duration_reveal']:
                updated_process = copy(process)
                updated_process.phase = SelectionPhase.proof_race
                updated_process.duration_in_current_phase = 0
                # TODO: To allow for fixed phase time, we might just add another check here - if duration > params and if content is not revealed -> proof_race
            else:
                if process.block_content_is_revealed:  # If block content was revealed. 
                    updated_process = copy(process)
                    updated_process.phase = SelectionPhase.pending_rollup_proof
                    updated_process.duration_in_current_phase = 0
                else:  # If block content not revealed
                    probability_to_use = params['block_content_reveal_probability']
                    content_will_be_revealed = bernoulli_trial(probability = probability_to_use)
                    if content_will_be_revealed:
                        process.block_content_is_revealed = True
                        # XXX: How does time update here? 
                    else: 
                        pass
        else:
            pass

    return {'update_process': updated_process}
    

def p_submit_proof(params: AztecModelParams,
                          _2,
                          _3,
                          state: AztecModelState) -> Signal:
    """
    Advances state of Processes that have submitted valid proofs.
    """
    process = state['current_process']
    updated_process: Optional[Process] = None

    if process is None:
        pass
    else:
        if process.phase == SelectionPhase.pending_rollup_proof:
            if process.duration_in_current_phase > params['phase_duration_rollup']:
                updated_process = copy(process)
                updated_process.phase = SelectionPhase.skipped # TODO: confirm
                updated_process.duration_in_current_phase = 0
            else:
                if process.rollup_proof_is_commited:
                    updated_process = copy(process)
                    updated_process.phase = SelectionPhase.pending_finalization
                    updated_process.duration_in_current_phase = 0
                else: 
                    pass  # Nothing changes if no valid rollup
        else:
            pass

    return {'update_process': updated_process}


def p_finalize_block(params: AztecModelParams,
                     _2,
                     _3,
                     state: AztecModelState) -> Signal:
    """

    """
    # TODO
    # For every process on the `pending_finalization` phase, do:
    # - If the process has blown the phase duration,
    # then transition to finalized w/o rewards.
    # - Else, check if the finalize transaction was submitted.
    # If yes, advance to the next phase. Else, nothing happens

    process = state['current_process']
    updated_process: Optional[Process] = None

    if process is None:
        pass
    else:
        if process.phase == SelectionPhase.pending_finalization:
            if process.duration_in_current_phase > params['phase_duration_finalize']:
                updated_process = copy(process)
                updated_process.phase = SelectionPhase.finalized_without_rewards
                updated_process.duration_in_current_phase = 0
            else:
                if process.finalization_tx_is_submitted:
                    updated_process = copy(process)
                    updated_process.phase = SelectionPhase.finalized
                    updated_process.duration_in_current_phase = 0
                    # TODO: may add reward logic?
                else:
                    pass
        else:
            pass

    return {'update_process': updated_process}


def p_race_mode(params: AztecModelParams,
                     _2,
                     _3,
                     state: AztecModelState) -> Signal:
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
                    updated_process.phase = SelectionPhase.pending_finalization
                    updated_process.duration_in_current_phase = 0
                    # NOTE: this logic may be changed in the future
                    # to take into account the racing dynamics
                else:
                    pass
        else:
            pass

    return {'update_process': updated_process}


def s_sequencer(params: AztecModelParams,
                _2,
                _3,
                state: AztecModelState,
                signal: Signal) -> VariableUpdate:
    """

    """
    # TODO: Logic for updating the sequencer
    # Signal comes from p_select_sequencer

    return ('sequencer', None)


# def s_processes(params: AztecModelParams,
#                 _2,
#                 _3,
#                 state: AztecModelState,
#                 signal: Signal) -> VariableUpdate:
#     """
#     NOTE: this SUF is depreciated
#     """
#     processes = deepcopy(state['processes'])
#     processes_to_update: dict[ProcessUUID,
#                               Process] = signal.get('updated_processes', {})
#     for process_uuid, updated_process in processes_to_update.items():
#         pass  # TODO

#     new_process = signal.get('new_process', None)
#     if new_process != None:
#         processes.append(new_process)
#     return ('processes', processes)

def s_process(params: AztecModelParams,
                _2,
                _3,
                state: AztecModelState,
                signal: Signal) -> VariableUpdate:
    """
    
    """
    updated_process = signal.get('update_process', state['current_process'])
    # Update only if there's an relevant signal.
    value = updated_process if updated_process is not None else state['current_process']
    return ('current_process', value)



def s_proposals(params: AztecModelParams,
                _2,
                _3,
                state: AztecModelState,
                signal: Signal) -> VariableUpdate:
    """
    TODO
    """

    current_process = state['current_process']
    if current_process is not None:
        if current_process.phase == SelectionPhase.pending_proposals:
            # HACK: all interacting users are potential proposers
            # XXX: an sequencer can propose only once
            proposals = copy(state['proposals'])
            proposers = {p.proposer_uuid for p in proposals}
            potential_proposers = {u.uuid 
                                   for u in state['interacting_users']
                                   if u.uuid not in proposers}

            for potential_proposer in potential_proposers:
                if bernoulli.rvs(params['proposal_probability_per_user_per_block']):
                    
                    score = uniform.rvs(0, 1)
                    submission_time = state['time_l1']

                    # TODO parametrize & use more sane assumptions
                    gas = round(max(norm.rvs(50, 30), 1))
                    size = round(max(norm.rvs(10_000, 5_000), 100))

                    new_proposal = Proposal(uuid4(),
                                             potential_proposer, 
                                             score,
                                             submission_time,
                                             gas,
                                             size)
                    proposals.append(new_proposal)
                else:
                    pass
        else:
            proposals = []
    else:
        proposals = []

    return ('proposals', proposals)


def s_interacting_users(params: AztecModelParams,
                _2,
                _3,
                state: AztecModelState,
                signal: Signal) -> VariableUpdate:
    """
    TODO
    """
    return ('interacting_users', None)

