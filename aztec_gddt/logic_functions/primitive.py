from typing import Callable
from aztec_gddt.helper import *
from aztec_gddt.types import *


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


def replace_suf(variable: str, default_value=0.0) -> Callable:
    """Creates replacing function for state update from string

    Args:
        variable (str): The variable name that is updated

    Returns:
        function: A function that continues the state across a substep
    """
    return lambda _1, _2, _3, state, signal: (
        variable,
        signal.get(variable, default_value),
    )


def add_suf(variable: str, default_value=0.0) -> Callable:
    """
    Creates replacing function for state update from string

    Args:
        variable (str): The variable name that is updated

    Returns:
        function: A function that continues the state across a substep
    """
    return lambda _1, _2, _3, state, signal: (
        variable,
        signal.get(variable, default_value) + state[variable],
    )


def s_erase_history(
    params: AztecModelParams,
    _2,
    history,
    state: AztecModelState,
    signal: SignalEvolveProcess,
):
    """
    This substep is a hack for legacy cadCAD that makes it so that substep states do not get
    saved in favor of just the ending timestep state, thus saving large amounts of space
    """

    for t, timestep_state in enumerate(history):
        # We may want to drop the transactions key if running on `multi_mode`
        # history[t] = [{k: v for k, v in history[t][-1].items() if k != 'transactions'}]
        # Or not, if on `single_mode`
        history[t] = [history[t][-1]]
    #     # for i, substep_state in enumerate(timestep_state):
    #     #     if i > 0:
    #     #         history[t]
    # print(f"{state['timestep']}, {len(pickle.dumps(state))}, {len(pickle.dumps(history))}")
    # dict(sorted({k: len(pickle.dumps(v)) for k, v in state.items()}.items(), key=lambda it: it[1], reverse=True))
    return ("timestep", state["timestep"])  # type: ignore
