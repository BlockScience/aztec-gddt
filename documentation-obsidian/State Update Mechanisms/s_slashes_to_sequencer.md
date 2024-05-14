## Summary

- Filter to any recent transfers that went from slashing a sequencer that also was sent to a sequencer
- Add the number of these to the running total

## Code

<pre lang="python"><code>
def s_slashes_to_sequencer(
    params: AztecModelParams,
    _2,
    _3,
    state: AztecModelState,
    signal: SignalEvolveProcess,
):
    """
    Logic for keeping track of how many slashes have occurred.
    """
    old_slashes_to_sequencers = state["slashes_to_sequencers"]
    transfers: Sequence[Transfer] = signal.get("transfers", [])  # type: ignore

    # Calculate the number of slashes of each type to add
    delta_slashes_sequencers = len(
        [
            transfer
            for transfer in transfers
            if transfer.kind == TransferKind.slash_sequencer and transfer.to_sequencer
        ]
    )

    updated_slashes_to_sequencer = old_slashes_to_sequencers + delta_slashes_sequencers

    return ("slashes_to_sequencers", updated_slashes_to_sequencer)
</code></pre>