## Summary
- If the state is finalized, total fees is the sum of:
	- Winning proposal fee
	- Content reveal fee
	- Rollup proof fee
	- The commitment bond fee is it is not none
	- The blob fee from the content reveal
- Multiply this by gwei to tokens
## Code

<pre lang="python"><code>
def p_fee_cashback(
    params: AztecModelParams, _2, _3, state: AztecModelState
) -> SignalPayout:
    p: Process = state["current_process"]  # type: ignore
    if p.phase == SelectionPhase.finalized:

        txs: dict[TxUUID, AnyL1Transaction] = state["transactions"]
        # L1 Fees
        total_fees: float = 0
        total_fees += txs[p.tx_winning_proposal].fee
        total_fees += txs[p.tx_content_reveal].fee
        total_fees += txs[p.tx_rollup_proof].fee
        total_fees += (
            txs[p.tx_commitment_bond].fee if p.tx_commitment_bond is not None else 0
        )

        # Blob Fees
        total_fees += txs[p.tx_content_reveal].blob_fee  # type: ignore

        total_fees *= params["gwei_to_tokens"]
    else:
        total_fees = 0

    return SignalPayout(fee_cashback=total_fees)
</code></pre>