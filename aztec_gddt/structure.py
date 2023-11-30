from aztec_gddt.logic import *
from typing import Callable
from copy import deepcopy

# TODO: Put specific dictionaries in each list below. 

PRE_PHASE = [
]

PROPOSAL_PHASE = [
]

COMMITMENT_BOND_PHASE = [
]

REVEAL_PHASE = [
]

PROVING_PHASE = [
]

FINALIZATION_PHASE = [
]

# Combine all of the separate blocks into one. 
AZTEC_MODEL_BLOCKS = sum([PRE_PHASE, 
                  PROPOSAL_PHASE,
                  COMMITMENT_BOND_PHASE,
                  REVEAL_PHASE, 
                  PROVING_PHASE,
                  FINALIZATION_PHASE])

# NOTE: Original Structure, Perhaps We Will Return To It? 
# AZTEC_MODEL_BLOCKS: list[dict] = [
#    {
#        'label': 'Time Tracking',
#        'ignore': False,
#        'desc': 'Updates the time in the system',
#        'policies': {
#            'evolve_time': p_evolve_time
#        },
#        'variables': {
#            'block_time': s_block_time,
#            'delta_blocks': s_delta_blocks
#        }
#    },
#    {
#        'label': 'Block Process',
#        'ignore': False,
#        'policies': {
#            'init_process': p_init_process,
#            'select_sequencer': p_select_proposal,
#            'reveal_block_content': p_reveal_content,
#            'commit_block_proof': p_commit_bond,
#            'submit_block_proof': p_submit_proof,
#            'finalize_block': p_finalize_block,
#            'submit_block_proof_content_race': p_race_mode
#        },
#        'variables': {
#            'process': s_process
#        }
#    }
# ]


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
