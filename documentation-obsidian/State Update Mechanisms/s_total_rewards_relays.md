## Summary

- Same code as [[s_agents_rewards]] except it records adding the new relay rewards to the cumulative sum thus far.
## Code

<pre lang="python"><code>
def s_total_rewards_relays(

params: AztecModelParams, _2, _3, state: AztecModelState, signal: SignalPayout

):

old_total_rewards_relays = state["total_rewards_relays"]

  

p: Process = state["current_process"] # type: ignore

if p.phase == SelectionPhase.finalized:

txs = state["transactions"]

total_rewards = signal.get("block_reward", 0.0)

agents: dict[AgentUUID, Agent] = state["agents"].copy()

  

delta_rewards_prover = total_rewards * params["rewards_to_provers"]

delta_rewards_relay = total_rewards * params["rewards_to_relay"]

delta_rewards_sequencer = total_rewards - (

delta_rewards_relay + delta_rewards_prover

)

  

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

new_total_rewards_relays = old_total_rewards_relays + delta_rewards_relay

return ("total_rewards_relays", new_total_rewards_relays)

else:

return ("total_rewards_relays", state["total_rewards_relays"])
</code></pre>