from aztec_gddt.logic import *


AZTEC_MODEL_BLOCKS = [
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
    }
]


PREY_PREDATOR_MODEL_BLOCKS = [block for block in AZTEC_MODEL_BLOCKS
                              if block.get('ignore', False) is False]