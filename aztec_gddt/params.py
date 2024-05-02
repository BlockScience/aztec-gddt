from aztec_gddt.types import *
from uuid import uuid4
from scipy.stats import norm  # type: ignore
import numpy as np
import pandas as pd

from typing import List

# Note: For numpy 1.26 and above, random calls go through a generator.
rng = np.random.default_rng()

L1_BUFFER = 10 # To check timesteps -> L1_timesteps issue
TIMESTEPS = 1_000  # Used mostly for single runs
SAMPLES = 1  # Used mostly for single runs

N_INITIAL_AGENTS = 3

BASE_AGENTS = [
    Agent(
        uuid="relay",
        balance=0,  # type: Tokens
        is_sequencer=False,
        is_prover=False,
        is_relay=True,
        staked_amount=0.0,  # type: Tokens
    ),
    Agent(
        uuid="l1-builder",
        balance=0,  # type: Tokens
        is_sequencer=False,
        is_prover=False,
        is_relay=False,
        staked_amount=0.0,  # type: Tokens
    ),
    Agent(
        uuid="burnt",
        balance=0,  # type: Tokens
        is_sequencer=False,
        is_prover=False,
        is_relay=False,
        staked_amount=0.0,  # type: Tokens
    )
]


BASE_AGENTS_DICT = {a.uuid: a for a in BASE_AGENTS}

# Note: Used mostly for single runs
INITIAL_AGENTS: list[Agent] = [
    Agent(
        uuid=uuid4(),
        # balance=max(norm.rvs(50, 20), 1),
        balance=100,
        is_sequencer=True,
        is_prover=True,
        is_relay=False,
        staked_amount=50,
    )
    for i in range(N_INITIAL_AGENTS)
]

INITIAL_AGENTS_DICT: dict[AgentUUID, Agent] = {
    a.uuid: a for a in INITIAL_AGENTS}

AGENTS_DICT = {**BASE_AGENTS_DICT, **INITIAL_AGENTS_DICT}


INITIAL_CUMM_REWARDS = 200.0  # Assumption # type: Tokens
INITIAL_CUMM_CASHBACK = 00.0  # Assumption # type: Tokens
INITIAL_CUMM_BURN = 50.0  # Assumption # type: Tokens

INITIAL_SUPPLY = TokenSupply(
    circulating=sum(a.balance for a in INITIAL_AGENTS),
    staked=sum(a.staked_amount for a in INITIAL_AGENTS),
    burnt=INITIAL_CUMM_BURN,
    issued=INITIAL_CUMM_REWARDS + INITIAL_CUMM_CASHBACK,
)


SLASH_PARAMS = SlashParameters(
    failure_to_commit_bond=2, failure_to_reveal_block=1  # Assumption # type: Tokens
)


INITIAL_STATE = AztecModelState(
    timestep=0,
    substep=0,
    time_l1=0,
    delta_l1_blocks=0,
    advance_l1_blocks=0,
    slashes_to_provers=0.0,
    slashes_to_sequencers=0.0,
    total_rewards_provers=0.0,  # type: Tokens
    total_rewards_relays=0.0,  # type: Tokens
    total_rewards_sequencers=0.0,  # type: Tokens
    agents=AGENTS_DICT,
    current_process=None,  # Note: Used to start without an ongoing L2 block process
    transactions=dict(),
    gas_fee_l1=50,  # type: Gwei # Assumption
    gas_fee_blob=30,  # type: Gwei # Assumption: In reality likely much lower, but must be tuned. Goes per MB, not per blob currently
    finalized_blocks_count=0,
    cumm_block_rewards=INITIAL_CUMM_REWARDS,
    cumm_fee_cashback=INITIAL_CUMM_CASHBACK,
    cumm_burn=INITIAL_CUMM_BURN,
    token_supply=INITIAL_SUPPLY,
)

