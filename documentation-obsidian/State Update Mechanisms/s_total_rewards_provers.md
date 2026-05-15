## Summary

- Same code as [[s_agents_rewards]] except it records adding the new prover rewards to the cumulative sum thus far.

## Code

<pre lang="python"><code>
def s_total_rewards_provers(

params: AztecModelParams, _2, _3, state: AztecModelState, signal: SignalPayout

):

  

p: Process = state["current_process"] # type: ignore

if p.phase == SelectionPhase.finalized:

txs = state["transactions"]

total_rewards = signal.get("block_reward", 0.0)

  

old_total_rewards_provers = state["total_rewards_provers"]

delta_rewards_provers = total_rewards * params["rewards_to_provers"]

  

sequencer_uuid = state["transactions"][p.tx_rollup_proof].who

  

if not p.entered_race_mode:

prover_uuid = txs[p.tx_commitment_bond].prover_uuid # type: ignore

relays = [a_id for (a_id, a)

in state["agents"].items() if a.is_relay]

relay_uuid: AgentUUID = choice(relays)

else:

prover_uuid = sequencer_uuid

relay_uuid = sequencer_uuid

  

# Track Rewards

new_total_rewards_provers = old_total_rewards_provers + delta_rewards_provers

return ("total_rewards_provers", new_total_rewards_provers)

else:

return ("total_rewards_provers", state["total_rewards_provers"])
</code></pre>