## Code
{
        'label': 'Evolve Block Process',
        'ignore': False,
        'policies': {
            'init_process': p_init_process,
            'select_sequencer': p_select_proposal,
            'submit_commit_bond': p_commit_bond,
            'reveal_block_content': p_reveal_content,
            'submit_block_proof': p_submit_proof,
            'submit_block_proof_content_race': p_race_mode
        },
        'variables': {
            'current_process': s_process,
            'transactions': s_transactions,
            'advance_l1_blocks': s_advance_blocks,
            'slashes_to_sequencers': s_slashes_to_sequencer,
            'slashes_to_provers': s_slashes_to_prover,
            'agents': s_agent_transfer,
            'is_censored': lambda p, _1, _2, s, _5: ('is_censored', check_for_censorship(p, s))
        }
    }

## Policies

[[p_init_process]]
[[p_select_proposal]]
[[p_commit_bond]]
[[p_reveal_content]]
[[p_submit_proof]]
[[p_race_mode]]
## State Updates

[[s_process]]
[[s_transactions]]
[[s_advance_blocks]]
[[s_slashes_to_sequencer]]
[[s_slashes_to_prover]]
[[s_agent_transfer]]
[[s_is_censored_lambda_function]]