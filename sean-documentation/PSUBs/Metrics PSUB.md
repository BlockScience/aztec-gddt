## Code

<pre lang="python"><code>
{
        'label': 'Metrics',
        'ignore': False,
        'policies': {
        },
        'variables': {
            'token_supply': s_token_supply,
            'finalized_blocks_count': lambda _1, _2, _3, s, _5:  ('finalized_blocks_count', s['finalized_blocks_count'] + 1 if s['current_process'].phase == SelectionPhase.finalized else s['finalized_blocks_count'])
        }
    }
</code></pre>

## Policies


## State Updates

[[s_token_supply]]
[[s_finalized_blocks_count_lambda_function]]