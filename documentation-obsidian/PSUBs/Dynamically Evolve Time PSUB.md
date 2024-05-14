## Code

<pre lang="python"><code>
{
        'label': 'Dynamically Evolve Time',
        'ignore': False, 
        'policies': {
             'conditionally_evolve_time': p_evolve_time_dynamical
        },
        'variables': {
            'time_l1': s_block_time,
            'delta_blocks': s_delta_blocks,
            'current_process': s_current_process_time_dynamical,
            'advance_l1_blocks': s_reset_advance
        }
    }
</code></pre>

## Policies

[[p_evolve_time_dynamical]]
## State Updates

[[s_block_time]]
[[s_delta_blocks]]
[[s_current_process_time_dynamical]]
[[s_reset_advance]]