from aztec_gddt.types import *

TIMESTEPS = 5  # TODO
SAMPLES = 1  # TODO

# TODO: Set default values for initial state. - Ock, 11/29
INITIAL_STATE = AztecModelState(block_time=0,
                                delta_blocks=0)

# NOTE: I set the default parameters below to be completely arbitrary. - Ock, 11/29
SINGLE_RUN_PARAMS = AztecModelParams(label='default',
                                     timestep_in_blocks=1,
                                     uncle_count = 0,
                                     phase_duration_proposal = 1,
                                     phase_duration_reveal = 1,
                                     phase_duration_commit_bond = 1,
                                     phase_duration_rollup = 1,
                                     phase_duration_finalize = 1,
                                     phase_duration_race = 1,
                                     stake_activation_period = 10,
                                     unstake_cooldown_period = 5,
                                     block_content_reveal_probability = 0.1,
                                     tx_proof_reveal_probability = 0.15,
                                     rollup_proof_reveal_probability = 0.2,
                                     commit_bond_reveal_probability = 0.25)
