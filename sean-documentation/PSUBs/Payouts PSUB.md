## Code

<pre lang="python"><code>
    {
        'label': 'Payouts',
        'ignore': False, 
        'policies': {
            'block_reward': p_block_reward,
#            'fee_cashback': p_fee_cashback,
            'fee_from_users': p_fee_from_users
        },
        'variables':{
            'total_rewards_provers': s_total_rewards_provers,
            'total_rewards_sequencers': s_total_rewards_sequencers,
            'total_rewards_relays': s_total_rewards_relays,
            'agents': s_agents_rewards,
            'cumm_block_rewards': lambda _1,_2,_3,s1,s2: ('cumm_block_rewards', s2['block_reward'] + s1['cumm_block_rewards']),
#            'cumm_fee_cashback': lambda _1,_2,_3,s1,s2: ('cumm_fee_cashback', s2['fee_cashback'] + s1['cumm_fee_cashback'])
        }
    }
</code></pre>

## Policies

[[p_block_reward]]
[[p_fee_cashback]]
[[p_fee_from_users]]
## State Updates

[[s_total_rewards_provers]]
[[s_total_rewards_sequencers]]
[[s_total_rewards_relays]]
[[s_agents_rewards]]
[[s_cumm_fee_cashback_lambda_function]]
