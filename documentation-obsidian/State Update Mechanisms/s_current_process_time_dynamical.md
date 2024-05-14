## Summary

- Update the current_phase_init_time by delta_blocks for the current process

## Code

<pre lang="python"><code>
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
</code></pre>