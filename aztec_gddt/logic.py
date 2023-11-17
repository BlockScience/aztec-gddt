from cadCAD_tools.types import Signal, VariableUpdate # type: ignore
from aztec_gddt.helper import *
from aztec_gddt.types import *
from typing import Callable
from uuid import uuid4
from copy import deepcopy, copy

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




def p_evolve_time(params: AztecModelParams, _2, _3, _4) -> Signal:
    return {'delta_blocks': params['timestep_in_blocks']}

def s_block_time(params: AztecModelParams, _2, _3,
                  state: AztecModelState,
                  signal: Signal) -> VariableUpdate:
    return ('block_time', state['time_l1'] + signal['delta_blocks'])

def s_delta_blocks(_1, _2, _3, _4, signal: Signal) -> VariableUpdate:
    return ('delta_blocks', signal['delta_blocks'])


def p_init_process(params: AztecModelParams,
                   _2,
                   _3,
                   state: AztecModelState) -> Signal:
    """
    
    """
    last_process = last_active_process(state['processes'])
    do_init_process = last_process.current_phase == SelectionPhase.pending_rollup_proof
    do_init_process |= last_process.current_phase == SelectionPhase.skipped
    do_init_process |= last_process.current_phase == SelectionPhase.reorg

    if do_init_process:
        new_process = Process(uuid=uuid4(),
                                       current_phase=SelectionPhase.pending_proposals,
                                       leading_sequencer=None,
                                       uncle_sequencers=None,
                                       current_phase_init_time=state['time_l1'],
                                       duration_in_current_phase=0,
                                       proofs_are_public=False,
                                       process_aborted=False)
    else:
        new_process = None

    return {'new_process': new_process}

def p_select_sequencer(params: AztecModelParams,
                   _2,
                   _3,
                   state: AztecModelState) -> Signal:
    """
    
    """
    processes_to_transition = [p for p in state['processes']
                               if p.current_phase == SelectionPhase.pending_proposals
                               and p.duration_in_current_phase >= params['proposal_duration']]
    
    # selection_results: process_uuid -> (winner_proposal, uncle_proposal_list)
    updated_processes: dict[ProcessUUID, Process] = {}
    for process in processes_to_transition:
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
            
            updated_process = copy(process)
            updated_process.current_phase = SelectionPhase.pending_reveal
            updated_process.leading_sequencer = winner_proposal.uuid
            updated_process.uncle_sequencers = [p.uuid for p in uncle_proposals]
            updated_processes[process.uuid] = updated_process
        else:
            pass

    return {'update_processes': updated_processes}


def p_reveal_block_content(params: AztecModelParams,
                   _2,
                   _3,
                   state: AztecModelState) -> Signal:
    """
    
    """
    updated_processes: dict = {}
    # TODO
    # For every process on the `pending_reveal` phase, do:
    # - If the process has blown the phase duration, 
    # then transition to skipped. 
    # - Else, check if the the block content was revealed for that process.
    # If yes, advance to the next phase. Else, nothing happens.
    return {'update_processes': updated_processes}


def p_submit_block_proofs(params: AztecModelParams,
                   _2,
                   _3,
                   state: AztecModelState) -> Signal:
    """
    
    """
    updated_processes: dict = {}
    # TODO
    # For every process on the `pending_rollup_proof` phase, do:
    # - If the process has blown the phase duration, 
    # then transition to / trigger reorg.
    # - Else, check if a **valid** rollup proof was submitted for that process.
    # If yes, advance to the next phase. Else, nothing happens.
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



def s_processes(params: AztecModelParams,
                      _2,
                      _3,
                      state: AztecModelState,
                      signal: Signal) -> VariableUpdate:
    """
    
    """
    processes = deepcopy(state['processes'])

    processes_to_update = signal.get('updated_processes', {}),
    for process_uuid, updated_process in processes_to_update.items():
        pass # TODO   


    new_process = signal.get('new_process', None)
    if new_process != None:
        processes.append(new_process)

    return ('processes', processes)
