## Summary

- First check to make sure we are in the pending reveal phase otherwise nothing is going to happen
- If remaining time is less than 0, enter into proof race and slash the leading sequencer by params["slash_params"].failure_to_reveal_block
- gas: Gas = params["gas_estimators"].content_reveal(state)
- fee = gas * state["gas_fee_l1"]
- SAFETY_BUFFER = params['safety_factor_reveal_content'] * fee 
- expected_l2_blocks_per_day = params['l1_blocks_per_day'] / \
                    total_phase_duration(params)
- expected_rewards = 1, expected_costs = 0, payoff_reveal = expected_rewards - expected_costs
- Bernoulli trial for agent_decides_to_reveal_block_content
- gas_fee_blob_acceptable = True, gas_fee_l1_acceptable = True
- block_is_uncensored = check_for_censorship(params, state)
- If agent_expects_profit and agent_decides_to_reveal_block_content and gas_fee_blob_acceptable and gas_fee_l1_acceptable and block_is_uncensored then
- Switch phase to pending_rollup_proof
- Create a content reveal transaction with the lead sequencer
- Set this new transaction ID to the variable updated_process.tx_content_reveal
## Code

<pre lang="python"><code>
def p_reveal_content(
    params: AztecModelParams,
    _2,
    history: list[list[AztecModelState]],
    state: AztecModelState,
) -> SignalEvolveProcess:
    """
    Advances state of Processes that have revealed block content.
    """

    # Note: Advances state of Process in reveal phase that have revealed block content.
    process = state["current_process"]
    updated_process: Optional[Process] = None
    advance_blocks = 0
    new_transactions = list()
    transfers: list[Transfer] = []

    max_reveal_duration = params["phase_duration_reveal_max_blocks"]

    if process is None:
        pass
    else:
        if process.phase == SelectionPhase.pending_reveal:

            # If the process has blown the phase duration
            remaining_time = max_reveal_duration - process.duration_in_current_phase
            if remaining_time < 0:
                updated_process = copy(process)
                updated_process.phase = SelectionPhase.proof_race
                updated_process.entered_race_mode = True
                updated_process.duration_in_current_phase = 0

                # Slash leading sequencer if content is not revealed.
                slashed_amount = params["slash_params"].failure_to_reveal_block
                transfers.append(
                    Transfer(
                        source=updated_process.leading_sequencer,
                        destination="burnt",
                        amount=slashed_amount,
                        kind=TransferKind.slash_sequencer,
                        to_sequencer=True,
                    )
                )
            else:
                # NOTE: Costs now include gas fees and safety buffer.
                gas: Gas = params["gas_estimators"].content_reveal(state)
                fee = gas * state["gas_fee_l1"]
                # Assumption: Agents have extra costs / profit considerations and need a safety buffer
                SAFETY_BUFFER = params['safety_factor_reveal_content'] * fee 
                expected_l2_blocks_per_day = params['l1_blocks_per_day'] / \
                    total_phase_duration(params)

                # expected_rewards = params['daily_block_reward']
                # expected_rewards *= rewards_to_sequencer(params)
                # expected_rewards /= expected_l2_blocks_per_day
                expected_rewards = 1 #XXX: Temporary to ignore economic assumptions. 
                assert expected_rewards >= 0, "REVEAL_CONTENT: Expected rewards should be positive."

                
                # expected_costs: float = params["op_cost_sequencer"]
                # expected_costs += fee
                # expected_costs += SAFETY_BUFFER
                # expected_costs *= params['gwei_to_tokens']
                expected_costs = 0 #XXX: Temporary to ignore economic assumptions. 
                assert expected_costs == 0, "REVEAL_CONTENT: Expected costs should be zero."


                payoff_reveal = expected_rewards - expected_costs

                agent_expects_profit = payoff_reveal >= 0
                assert agent_expects_profit, "REVEAL_CONTENT: Agent should be expecting profit."

                agent_decides_to_reveal_block_content = bernoulli_trial(
                    probability=trial_probability(params['phase_duration_reveal_max_blocks'],
                                                  params['final_probability'])
                )

                # gas_fee_blob_acceptable = (
                #     state["gas_fee_blob"] <= params["blob_gas_threshold_for_tx"]
                # )

                gas_fee_blob_acceptable = True

                # gas_fee_l1_acceptable = (
                #     state["gas_fee_l1"] <= params["gas_threshold_for_tx"]
                # )
                
                gas_fee_l1_acceptable = True

                block_is_uncensored = check_for_censorship(params, state)

                if (
                    agent_expects_profit
                    and agent_decides_to_reveal_block_content
                    and gas_fee_blob_acceptable
                    and gas_fee_l1_acceptable
                    and block_is_uncensored
                ):
                    updated_process = copy(process)
                    advance_blocks = remaining_time
                    updated_process.phase = SelectionPhase.pending_rollup_proof
                    updated_process.duration_in_current_phase = 0

                    who = updated_process.leading_sequencer  
                    blob_gas: BlobGas = params["gas_estimators"].content_reveal_blob(
                        state
                    )
                    blob_fee: Gwei = blob_gas * state["gas_fee_blob"]

                    tx_count = params["tx_estimators"].transaction_count(state)
                    tx_avg_size = int(
                        state["transactions"][process.tx_winning_proposal].size / tx_count)  # type: ignore
                    tx_avg_fee_per_size = params[
                        "tx_estimators"
                    ].transaction_average_fee_per_size(state)

                    tx = ContentReveal(
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

                    new_transactions.append(tx)
                    updated_process.tx_content_reveal = tx.uuid

                else:
                    pass
        else:
            pass

    return {
        "update_process": updated_process,
        "new_transactions": new_transactions,
        "advance_l1_blocks": advance_blocks,
    }
</code></pre>