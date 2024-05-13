## Summary

- Create the token supply metrics by aggregating over the balances in the system
## Code

<pre lang="python"><code>
def s_token_supply(
    params: AztecModelParams,
    _2,
    _3,
    state: AztecModelState,
    signal: SignalEvolveProcess,
):
    """
    Logic for token supply.
    """
    return ("token_supply", TokenSupply.from_state(state))
</code></pre>