## Summary
- Check if the current process phase is pending_proposals, otherwise new_proposals is none
- Find current proposers as those proposers in the new_transactions that proposed after the current_process.current_phase_init_time
- Any agents not in this are potential_proposers as long as they are sequencers and also have a staked amount greater than params['minimum_stake']
- For each potential proposer, do a bernoulli trial, i.e. bernoulli_trial(trial_probability(params['phase_duration_proposal_max_blocks'],
                                                     params['final_probability']))
	to determine if a new proposal should be created
- The following code defines out the metadata aspects
```
tx_uuid = uuid4()
                    gas: Gas = params["gas_estimators"].proposal(state)
                    fee: Gwei = gas * state["gas_fee_l1"]
                    score = uniform.rvs()  # Assumption: score is always uniform
                    size = params["tx_estimators"].proposal_average_size(state)
                    public_share = 0.5  # Assumption: Share of public function calls 

                    # gas_fee_l1_acceptable = (
                    # state["gas_fee_l1"] <= params["gas_threshold_for_tx"]
                    # )

                    gas_fee_l1_acceptable = True #XXX: Temporary economic assumption

                    block_is_uncensored = check_for_censorship(params, state)
```
- As long as the gas fee is acceptable and the block is not censored, a block is created
## Code

<pre lang="python"><code>
def s_transactions_new_proposals(
    params: AztecModelParams, _2, _3, state: AztecModelState, _5
):
    """
    Logic for submitting new proposals.
    """

    new_transactions = state["transactions"].copy()
    current_process: Process | None = state["current_process"]
    new_proposals: dict[TxUUID, Proposal] = dict()
    if current_process is not None:
        if current_process.phase == SelectionPhase.pending_proposals:
            current_proposers: set[AgentUUID] = {p.who
                                                 for p in new_transactions.values()
                                                 if p.when >= current_process.current_phase_init_time}
            potential_proposers: set[AgentUUID] = {
                u.uuid
                for u in state["agents"].values()
                if u.uuid not in current_proposers
                and u.is_sequencer
                and u.staked_amount >= params['minimum_stake']
            }

            for potential_proposer in potential_proposers:
                if bernoulli_trial(trial_probability(params['phase_duration_proposal_max_blocks'],
                                                     params['final_probability'])):

                    tx_uuid = uuid4()
                    gas: Gas = params["gas_estimators"].proposal(state)
                    fee: Gwei = gas * state["gas_fee_l1"]
                    score = uniform.rvs()  # Assumption: score is always uniform
                    size = params["tx_estimators"].proposal_average_size(state)
                    public_share = 0.5  # Assumption: Share of public function calls 

                    # gas_fee_l1_acceptable = (
                    # state["gas_fee_l1"] <= params["gas_threshold_for_tx"]
                    # )

                    gas_fee_l1_acceptable = True #XXX: Temporary economic assumption

                    block_is_uncensored = check_for_censorship(params, state)

                    if (gas_fee_l1_acceptable
                        and block_is_uncensored
                        ):
                        new_proposal = Proposal(
                            who=potential_proposer,
                            when=state["time_l1"],
                            uuid=tx_uuid,
                            gas=gas,
                            fee=fee,
                            score=score,
                            size=size,
                            public_composition=public_share,
                        )

                        new_proposals[tx_uuid] = new_proposal
                    else:
                        pass
                else:
                    pass
        else:
            new_proposals = dict()
    else:
        new_proposals = dict()

    new_transactions = {**new_transactions, **new_proposals}
    return ("transactions", new_transactions)
</code></pre>