INITIAL_STATE['token_supply'] = TokenSupply.from_state(INITIAL_STATE)

#############################################################
## Begin: Steady state gas estimators defined              ##
#############################################################

MEAN_STEADY_STATE_L1 = 50  # type: Gwei
DEVIATION_STEADY_STATE_L1 = 5
MEAN_STEADY_STATE_BLOB = 30  # type: Gwei
DEVIATION_STEADY_STATE_BLOB = 5

# Note: Rounding is needed to address the fact that Gas is an integer type.
steady_gas_fee_l1_time_series = np.array(
    [
        max(floor(el), 10)
        for el in rng.standard_normal(TIMESTEPS) * DEVIATION_STEADY_STATE_L1
        + MEAN_STEADY_STATE_L1  # DEVIATION_STEADY_STATE_L1
    ]
)
steady_gas_fee_blob_time_series = np.array(
    [
        max(floor(el), 10)
        for el in rng.standard_normal(TIMESTEPS) * DEVIATION_STEADY_STATE_BLOB
        + MEAN_STEADY_STATE_BLOB
    ]
)


def steady_state_l1_gas_estimate(state: AztecModelState):
    if state["timestep"] < len(steady_gas_fee_l1_time_series):
        return steady_gas_fee_l1_time_series[state["timestep"]]
    else:
        return steady_gas_fee_l1_time_series[-1]


def steady_state_blob_gas_estimate(state: AztecModelState):
    if state["timestep"] < len(steady_gas_fee_blob_time_series):
        return steady_gas_fee_blob_time_series[state["timestep"]]
    else:
        return steady_gas_fee_blob_time_series[-1]


#############################################################
## End: Steady state gas estimators defined                ##
#############################################################

#############################################################
## Begin: single shock gas estimators defined              ##
#############################################################


# NOTE: ideally, this should be mapped either to relative timesteps or L1 time rather than fixed timesteps
# so that the scenarios are invariant to number
L1_SHOCK_AMOUNT = 150  # type: Gwei
BLOB_SHOCK_AMOUNT = 150  # type: Gwei
initial_time = floor(0.25 * TIMESTEPS)  # Assumption: 25% of timesteps
final_time = floor(0.25 * TIMESTEPS)  # Assumption: 25% of timesteps


single_shock_gas_fee_l1_time_series = np.zeros(TIMESTEPS)
single_shock_gas_fee_blob_time_series = np.zeros(TIMESTEPS)

single_shock_gas_fee_l1_time_series[0:initial_time] = steady_gas_fee_l1_time_series[
    0:initial_time
].copy()
single_shock_gas_fee_l1_time_series[-final_time:] = steady_gas_fee_l1_time_series[
    -final_time:
].copy()
single_shock_gas_fee_l1_time_series[initial_time: TIMESTEPS - final_time] = (
    steady_gas_fee_l1_time_series[initial_time: TIMESTEPS - final_time].copy()
    + L1_SHOCK_AMOUNT
)

single_shock_gas_fee_blob_time_series[0:initial_time] = steady_gas_fee_blob_time_series[
    0:initial_time
].copy()
single_shock_gas_fee_blob_time_series[-final_time:] = steady_gas_fee_blob_time_series[
    -final_time:
].copy()
single_shock_gas_fee_blob_time_series[initial_time: TIMESTEPS - final_time] = (
    steady_gas_fee_blob_time_series[initial_time: TIMESTEPS -
                                    final_time].copy()
    + L1_SHOCK_AMOUNT
)

#############################################################
## End: single shock gas estimators defined                ##
#############################################################

#############################################################
## Begin: intermittent shock gas estimators defined        ##
#############################################################

L1_INTER_SHOCK_AMPLITUDE = 100  # Amplitude of wave
L1_INTER_SHOCK_PERIOD = 10  # Period of wave
num_points = (TIMESTEPS - final_time) - initial_time
t = np.arange(initial_time, initial_time + num_points)

