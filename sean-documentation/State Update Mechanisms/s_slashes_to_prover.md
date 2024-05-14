## Summary

- Filter to any recent transfers that went from slashing a prover that also was sent to a prover
- Add the number of these to the running total
## Code

<pre lang="python"><code>
def s_slashes_to_prover(
    params: AztecModelParams,
    _2,
    _3,
    state: AztecModelState,
    signal: SignalEvolveProcess,
):
    """
    Logic for keeping track of how many slashes have occurred.
    """
    old_slashes_to_prover = state["slashes_to_provers"]
    transfers: Sequence[Transfer] = signal.get("transfers", [])  # type: ignore

    # Calculate the number of slashes of each type to add
    delta_slashes_prover = len(
        [
            transfer
            for transfer in transfers
            if (transfer.kind == TransferKind.slash_prover) and (transfer.to_prover == True)
        ]
    )

    updated_slashes_to_prover = old_slashes_to_prover + delta_slashes_prover

    return ("slashes_to_provers", updated_slashes_to_prover)
</code></pre>