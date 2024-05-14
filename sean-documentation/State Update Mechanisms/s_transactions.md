## Summary

- Update the transactions with the new transactions
## Code

<pre lang="python"><code>
def s_transactions(
    params: AztecModelParams,
    _2,
    _3,
    state: AztecModelState,
    signal: SignalEvolveProcess,
):
    """
    Logic for new transactions.
    """

    new_tx_list: list[TransactionL1] = signal.get(
        "new_transactions", list()
    )  # type: ignore

    new_tx_dict: dict[TxUUID, TransactionL1] = {
        tx.uuid: tx for tx in new_tx_list}

    new_transactions = {**state["transactions"].copy(), **new_tx_dict}

    return ("transactions", new_transactions)
</code></pre>