raw_shock_signal = (
    L1_INTER_SHOCK_AMPLITUDE * np.sin(2 * np.pi * t / L1_INTER_SHOCK_PERIOD)
    + L1_INTER_SHOCK_AMPLITUDE
)
L1_INTER_SHOCK_SIGNAL = np.array([floor(max(x, 1)) for x in raw_shock_signal])


intermit_shock_gas_fee_l1_time_series = np.zeros(TIMESTEPS)
intermit_shock_gas_fee_blob_time_series = np.zeros(TIMESTEPS)

intermit_shock_gas_fee_l1_time_series[0:initial_time] = steady_gas_fee_l1_time_series[
    0:initial_time
].copy()
intermit_shock_gas_fee_l1_time_series[-final_time:] = steady_gas_fee_l1_time_series[
    -final_time:
].copy()
intermit_shock_gas_fee_l1_time_series[initial_time: TIMESTEPS - final_time] = (
    steady_gas_fee_l1_time_series[initial_time: TIMESTEPS - final_time].copy()
    + L1_INTER_SHOCK_SIGNAL
)


GAS_FEE_L1_TIME_SERIES_LIST = [
    steady_gas_fee_l1_time_series,
    intermit_shock_gas_fee_l1_time_series,
    single_shock_gas_fee_l1_time_series,
]
GAS_FEE_BLOB_TIME_SERIES_LIST = [
    steady_gas_fee_blob_time_series,
    intermit_shock_gas_fee_blob_time_series,
    single_shock_gas_fee_blob_time_series,
]


#############################################################
## End: intermittent shock gas estimators defined        ##
#############################################################

# HACK: Gas is 1 for all transactions
DEFAULT_DETERMINISTIC_TX_ESTIMATOR = UserTransactionEstimators(
    transaction_count=lambda _: 1,  # type: ignore
    proposal_average_size=lambda _: 100,  # type: ignore
    transaction_average_fee_per_size=lambda _: 50.5,  # type: ignore
)


DEFAULT_DETERMINISTIC_GAS_ESTIMATOR = L1GasEstimators(
    proposal=lambda _: 100_000,  # type: ignore
    commitment_bond=lambda _: 100_000,  # type: ignore
    content_reveal=lambda _: 81_000,  # type: ignore
    content_reveal_blob=lambda _: 500_000,  # type: ignore
    rollup_proof=lambda _: 700_000  # type: ignore
)


#################################################
## Begin censorship time series information    ## 
################################################

ALWAYS_TRUE_SERIES = [True] * (L1_BUFFER * TIMESTEPS)
ALWAYS_FALSE_SERIES = [False] * (L1_BUFFER * TIMESTEPS)

def build_censor_series_from_role(data: pd.DataFrame,
                        censor_list: List[str] = None, 
                        start_time: int = None,
                        num_timesteps: int = 1000, 
                        role: str = None):

    sorted_data = data.sort_values(by='date')

    # HACK: Currently we have hard-coded timestep limits. 
    if num_timesteps > 1000:
        Exception("Currently all simulation runs must be 1000 timesteps or less.")

    if start_time is None:
        start_time = random.randint(0, length - number_of_timesteps)

    if censor_list is None:
        censor_list = []

    index_range_to_use = [x for x in range(start_time, start_time + num_timesteps)]
    indexed_data = data.iloc[index_range_to_use]
    censored_series = indexed_data[role].apply(lambda x: x in censor_list).to_list()

    return censored_series
    

