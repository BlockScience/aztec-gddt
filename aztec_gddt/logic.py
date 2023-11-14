from cadCAD_tools.types import Signal, VariableUpdate # type: ignore
from aztec_gddt.helper import *
from aztec_gddt.types import *
from typing import Callable
from uuid import uuid4
from copy import deepcopy

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
    selection_results: dict[ProcessUUID, tuple[Proposal, list[Proposal]]] = {}
    for process in processes_to_transition:
        proposals = state['proposals'].get(process.uuid, [])
        if len(proposals) > 0:

            # TODO: check if true
            number_uncles = min(len(proposals) - 1, params['uncle_count'])

            ranked_proposals = sorted(proposals, 
                                      key=lambda p: p.score,
                                      reverse=True)
            
            winner_proposal = ranked_proposals[0]
            uncle_proposals = ranked_proposals[1:number_uncles+1]
            selection_results[process.uuid] = (winner_proposal, uncle_proposals)
        else:
            pass

    return {'selection_results': selection_results}
    

def s_processes(params: AztecModelParams,
                      _2,
                      _3,
                      state: AztecModelState,
                      signal: Signal) -> VariableUpdate:
    """
    
    """
    updated_processes = deepcopy(state['processes'])


    new_process = signal.get('new_process', None)
    if new_process != None:
        updated_processes.append(new_process)

    return ('processes', updated_processes)