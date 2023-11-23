from aztec_gddt.types import *

TIMESTEPS = 5  # TODO
SAMPLES = 1  # TODO

INITIAL_STATE = AztecModelState(block_time=0,
                                delta_blocks=0)

SINGLE_RUN_PARAMS = AztecModelParams(label='default',
                                     timestep_in_blocks=1)
