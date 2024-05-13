## Summary
- Increment time_l1 by delta_blocks

## Code

<pre lang="python"><code>
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
</code></pre>