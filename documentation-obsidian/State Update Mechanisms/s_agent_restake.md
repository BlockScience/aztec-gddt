## Summary
- Select all sequencers
- If the sequencer has less than the minimum stake they will top up to the minimum stake + 2 Ethereum or as close to it given not enough balance

## Code

<pre lang="python"><code>
def s_agent_restake(
    params: AztecModelParams,
    _2,
    history,
    state: AztecModelState,
    signal: SignalEvolveProcess,
):
    new_agents = state['agents'].copy()

    sequencers = {k: v for k, v in new_agents.items() if v.is_sequencer}
    for k, v in sequencers.items():
        if v.staked_amount < params['minimum_stake']:
            # Assumption: Sequencers top-up from balance with 2 more ETH than necessary
            max_amount_to_stake = (
                params['minimum_stake'] - v.staked_amount + 2.0)
            amount_to_stake = min(max_amount_to_stake, v.balance)
            v.balance -= amount_to_stake
            v.staked_amount += amount_to_stake

    return ('agents', new_agents)
</code></pre>