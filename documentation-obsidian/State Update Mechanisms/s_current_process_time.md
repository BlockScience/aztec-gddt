## Summary
- Update the time in the current process by delta blocks

## Code

<pre lang="python"><code>
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
        updated_process.duration_in_current_phase += signal.get(
            "delta_blocks", 0)
    else:
        pass

    return ("current_process", updated_process)
</code></pre>