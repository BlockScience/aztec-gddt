## Summary
- Return delta blocks equal to params["timestep_in_blocks"]

## Code

<pre lang="python"><code>
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
</code></pre>