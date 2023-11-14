from cadCAD_tools.types import Signal, VariableUpdate # type: ignore
from aztec_gddt.types import AztecModelParams, AztecModelState
from typing import Callable

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
