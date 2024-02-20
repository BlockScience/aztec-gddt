from aztec_gddt.types import *
from uuid import uuid4
from scipy.stats import norm  # type: ignore

TIMESTEPS = 1000  # HACK
SAMPLES = 1  # HACK

N_INITIAL_AGENTS = 3

 # XXX
INITIAL_AGENTS: list[Agent] = [Agent(uuid=uuid4(),
                                     balance=max(norm.rvs(50, 20), 1),
                                     is_sequencer=True,
                                     is_prover=True,
                                     is_relay=False,
                                     staked_amount=5)
                               for i
                               in range(N_INITIAL_AGENTS)]

# Relay Agent
INITIAL_AGENTS.append(Agent(uuid='relay',
                            balance=0,
                            is_sequencer=False,
                            is_prover=False,
                            is_relay=True,
                            staked_amount=0.0))


# L1 Builder Agent
INITIAL_AGENTS.append(Agent(uuid='l1-builder',
                            balance=0,
                            is_sequencer=False,
                            is_prover=False,
                            is_relay=False,
                            staked_amount=0.0))


# Burn sink
INITIAL_AGENTS.append(Agent(uuid='burnt',
                            balance=0,
                            is_sequencer=False,
                            is_prover=False,
                            is_relay=False,
                            staked_amount=0.0))

AGENTS_DICT: dict[AgentUUID, Agent] = {a.uuid: a for a in INITIAL_AGENTS}

INITIAL_CUMM_REWARDS = 200 # XXX
INITIAL_CUMM_CASHBACK = 50 # XXX
INITIAL_CUMM_BURN = 50 # XXX
INITIAL_SUPPLY = TokenSupply(
    circulating=sum(a.balance for a in INITIAL_AGENTS),
    staked=sum(a.staked_amount for a in INITIAL_AGENTS),
    burnt=INITIAL_CUMM_BURN,
    issued=INITIAL_CUMM_REWARDS+INITIAL_CUMM_CASHBACK
)


SLASH_PARAMS = SlashParameters(
    failure_to_commit_bond=2, # XXX
    failure_to_reveal_block=1 # XXX
)


INITIAL_STATE = AztecModelState(time_l1=0,
                                delta_l1_blocks=0,
                                advance_l1_blocks=0,

                                agents=AGENTS_DICT,
                                current_process=None, # XXX
                                transactions=dict(),

                                gas_fee_l1=50, # XXX
                                gas_fee_blob=7, # XXX

                                finalized_blocks_count=0,
                                cumm_block_rewards=INITIAL_CUMM_REWARDS,
                                cumm_fee_cashback=INITIAL_CUMM_CASHBACK,
                                cumm_burn=INITIAL_CUMM_BURN,
                                token_supply=INITIAL_SUPPLY
                                )

GAS_ESTIMATORS = L1GasEstimators(
    proposal=lambda _: 100_000,
    commitment_bond=lambda _: 100_000,
    content_reveal=lambda _: 81_000,
    content_reveal_blob=lambda _: 500_000, # NOTE: this is a HACK assumption, gas was estimated from various documents by Aztec Labs
    rollup_proof=lambda _: 450_000
)

# HACK: Gas is 1 for all transactions
TX_ESTIMATORS = UserTransactionEstimators(
    transaction_count=lambda _: 1,
    proposal_average_size=lambda _: 100,
    transaction_average_fee_per_size=lambda _: 50.5
)


SINGLE_RUN_PARAMS = AztecModelParams(label='default',
                                     timestep_in_blocks=1,

                                     uncle_count=0, # TODO
                                     reward_per_block=1.0, # TODO
                                     fee_subsidy_fraction=1.0, # TODO

                                     # Phase Durations
                                     phase_duration_proposal=10, # TODO
                                     phase_duration_reveal_min_blocks=0, # TODO
                                     phase_duration_reveal_max_blocks = 10, # TODO
                                     phase_duration_commit_bond=10, # TODO
                                     phase_duration_rollup=30, # TODO
                                     phase_duration_race=30, # TODO

                                     stake_activation_period=40, # TODO
                                     unstake_cooldown_period=40, # TODO


                                     # Behavioral Parameters
                                     proposal_probability_per_user_per_block=0.2, # XXX
                                     block_content_reveal_probability=0.2, # XXX
                                     tx_proof_reveal_probability=0.2, # XXX
                                     rollup_proof_reveal_probability=0.2, # XXX
                                     commit_bond_reveal_probability=0.2, # XXX
                                     gas_threshold_for_tx=70, # HACK
                                     blob_gas_threshold_for_tx=50, # HACK
                                     proving_marketplace_usage_probability=0.3, # XXX
                                     
                                     rewards_to_provers=0.3, # XXX
                                     rewards_to_relay=0.01, # XXX

                                     gwei_to_tokens=1e-9, 

                                     gas_estimators=GAS_ESTIMATORS,
                                     tx_estimators=TX_ESTIMATORS,
                                     slash_params=SLASH_PARAMS,
                                     commit_bond_amount = 10.0
                                     
                                     )  
