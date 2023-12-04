from aztec_gddt.types import *
from uuid import uuid4
from scipy.stats import norm  # type: ignore

TIMESTEPS = 5  # TODO
SAMPLES = 1  # TODO

N_INITIAL_USERS = 3

INITIAL_INTERACTING_USERS = [Sequencer(i, max(norm.rvs(200, 100), 1))
                             for i
                             in range(N_INITIAL_USERS)]

# TODO: Set default values for initial state. - Ock, 11/29
INITIAL_STATE = AztecModelState(time_l1=0,
                                delta_l1_blocks=0,
                                finalized_blocks_count=0,
                                interacting_users=INITIAL_INTERACTING_USERS,
                                current_process=None,
                                proposals=[],
                                events=[])

# NOTE: I set the default parameters below to be completely arbitrary. - Ock, 11/29
SINGLE_RUN_PARAMS = AztecModelParams(label='default',
                                     timestep_in_blocks=1,
                                     uncle_count=0,
                                     phase_duration_proposal=3,
                                     phase_duration_reveal=3,
                                     phase_duration_commit_bond=3,
                                     phase_duration_rollup=3,
                                     phase_duration_finalize=3,
                                     phase_duration_race=3,
                                     stake_activation_period=10,
                                     unstake_cooldown_period=5,
                                     proposal_probability_per_user_per_block=0.1,
                                     block_content_reveal_probability=0.1,
                                     tx_proof_reveal_probability=0.15,
                                     rollup_proof_reveal_probability=0.2,
                                     commit_bond_reveal_probability=0.25)
