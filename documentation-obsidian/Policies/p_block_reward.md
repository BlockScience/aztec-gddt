## Summary

- If the process is finalized compute the reward as follows:
	- total_phase_duration = p['phase_duration_proposal_max_blocks'] + p['phase_duration_reveal_max_blocks'] + p['phase_duration_commit_bond_max_blocks'] + p['phase_duration_rollup_max_blocks'])
	- expected_l2_blocks_per_day = params['l1_blocks_per_day'] / total_phase_duration
	- reward = params['daily_block_reward'] / expected_l2_blocks_per_day
## Code

<pre lang="python"><code>
def p_block_reward(
    params: AztecModelParams, _2, _3, state: AztecModelState
) -> SignalPayout:
    p: Process = state["current_process"]  # type: ignore
    if p.phase == SelectionPhase.finalized:

        # Assumption: this assumes that the average L2 block duration
        # will be the max L2 block duration
        expected_l2_blocks_per_day = params['l1_blocks_per_day'] / \
            total_phase_duration(params)
        reward = params['daily_block_reward'] / expected_l2_blocks_per_day
    else:
        reward = 0
    return SignalPayout(block_reward=reward)
</code></pre>