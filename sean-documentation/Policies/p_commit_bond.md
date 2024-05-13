## Summary

- Bond amount and commit duration are taken in as parameters


## Code

<pre lang="python"><code>
def p_commit_bond(
    params: AztecModelParams,
    _2,
    history: list[list[AztecModelState]],
    state: AztecModelState,
) -> SignalEvolveProcess:
    process: Process | None = state["current_process"]
    updated_process: Optional[Process] = None
    new_transactions = list()
    advance_blocks = 0
    transfers: list[Transfer] = []
    bond_amount = params["commit_bond_amount"]
    commit_duration = params["phase_duration_commit_bond_max_blocks"]

    if process is None:
        pass
    else:
        if process.phase == SelectionPhase.pending_commit_bond:
            remaining_time = commit_duration - process.duration_in_current_phase
            if remaining_time < 0:
                # Move to Proof Race mode if duration is expired
                updated_process = copy(process)
                updated_process.phase = SelectionPhase.proof_race
                updated_process.entered_race_mode = True
                updated_process.duration_in_current_phase = 0

                # Slash leading sequencer if no commit bond is put down.
                slashed_amount = params["slash_params"].failure_to_commit_bond
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
                gas: Gas = params["gas_estimators"].commitment_bond(state)
                fee = gas * state["gas_fee_l1"]

                # Assumption: Agents have extra costs / profit considerations and need a safety buffer
                SAFETY_BUFFER = params['safety_factor_commit_bond'] * fee

                expected_l2_blocks_per_day = params['l1_blocks_per_day'] / \
                    total_phase_duration(params)

                # expected_rewards = params['daily_block_reward']
                # expected_rewards *= rewards_to_sequencer(params)
                # expected_rewards /= expected_l2_blocks_per_day
                expected_rewards = 1 #XXX: Temporary to ignore economic assumptions. 
                assert expected_rewards > 0, "COMMIT_BOND: Expected rewards should be positive."

                # expected_costs: float = params["op_cost_sequencer"]
                # expected_costs += fee
                # expected_costs += SAFETY_BUFFER
                # expected_costs *= params['gwei_to_tokens']
                expected_costs = 0 #XXX: Temporary to ignore economic assumptions. 
                assert expected_costs == 0, "COMMIT_BOND: Expected costs should be 0."

                payoff_reveal = expected_rewards - expected_costs
                assert payoff_reveal >= 0, "COMMIT_BOND: Payoff should not be negative."

                if payoff_reveal >= 0:

                    # If duration is not expired, do  a trial to see if bond is commited
                    agent_decides_to_reveal_commit_bond = bernoulli_trial(
                        probability=trial_probability(params['phase_duration_commit_bond_max_blocks'],
                                                      params['final_probability'])
                    )
                    # gas_fee_l1_acceptable = (
                    #     state["gas_fee_l1"] <= params["gas_threshold_for_tx"]
                    # )

                    gas_fee_l1_acceptable = True #XXX: Temporary economic assumption
                    
                    block_is_uncensored = check_for_censorship(params, state)
                    
                    if (agent_decides_to_reveal_commit_bond 
                        and gas_fee_l1_acceptable
                        and block_is_uncensored):
                        updated_process = copy(process)
                        lead_seq: Agent = state['agents'][process.leading_sequencer]
                        proposal_uuid = process.tx_winning_proposal
                        proving_market_is_used = bernoulli_trial(
                            params["proving_marketplace_usage_probability"]
                        )

                        if proving_market_is_used:
                            provers: list[AgentUUID] = [
                                a_id
                                for (a_id, a) in state["agents"].items()
                                if a.is_prover and a.balance >= bond_amount
                            ]

                            if len(provers) > 0:
                                prover: AgentUUID = choice(provers)
                            else:
                                if (lead_seq.balance >= bond_amount):
                                    prover = updated_process.leading_sequencer
                                else:
                                    prover = None
                        else:
                            if (lead_seq.balance >= bond_amount):
                                prover = updated_process.leading_sequencer
                            else:
                                prover = None

                        if prover is not None:
                            # TODO: double-check this.
                            advance_blocks = remaining_time
                            updated_process.phase = SelectionPhase.pending_reveal
                            updated_process.duration_in_current_phase = 0
                            tx = CommitmentBond(
                                who=prover,
                                when=state["time_l1"],
                                uuid=uuid4(),
                                gas=gas,
                                fee=fee,
                                proposal_tx_uuid=proposal_uuid,
                                prover_uuid=prover,
                                bond_amount=bond_amount,
                            )
                            new_transactions.append(tx)
                            updated_process.tx_commitment_bond = tx.uuid
                        else:
                            pass
                    else:
                        # Force Race Mode by doing nothing
                        pass
                else:
                    # else, nothing happens
                    pass
        else:
            pass
    return {
        "update_process": updated_process,
        "new_transactions": new_transactions,
        "advance_l1_blocks": advance_blocks,
        "transfers": transfers,
    }
</code></pre>