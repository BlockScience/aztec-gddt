## Code

{
        'label': 'Agent Actions',
        'ignore' : False, 
        'policies': {
            # Potential Change: Possibly add policies for the users triggering the relevant events
            # eg. making the proofs public
        },
        'variables': {
            'transactions': s_transactions_new_proposals,
            'agents': s_agent_restake
            # Potential Change: Possibly add a SUF for updating toggling the event
            # bools in the current process
        }
    },

## Policies

## State Updates

[[s_transactions_new_proposals]]
[[s_agent_restake]]