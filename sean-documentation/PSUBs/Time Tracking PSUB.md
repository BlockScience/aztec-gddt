## Code

{
        'label': 'Time Tracking',
        'ignore': False,
        'desc': 'Updates the time in the system',
        'policies': {
            'evolve_time': p_evolve_time
        },
        'variables': {
            'time_l1': s_block_time,
            'delta_blocks': s_delta_blocks,
            'current_process': s_current_process_time,
        }
    },

## Policies

[[p_evolve_time]]

## State Updates

[[s_block_time]]
[[s_delta_blocks]]
[[s_current_process_time]]