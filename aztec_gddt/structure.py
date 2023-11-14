from aztec_gddt.logic import *
from typing import Callable
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
            'block_time': s_block_time,
            'delta_blocks': s_delta_blocks
        }
    },
    {
        'label': 'Advance Block Process Phases',
        'policies': {
            'init_process': p_init_process,
            'select_sequencer': p_select_sequencer,
            'reveal_block_content': None,
            'reveal_block_proofs': None,
            'finalize_block': None
        },
        'variables': {
            'processes': s_processes
        }
    },
    {
        'label': 'Handle L2 reorgs'
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