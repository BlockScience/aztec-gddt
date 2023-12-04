from aztec_gddt.types import *

TIMESTEPS = 5  # TODO
SAMPLES = 1  # TODO

# TODO: Set default values for initial state. - Ock, 11/29
INITIAL_STATE = AztecModelState(time_l1=0,
                                delta_l1_blocks=0,
                                finalized_blocks_count=0,
                                interacting_users=[],
                                current_process=None,
                                proposals=[],
                                events=[])

# NOTE: I set the default parameters below to be completely arbitrary. - Ock, 11/29
SINGLE_RUN_PARAMS = AztecModelParams(label='default',
                                     timestep_in_blocks=1,
                                     uncle_count = 0,
                                     phase_duration_proposal = 3,
                                     phase_duration_reveal = 3,
                                     phase_duration_commit_bond = 3,
                                     phase_duration_rollup = 3,
                                     phase_duration_finalize = 3,
                                     phase_duration_race = 3,
                                     stake_activation_period = 10,
                                     unstake_cooldown_period = 5,
                                     block_content_reveal_probability = 0.1,
                                     tx_proof_reveal_probability = 0.15,
                                     rollup_proof_reveal_probability = 0.2,
                                     commit_bond_reveal_probability = 0.25)
