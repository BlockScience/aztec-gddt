from aztec_gddt.types import *
from uuid import uuid4
from scipy.stats import norm  # type: ignore

TIMESTEPS = 5  # TODO
SAMPLES = 1  # TODO

N_INITIAL_USERS = 3

INITIAL_INTERACTING_USERS = [Agent(uuid=uuid4(),
                                   balance=max(norm.rvs(200, 100), 1),
                                   is_sequencer=True,
                                   is_prover=True,
                                   is_relay=False,
                                   staked_amount=0.0)
                             for i
                             in range(N_INITIAL_USERS)]

# TODO: Set default values for initial state. - Ock, 11/29
INITIAL_STATE = AztecModelState(time_l1=0,
                                delta_l1_blocks=0,
                                finalized_blocks_count=0,
                                agents=INITIAL_INTERACTING_USERS,
                                current_process=None,
                                proposals=[],
                                events=[])

# NOTE: I set the default parameters below to be completely arbitrary. - Ock, 11/29
SINGLE_RUN_PARAMS = AztecModelParams(label='default',
                                     timestep_in_blocks=1,
                                     uncle_count=0,
                                     phase_duration_proposal=5,
                                     phase_duration_reveal=5,
                                     phase_duration_commit_bond=5,
                                     phase_duration_rollup=25,
                                     # left at 3 for now - could merge with rollup proof submission
                                     phase_duration_finalize=3,
                                     # same duration as rollup/proving phase to keep total block time fixed.
                                     phase_duration_race=25,
                                     # TODO: How to keep overall block time fixed if we move to race mode after commit bond phase and skip reveal
                                     stake_activation_period=40,
                                     unstake_cooldown_period=40,
                                     proposal_probability_per_user_per_block=0.1,
                                     # TODO: proposal_probability should depend on the score in v1 already
                                     block_content_reveal_probability=0.5,  # reveals in ~96.9% over 5 L1 blocks
                                     tx_proof_reveal_probability=0.15,  # tx_proofs do not have to be revealed in v1
                                     rollup_proof_reveal_probability=0.1,
                                     # TODO: rollup_proof_reveal if possible, we use a distribution that is much more likely to reveal later during the phase, as Proving takes time
                                     commit_bond_reveal_probability=0.4)  # bond put up with ~92% likelihood over 5 rounds
