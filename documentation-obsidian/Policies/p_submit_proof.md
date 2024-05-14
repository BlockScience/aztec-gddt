## Summary

- If pending rollup proof is the current phase and the remaining time is less than 0, create a skipped block, create a slash of the bond amount and slash the prover, else:
- Get gas from gas estimators for content reveal, pull fee from state, set up safety buffer as params['safety_factor_rollup_proof'] * fee
- expected_l2_blocks_per_day = params['l1_blocks_per_day'] / total_phase_duration(params)
- expected_rewards = 1, expected_costs = 0, payoff_reveal = expected_rewards - expected_costs
- Bernoulli trial is used to determine if the agent decides to reveal the rollup proof
- gas_fee_l1_acceptable = True # Assume gas fee is acceptable. 
- block_is_uncensored = check_for_censorship(params, state)
- If agent_decides_to_reveal_rollup_proof and gas_fee_l1_acceptable and agent_expects_profit and block_is_uncensored, create the finalized phase and rollup proof transaction

## Code

<pre lang="python"><code>
def p_submit_proof(
    params: AztecModelParams, _2, _3, state: AztecModelState
) -> SignalEvolveProcess:
    """
    Advances state of Processes that have  submitted rollup proofs.
    """
    process = state["current_process"]
    updated_process: Optional[Process] = None
    new_transactions = list()
    advance_blocks = 0
    transfers: list[Transfer] = []

    phase_max_duration = params["phase_duration_rollup_max_blocks"]

    if process is None:
        pass
    else:
        if process.phase == SelectionPhase.pending_rollup_proof:
            remaining_time = phase_max_duration - process.duration_in_current_phase
            if remaining_time < 0:
                updated_process = copy(process)
                updated_process.phase = SelectionPhase.skipped
                updated_process.duration_in_current_phase = 0

                # Determine who should be slashed, and how much.
                transactions = state["transactions"]
                commit_bond_id = updated_process.tx_commitment_bond
                commit_bond: CommitmentBond = transactions.get(
                    commit_bond_id, None)  # type: ignore
                who_to_slash = commit_bond.prover_uuid
                how_much_to_slash = commit_bond.bond_amount

                # Slash the prover for failing to reveal the proof.
                slash_transfer = Transfer(
                    source=who_to_slash,
                    destination="burnt",
                    amount=how_much_to_slash,
                    kind=TransferKind.slash_prover,
                    to_prover=True,
                )
                transfers.append(slash_transfer)

            else:
                gas: Gas = params["gas_estimators"].content_reveal(state)
                fee = gas * state["gas_fee_l1"]
                # Assumption: Agents have extra costs / profit considerations and need a safety buffer
                SAFETY_BUFFER = params['safety_factor_rollup_proof'] * fee
                expected_l2_blocks_per_day = params['l1_blocks_per_day'] / \
                    total_phase_duration(params)

                # expected_rewards = params['daily_block_reward']
                # expected_rewards *= params['rewards_to_provers']
                # expected_rewards /= expected_l2_blocks_per_day
                expected_rewards = 1
                assert expected_rewards >= 0, "SUBMIT PROOF: Expected rewards should be positive."

                # expected_costs: float = params["op_cost_prover"]
                # expected_costs += fee
                # expected_costs += SAFETY_BUFFER
                # expected_costs *= params['gwei_to_tokens']
                expected_costs = 0
                assert expected_costs == 0, "SUBMIT PROOF: Expected costs should be zero."

                payoff_reveal = expected_rewards - expected_costs

                agent_expects_profit = payoff_reveal >= 0
                assert agent_expects_profit, "SUBMIT_PROOF: Agent should expect profit."

                agent_decides_to_reveal_rollup_proof = bernoulli_trial(
                    probability=trial_probability(params['phase_duration_rollup_max_blocks'],
                                                  params['final_probability'])
                )

                # gas_fee_l1_acceptable = (
                #     state["gas_fee_l1"] <= params["gas_threshold_for_tx"]
                # )
                gas_fee_l1_acceptable = True #XXX: Assume gas fee is acceptable. 

                block_is_uncensored = check_for_censorship(params, state)

                if (
                    agent_decides_to_reveal_rollup_proof 
                    and gas_fee_l1_acceptable 
                    and agent_expects_profit
                    and block_is_uncensored
                ):
                    updated_process = copy(process)
                    advance_blocks = remaining_time
                    updated_process.phase = SelectionPhase.finalized
                    updated_process.duration_in_current_phase = 0
                    transactions = state["transactions"]

                    commit_bond_id = updated_process.tx_commitment_bond
                    commit_bond: CommitmentBond = transactions.get(  # type: ignore
                        commit_bond_id, None)  # type: ignore
                    who = commit_bond.prover_uuid
                    gas: Gas = params['gas_estimators'].rollup_proof(  # type: ignore
                        state) # type: ignore
                    fee: Gwei = gas * state['gas_fee_l1'] # type: ignore

                    tx = RollupProof(
                        who=who, when=state["time_l1"], uuid=uuid4(), gas=gas, fee=fee
                    )

                    new_transactions.append(tx)
                    updated_process.tx_rollup_proof = tx.uuid

                else:
                    pass  # Nothing changes if no valid rollup
        else:
            pass

    return {
        "update_process": updated_process,
        "new_transactions": new_transactions,
        "advance_l1_blocks": advance_blocks,
        "transfers": transfers,
    }
</code></pre>