## Summary
- Record the delta_blocks signal from the prior policy

## Code

<pre lang="python"><code>
def s_delta_blocks(_1, _2, _3, _4, signal: SignalTime):
    """
    State update function for change in block number.

    Args:
        signal (Signal): The Signal, generated in p_evolve_time, of how many blocks to advance time.

    Returns:
        VariableUpdate
    """
    return ("delta_blocks", signal.get("delta_blocks", 0))
</code></pre>