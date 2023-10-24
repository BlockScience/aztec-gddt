from aztec_gddt.params import SINGLE_RUN_PARAMS, INITIAL_STATE, TIMESTEPS, SAMPLES
from aztec_gddt.structure import CONSENSUS_PLEDGE_DEMO_BLOCKS

default_run_args = (INITIAL_STATE,
                     {k: [v] for k, v in SINGLE_RUN_PARAMS.items()},
                    CONSENSUS_PLEDGE_DEMO_BLOCKS,
                    TIMESTEPS,
                    SAMPLES)