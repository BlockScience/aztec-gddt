from aztec_gddt.logic import *
from typing import Callable
from copy import deepcopy

# Temporary Dictionary Template for Copy-Paste

{
        'label': '',
        'ignore': False,
        'policies': {
        },
        'variables': {
        }
    }

PRE_PHASE:list[dict] = [
        {
        'label': 'Update Interacting Users',
        'ignore': False,
        'policies': {
            'update_interacting_users': p_update_interacting_users
        },
        'variables': {
            'interacting_users': s_interacting_users  
        }
    },
    # Initialize a new process for a new block.
    {
        'label': 'Initialize Process',
        'ignore': False,
        'policies': {
            # TODO
        },
        'variables': {
            # TODO
        }
    }
]

PROPOSAL_PHASE:list[dict] = [
    
]

COMMITMENT_BOND_PHASE:list[dict] = [
]

REVEAL_PHASE: list[dict] = [
]

PROVING_PHASE: list[dict] = [
]

FINALIZATION_PHASE: list[dict] = [
]



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
            'delta_blocks': s_delta_blocks,
            'current_process': s_current_process_time
        }
    },
    {
        'label': 'User Actions',
        'policies': {
        },
        'variables': {
            'proposals': s_proposals
        }
    },
    {
        'label': 'Evolve Block Process',
        'ignore': False,
        'policies': {
            'init_process': p_init_process,
            'select_sequencer': p_select_proposal,
            'reveal_block_content': p_reveal_content,
            'submit_commit_bond': p_commit_bond,
            'submit_block_proof': p_submit_proof,
            'finalize_block': p_finalize_block,
            'submit_block_proof_content_race': p_race_mode
        },
        'variables': {
            'current_process': s_process
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
