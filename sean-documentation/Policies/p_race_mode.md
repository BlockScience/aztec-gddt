## Summary

- remaining_time = max_phase_duration - process.duration_in_current_phase
- If remaining time is less than 0, move to skipped else
- Two transactions for a rollup proof and content reveal are created and linked to the l1-builder
## Code

<pre lang="python"><code>
def p_race_mode(
    params: AztecModelParams, _2, _3, state: AztecModelState
) -> SignalEvolveProcess:
    """
    Logic for race mode.
    """
    process = state["current_process"]
    updated_process: Optional[Process] = None
    new_transactions: list[TransactionL1] = list()

    max_phase_duration = params["phase_duration_race_max_blocks"]
    
    # NOTE: Logic of race mode is different.
    # No check here for L1 censorship.

    if process is None:
        pass
    else:
        if process.phase == SelectionPhase.proof_race:
            remaining_time = max_phase_duration - process.duration_in_current_phase
            if remaining_time < 0:
                updated_process = copy(process)
                updated_process.phase = SelectionPhase.skipped
                updated_process.duration_in_current_phase = 0
            else:
                # Assumption: there is a hard-coded L1 Builder agent
                # who immediately ends the race mode.
                who = "l1-builder"
                gas: Gas = params["gas_estimators"].content_reveal(state)
                fee: Gwei = gas * state["gas_fee_l1"]
                blob_gas: BlobGas = params["gas_estimators"].content_reveal_blob(
                    state)
                blob_fee: Gwei = blob_gas * state["gas_fee_blob"]

                tx_count = params["tx_estimators"].transaction_count(state)
                tx_avg_size = int(
                    state["transactions"][process.tx_winning_proposal].size / tx_count)  # type: ignore
                tx_avg_fee_per_size = params[
                    "tx_estimators"
                ].transaction_average_fee_per_size(state)

                tx_1 = RollupProof(
                    who=who, when=state["time_l1"], uuid=uuid4(), gas=gas, fee=fee
                )

                tx_2 = ContentReveal(
                    who=who,
                    when=state["time_l1"],
                    uuid=uuid4(),
                    gas=gas,
                    fee=fee,
                    blob_gas=blob_gas,
                    blob_fee=blob_fee,
                    transaction_count=tx_count,
                    transaction_avg_size=tx_avg_size,
                    transaction_avg_fee_per_size=tx_avg_fee_per_size,
                )

                new_transactions.append(tx_1)
                new_transactions.append(tx_2)

                updated_process = copy(process)
                updated_process.tx_rollup_proof = tx_1.uuid
                updated_process.block_content_is_revealed = True
                updated_process.tx_content_reveal = tx_2.uuid
                updated_process.phase = SelectionPhase.finalized
                updated_process.duration_in_current_phase = 0
        else:
            pass

    return {"update_process": updated_process, "new_transactions": new_transactions}
</code></pre>