## Summary

- If the transaction is finalized the total fees come from total_tx_fee from the content reveal
## Code

<pre lang="python"><code>
def p_fee_from_users(
    params: AztecModelParams, _2, _3, state: AztecModelState
) -> SignalPayout:
    p: Process = state["current_process"]  # type: ignore
    if p.phase == SelectionPhase.finalized:
        txs: dict[TxUUID, AnyL1Transaction] = state["transactions"]
        total_fees = txs[p.tx_content_reveal].total_tx_fee  # type: ignore
    else:
        total_fees = 0

    return SignalPayout(fee_from_users=total_fees)
</code></pre>