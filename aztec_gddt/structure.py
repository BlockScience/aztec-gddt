from aztec_gddt.logic import *
from aztec_gddt.types import *
from copy import deepcopy

AZTEC_MODEL_BLOCKS: list[dict] = [
    {
        'label': 'Time Tracking',
        'ignore': False,
        'desc': 'Updates the time in the system',
        'policies': {
            'evolve_time': p_evolve_time
        },
        'variables': {
            'time_l1': s_block_time,
            'delta_l1_blocks': s_delta_l1_blocks,
            'current_process': s_current_process_time,
        }
    },
    {
        'label': 'Exogenous Processes',
        'policies': {

        },
        'variables': {
            'gas_fee_l1': s_gas_fee_l1,
            'gas_fee_blob': s_gas_fee_blob
        }
    },
    {
        'label': 'Agent Actions',
        'policies': {
            # TODO Possibly add policies for the users triggering the relevant events
            # eg. making the proofs public
        },
        'variables': {
            'transactions': s_transactions_new_proposals
            # TODO Possibly add a SUF for updating toggling the event
            # bools in the current process
        }
    },
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
            'agents': s_agent_transfer
        }
    },
    {
        'label': 'Payouts',
        'policies': {
            'block_reward': p_block_reward,
            'fee_cashback': p_fee_cashback,
            'fee_from_users': p_fee_from_users
        },
        'variables':{
            'agents': s_agents_rewards,
            'cumm_block_rewards': lambda _1,_2,_3,s1,s2: ('cumm_block_rewards', s2['block_reward'] + s1['cumm_block_rewards']),
            'cumm_fee_cashback': lambda _1,_2,_3,s1,s2: ('cumm_fee_cashback', s2['fee_cashback'] + s1['cumm_fee_cashback'])
        }
    },
    {
        'label': 'Dynamically Evolve Time',
        'policies': {
             'conditionally_evolve_time': p_evolve_time_dynamical
        },
        'variables': {
            'time_l1': s_block_time,
            'delta_l1_blocks': s_delta_l1_blocks,
            'current_process': s_current_process_time_dynamical,
            'advance_l1_blocks': s_reset_advance
        }
    },
    {
        'label': 'Metrics',
        'policies': {
        },
        'variables': {
            'token_supply': s_token_supply,
            'finalized_blocks_count': lambda _1, _2, _3, s, _5:  ('finalized_blocks_count', s['finalized_blocks_count'] + 1 if s['current_process'].phase == SelectionPhase.finalized else s['finalized_blocks_count'])
        }
    }
]


blocks: list[dict] = []
for block in [b for b in AZTEC_MODEL_BLOCKS if b.get('ignore', False) != True]:
    _block = deepcopy(block)
    for variable, suf in block.get('variables', {}).items():
        if suf == add_suf:
            _block['variables'][variable] = add_suf(variable)
        elif suf == replace_suf:
            _block['variables'][variable] = replace_suf(variable)
        else:
            pass
    blocks.append(_block)

AZTEC_MODEL_BLOCKS = [block for block in AZTEC_MODEL_BLOCKS
                      if block.get('ignore', False) is False]
