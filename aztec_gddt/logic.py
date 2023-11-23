from copy import deepcopy, copy
from typing import Callable
from uuid import uuid4

from cadCAD_tools.types import Signal, VariableUpdate  # type: ignore

from aztec_gddt.helper import *
from aztec_gddt.types import *


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
    return ('block_time', state['time_l1'] + signal['delta_blocks'])


def s_delta_blocks(_1, _2, _3, _4, signal: Signal) -> VariableUpdate:
    """
    State update function for change in block number. 

    Args: 
        signal (Signal): The Signal, generated in p_evolve_time, of how many blocks to advance time. 

    Returns: 
        VariableUpdate
    """
    return ('delta_blocks', signal['delta_blocks'])

##############################
## Selection Phase          ##
##############################


#############################
## First step: determine   ##
## who drops in and drops  ##
## out of the interacting  ##
## users.                  ##
#############################


def p_update_interacting_users(params: AztecModelParams,
                               _2,
                               _3,
                               state: AztecModelState) -> Signal:
    """
    Args:
         params (AztecModelParams): The current parameters of the model.
         state (AztecModelState): The current state of the model.

    Returns:
         Signal: The new process to be considered in the system. 

    """
    # TODO: logic for updating interacting users

    return {"new_interacting_users": None}


def p_init_process(params: AztecModelParams,
                   _2,
                   _3,
                   state: AztecModelState) -> Signal:
    """
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
                              process_aborted=False)
    else:
        new_process = None

    return {'update_process': new_process}

#######################################
##         Selection Phase           ##
#######################################


#######################################
## Policy and state update functions ##
## for selection.                    ##
#######################################

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
    do_select_process = process.phase == SelectionPhase.pending_proposals
    do_select_process &= process.duration_in_current_phase >= params['proposal_duration']

    if do_select_process:
        # TODO: filter out invalid proposals
        # J: Which invalid proposals are we expecting here? Anything "spam/invalid" would just be ignored, not sure we need to sim that, unless for blockspace
        proposals = state['proposals'].get(process.uuid, [])
        if len(proposals) > 0:
            # TODO: check if true
            number_uncles = min(len(proposals) - 1, params['uncle_count'])

            ranked_proposals = sorted(proposals,
                                        key=lambda p: p.score,
                                        reverse=True)

            winner_proposal = ranked_proposals[0]
            uncle_proposals = ranked_proposals[1:number_uncles+1]

            updated_process = copy(state['current_process'])
            updated_process.phase = SelectionPhase.pending_reveal
            updated_process.leading_sequencer = winner_proposal.uuid
            updated_process.uncle_sequencers = [p.uuid for p in uncle_proposals]
        else:
            updated_process = None
    else:
        updated_process = None
        

    return {'update_process': updated_process}


def p_reveal_block_content(params: AztecModelParams,
                           _2,
                           _3,
                           state: AztecModelState) -> Signal:
    """
    Advances state of Processes that have revealed block content.
    """
    # TODO: How to check if block content was revealed for process? (Add this as a field for the class?)
    # Note: Advances state of Process in reveal phase that have revealed block content.

    current_processes = state['processes']
    updated_processes: dict[ProcessUUID, Process] = {}

    ##################################################################
    ## For every process in the reveal content phase, run           ##
    ## a Bernoulli trial and determine whether this proposal        ##
    ## reveals block content or now.                                ##
    ###################################################################

    pending_reveal_processes = select_processes_by_state(current_processes,
                                                         SelectionPhase.pending_reveal)

    for process in pending_reveal_processes:     # For each process on  `pending_reveal` phase
        updated_process = copy(process)

        # If the process has blown the phase duration
        if has_blown_phase_duration(process):
            # Transition process to skipped phase.
            updated_process.current_phase = SelectionPhase.finalized_without_rewards
        else:
            if process.block_content_is_revealed:  # If finalized transaction was submitted.
                updated_process.current_phase = SelectionPhase.pending_rollup_proof
            else:  # If block content not revealed
                pass  # Nothing happens

        # Assign to place in dictionary
        updated_processes[process.uuid] = updated_process

    return {'update_processes': updated_processes}


def p_submit_block_proofs(params: AztecModelParams,
                          _2,
                          _3,
                          state: AztecModelState) -> Signal:
    """
    Advances state of Processes that have submitted valid proofs.
    """

    current_processes: list[Process] = state['processes']
    updated_processes: dict[ProcessUUID, Process] = {}

    pending_rollup_proof_processes = select_processes_by_state(current_processes,
                                                               SelectionPhase.pending_rollup_proof)

    for process in pending_rollup_proof_processes:
        updated_process = copy(process)

        if has_blown_phase_duration(process):
            process.current_phase = SelectionPhase.reorg
            updated_processes[process.uuid] = updated_process
        else:
            if process.proofs_are_public:
                updated_process.current_phase = SelectionPhase.pending_finalization
                updated_processes[process.uuid] = updated_process
            else:  # If no valid rollup
                pass  # Nothing changes

        # Assign to place in dictionary
        updated_processes[process.uuid] = updated_process

    return {'update_processes': updated_processes}


def p_finalize_block(params: AztecModelParams,
                     _2,
                     _3,
                     state: AztecModelState) -> Signal:
    """

    """
    updated_processes: dict = {}
    # TODO
    # For every process on the `pending_finalization` phase, do:
    # - If the process has blown the phase duration,
    # then transition to finalized w/o rewards.
    # - Else, check if the finalize transaction was submitted.
    # If yes, advance to the next phase. Else, nothing happens
    return {'update_processes': updated_processes}


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


def s_processes(params: AztecModelParams,
                _2,
                _3,
                state: AztecModelState,
                signal: Signal) -> VariableUpdate:
    """
    NOTE: this SUF is depreciated
    """
    processes = deepcopy(state['processes'])
    processes_to_update: dict[ProcessUUID,
                              Process] = signal.get('updated_processes', {})
    for process_uuid, updated_process in processes_to_update.items():
        pass  # TODO

    new_process = signal.get('new_process', None)
    if new_process != None:
        processes.append(new_process)

    return ('processes', processes)

def s_process(params: AztecModelParams,
                _2,
                _3,
                state: AztecModelState,
                signal: Signal) -> VariableUpdate:
    """
    
    """
    return ('process', signal.get('update_process', state['current_process']))



###########################
## Overall steps         ##
###########################

###########################
## Phases                ##
## A new process starts  ##
## Question:             ##
## When should Sequencers ##
## be updated? At the beginning ##
## of a new process?            ##
##################################

# First phase of new process:
# which Sequencers drop in or drop out?
# Decision: Danilo will make.
