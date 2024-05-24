from aztec_gddt.helper import *
from aztec_gddt.types import *
from copy import deepcopy, copy


def p_evolve_time(
    params: AztecModelParams, _2, _3, state: AztecModelState
) -> SignalTime:
    """
    Policy function giving the change in number of blocks.

    Args:
         params (AztecModelParams): The current parameters of the model.

    Returns:
        Signal:
            a dictionary of variables that can be used in an update
    """
    return {"delta_blocks": params["timestep_in_blocks"]}


def p_evolve_time_dynamical(_1, _2, _3, state: AztecModelState) -> SignalTime:
    """
    Policy function giving the change in number of blocks.

    Args:
         state (AztecModelState): The current state of the model.

    Returns:
        Signal:
            a dictionary of variables that can be used in an update
    """
    return {"delta_blocks": state["advance_l1_blocks"]}


def s_block_time(
    params: AztecModelParams, _2, _3, state: AztecModelState, signal: SignalTime
):
    """
    State update function advancing block time.

    Args:
         params (AztecModelParams): The current parameters of the model.
         state (AztecModelState): The current state of the model.
         signal (Signal): The Signal, generated in p_evolve_time, of how many blocks to advance time.

    Returns:

            A two-element tuple that all state update functions must return.
    """
    return ("time_l1", state["time_l1"] + signal["delta_blocks"])  # type: ignore


def s_delta_blocks(_1, _2, _3, _4, signal: SignalTime):
    """
    State update function for change in block number.

    Args:
        signal (Signal): The Signal, generated in p_evolve_time, of how many blocks to advance time.

    Returns:
        VariableUpdate
    """
    return ("delta_blocks", signal.get("delta_blocks", 0))


def s_reset_advance(
    params: AztecModelParams, _2, _3, state: AztecModelState, signal: SignalTime
):
    """
    State update function advancing block time.

    Args:
         params (AztecModelParams): The current parameters of the model.
         state (AztecModelState): The current state of the model.
         signal (Signal): The Signal, generated in p_evolve_time, of how many blocks to advance time.

    Returns:

            A two-element tuple that all state update functions must return.
    """
    return ("advance_l1_blocks", 0)  # type: ignore


def s_current_process_time(_1, _2, _3, state: AztecModelState, signal: SignalTime):
    """
    State update function for change in block number.

    Args:
        signal (Signal): The Signal, generated in p_evolve_time, of how many blocks to advance time.

    Returns:
        VariableUpdate
    """
    updated_process: Process | None = copy(state["current_process"])
    if updated_process is not None:
        # type: ignore
        updated_process.duration_in_current_phase += signal.get("delta_blocks", 0)

    return ("current_process", updated_process)


def s_current_process_time_dynamical(
    _1, _2, _3, state: AztecModelState, signal: SignalTime
):
    """
    State update function for change in block number.

    Args:
        signal (Signal): The Signal, generated in p_evolve_time, of how many blocks to advance time.

    Returns:
        VariableUpdate
    """
    delta_blocks = signal.get("delta_blocks", 0)
    updated_process: Process | None = copy(state["current_process"])
    if updated_process is not None:
        if delta_blocks > 0:
            updated_process.current_phase_init_time += delta_blocks

    return ("current_process", updated_process)


def s_is_censored(p, _1, _2, s, _5):
    return (
        "is_censored",
        check_for_censorship(p, s),
    )
