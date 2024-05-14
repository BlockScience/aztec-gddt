## Summary
- Only is executed if the current process is in finalized mode
- Grab the block_reward as total_rewards from the prior policy and the transactions from the state
- Split out the rewards to relayers, provers, sequencers by using the parameters of rewards_to_relays and rewards_to_provers.
- If it is not in race mode pick the prover_uuid for the prover to use and randomly pull a relayer from the state, otherwise both are the sequencer
- Disburse the rewards

## Code

<pre lang="python"><code>
def s_agents_rewards(

params: AztecModelParams, _2, _3, state: AztecModelState, signal: SignalPayout

):

  

p: Process = state["current_process"] # type: ignore

if p.phase == SelectionPhase.finalized:

txs = state["transactions"]

total_rewards = signal.get("block_reward", 0.0)

agents: dict[AgentUUID, Agent] = state["agents"].copy()

  

rewards_relay = total_rewards * params["rewards_to_relay"]

rewards_prover = total_rewards * params["rewards_to_provers"]

rewards_sequencer = total_rewards - (rewards_relay + rewards_prover)

  

sequencer_uuid = state["transactions"][p.tx_rollup_proof].who

  

if not p.entered_race_mode:

prover_uuid = txs[p.tx_commitment_bond].prover_uuid # type: ignore

relays = [a_id for (a_id, a)

in state["agents"].items() if a.is_relay]

relay_uuid: AgentUUID = choice(relays)

else:

prover_uuid = sequencer_uuid

relay_uuid = sequencer_uuid

  

# Disburse Rewards

agents[sequencer_uuid].balance += rewards_sequencer

agents[prover_uuid].balance += rewards_prover

agents[relay_uuid].balance += rewards_relay

return ("agents", agents)

else:

return ("agents", state["agents"])
</code></pre>