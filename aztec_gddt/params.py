from aztec_gddt.types import *
from uuid import uuid4
from scipy.stats import norm  # type: ignore

TIMESTEPS = 5  # HACK
SAMPLES = 1  # HACK

N_INITIAL_AGENTS = 3

INITIAL_AGENTS: list[Agent] = [Agent(uuid=uuid4(),
                                     balance=max(norm.rvs(200, 100), 1),
                                     is_sequencer=True,
                                     is_prover=True,
                                     is_relay=False,
                                     staked_amount=0.0)
                               for i
                               in range(N_INITIAL_AGENTS)]

AGENTS_DICT: dict[AgentUUID, Agent] = {a.uuid: a for a in INITIAL_AGENTS}

INITIAL_STATE = AztecModelState(time_l1=0,
                                delta_l1_blocks=0,

                                agents=AGENTS_DICT,
                                current_process=None,
                                proposals=dict(),

                                gas_fee_l1=30,
                                gas_fee_blob=30,

                                finalized_blocks_count=0
                                )

# HACK: Gas is 1 for all transactions
GAS_ESTIMATORS = L1GasEstimators(
    proposal=lambda _: 1,
    commitment_bond=lambda _: 1,
    content_reveal=lambda _: 1,
    content_reveal_blob=lambda _: 1,
    rollup_proof=lambda _: 1
)


# NOTE: I set the default parameters below to be completely arbitrary. - Ock, 11/29
SINGLE_RUN_PARAMS = AztecModelParams(label='default',
                                     timestep_in_blocks=1,

                                     uncle_count=0,

                                     # Phase Durations
                                     phase_duration_proposal=5,
                                     phase_duration_reveal=5,
                                     phase_duration_commit_bond=5,
                                     phase_duration_rollup=25,
                                     phase_duration_finalize=3,
                                     phase_duration_race=25,

                                     stake_activation_period=40,
                                     unstake_cooldown_period=40,


                                     # Behavioral Parameters
                                     proposal_probability_per_user_per_block=0.1,
                                     block_content_reveal_probability=0.5,  # ~97% reveal per 5 block
                                     tx_proof_reveal_probability=0.15,  # tx_proofs do not have to be revealed in v1
                                     rollup_proof_reveal_probability=0.1,
                                     commit_bond_reveal_probability=0.4,
                                     gas_estimators=GAS_ESTIMATORS)  # P=92% over 4B
