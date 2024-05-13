## Summary

- Set the advance L1 blocks back to 0

## Code

<pre lang="python"><code>
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
</code></pre>