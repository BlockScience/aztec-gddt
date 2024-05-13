## Summary
- Return delta blocks as the value for advance_l1_blocks in the current state

## Code

<pre lang="python"><code>
def p_evolve_time_dynamical(
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
    return {"delta_blocks": state["advance_l1_blocks"]}

</code></pre>