def build_censor_params(data: pd.DataFrame, 
                        censoring_builders: List[str],
                        censoring_validators: List[str],
                        start_time: int = None,
                        num_timesteps:int = 1000):

    practical_num_timesteps = L1_BUFFER * num_timesteps

    if start_time is None:
        data_length = len(data)
        start_time = random.randint(0, data_length - (practical_num_timesteps + 1))
    
    # XXX: Currently doubling number of timesteps due to weird out-of-range errors on long runs. 

    censorship_builder_data = build_censor_series_from_role(data = data,
                                                           censor_list = censoring_builders,
                                                           start_time = start_time,
                                                           num_timesteps = practical_num_timesteps,
                                                           role = 'builder')
    censorship_validator_data = build_censor_series_from_role(data = data,
                                                           censor_list = censoring_validators,
                                                           start_time = start_time,
                                                           num_timesteps = practical_num_timesteps,
                                                           role = 'validator')

    censorship_info_dict = {"censorship_series_builder": [censorship_builder_data],
                   "censorship_series_validator": [censorship_validator_data]}

    return censorship_info_dict



#################################################
## End censorship time series information     ## 
################################################



SINGLE_RUN_PARAMS = AztecModelParams(
    label="default",
    timestep_in_blocks=1,
    uncle_count=0,
    fee_subsidy_fraction=1.0,  # unused
    minimum_stake=30,  # Assumption: Min Stake, where Sequencers try to top-up if they fall below after slashing
    l1_blocks_per_day=int(24 * 60 * 60 / 12.08),
    daily_block_reward=32,
    # Placeholder Logic
    logic={},
    # Phase Durations
    phase_duration_proposal_min_blocks=0,  # Assumption: Sweeping sets upper bound and lower bound per upper bound for fixed / dynamic
    phase_duration_proposal_max_blocks=10,  # Assumption
    phase_duration_reveal_min_blocks=0,  # Assumption
    phase_duration_reveal_max_blocks=10,  # Assumption
    phase_duration_commit_bond_min_blocks=0,  # Assumption
    phase_duration_commit_bond_max_blocks=10,  # Assumption
    phase_duration_rollup_min_blocks=0,  # Assumption
    phase_duration_rollup_max_blocks=30,  # Assumption
    phase_duration_race_min_blocks=0,  # Assumption
    phase_duration_race_max_blocks=30,  # Assumption

    stake_activation_period=40,  # Assumption: Currently not impactful
    unstake_cooldown_period=40,  # Assumption: Currently not impactful
    # Behavioral Parameters
    final_probability=0.99,
    gas_threshold_for_tx=250,  # Assumption: We want to set a censorship level for gas prices (which we could create a timeseries with too)
    blob_gas_threshold_for_tx=250,  # Assumption: We want to set a censorship level for blob gas prices (which we could create a timeseries with too)
    proving_marketplace_usage_probability=0.7,  # Assumption: Global Probability, could instantiate agents with [0, 1]
    
    rewards_to_provers=0.3,  # Assumption: Reward Share
    rewards_to_relay=0.01,  # Assumption: Reward Share

    censorship_series_builder = ALWAYS_FALSE_SERIES,  # Iniital Assumptions: No Censorship
    censorship_series_validator = ALWAYS_FALSE_SERIES, # Iniital Assumption: No Censorship

    gwei_to_tokens=1e-9,
    gas_estimators=DEFAULT_DETERMINISTIC_GAS_ESTIMATOR,
    tx_estimators=DEFAULT_DETERMINISTIC_TX_ESTIMATOR,
    slash_params=SLASH_PARAMS,
    gas_fee_l1_time_series=GAS_FEE_L1_TIME_SERIES_LIST[-1],
    gas_fee_blob_time_series=GAS_FEE_BLOB_TIME_SERIES_LIST[-1],
    commit_bond_amount=16.0,  # type: Tokens
    op_cost_sequencer=0,  # Assumption: Currently all Sequencers have one op_cost constant to evaluate against
    op_cost_prover=0, # Assumption: Currently all Provers have one op_cost constant to evaluate against
    safety_factor_commit_bond = 0.0,
    safety_factor_reveal_content = 0.0,
    safety_factor_rollup_proof = 0.0,
    past_gas_weight_fraction = 0.9
)

