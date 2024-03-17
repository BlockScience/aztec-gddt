from pandas import DataFrame # type: ignore
from typing import Dict, List


from cadCAD.tools.preparation import sweep_cartesian_product # type: ignore

from aztec_gddt.params import INITIAL_STATE
from aztec_gddt.params import SINGLE_RUN_PARAMS, TIMESTEPS, BASE_AGENTS_DICT
from aztec_gddt.params import *
from aztec_gddt.structure import AZTEC_MODEL_BLOCKS
from aztec_gddt.types import AztecModelParams, AztecModelState, Agent
from uuid import uuid4
from scipy.stats import norm # type: ignore
from aztec_gddt.utils import sim_run
from typing import Optional
from random import sample




def standard_run(N_timesteps=TIMESTEPS) -> DataFrame:
    """Function which runs the cadCAD simulations

    Returns:
        DataFrame: A dataframe of simulation data
    """
    # The number of timesteps for each simulation to run
    

    # The number of monte carlo runs per set of parameters tested
    N_samples = 1
    # %%
    # Get the sweep params in the form of single length arrays
    sweep_params = {k: [v] for k, v in SINGLE_RUN_PARAMS.items()}

    # Load simulation arguments
    sim_args = (INITIAL_STATE,
                sweep_params,
                AZTEC_MODEL_BLOCKS,
                N_timesteps,
                N_samples)

    # Run simulation
    sim_df = sim_run(*sim_args)
    return sim_df

def custom_run(initial_state: Optional[AztecModelState] = None,
               default_params: Optional[AztecModelParams] = None,
               params_to_modify: Optional[Dict[str,List]] = None,
               model_blocks: Optional[list[dict]] = None,
               N_timesteps:int = TIMESTEPS,
               N_samples:int = 1) -> DataFrame:
    """
    Function to run a custom cadCAD simulation

    Args:
        initial_state (AztecModelState): The initial state for the simulation
        default_params (AztecModelParams): The default parameters to use. 
        params_to_sweep (Dict[str, List]): The parameters to sweep during the simulation
        model_blocks (list[dict]): The model blocks for the simulation
        N_timesteps (int): Number of timesteps to run the simulation
        N_samples (int): Number of Monte Carlo runs to perform

    Returns:
        DataFrame: A dataframe of simulation data
    """ 
    # Set default values.

    if initial_state is None:
        initial_state = INITIAL_STATE
    if default_params is None:
        default_params = SINGLE_RUN_PARAMS
    if model_blocks is None:
        model_blocks = AZTEC_MODEL_BLOCKS


     # Begin by copying the indicated default settings. 
    sweep_params = {k: [v] for k, v in default_params.items()}

    if params_to_modify is not None:
        # Modify the parameters that need to be modified. 
        for k,v in params_to_modify.items():
            sweep_params[k] = v
            # if isinstance(v, list):
            #     sweep_params[k] = v
            # else:
            #     sweep_params[k] = [v]
            # Load simulation arguments
    else:
        pass

    sim_args = (initial_state,
                sweep_params,
                model_blocks,
                N_timesteps,
                N_samples)

    # Run simulation
    sim_df = sim_run(*sim_args)
    return sim_df
    



def psuu_exploratory_run(N_sweep_samples=720, N_samples=3, N_timesteps=500) -> DataFrame:
    """Function which runs the cadCAD simulations

    Returns:
        DataFrame: A dataframe of simulation data
    """

    # Relay Agent
    Sqn3Prv3_agents = []
    N_sequencer = 3
    N_prover = 3

    for i in range(N_sequencer):
        a = Agent(uuid=uuid4(),
                                     balance=max(norm.rvs(50, 20), 1),
                                     is_sequencer=True,
                                     is_prover=False,
                                     is_relay=False,
                                     staked_amount=5)
        Sqn3Prv3_agents.append(a)
    for i in range(N_prover):
        a = Agent(uuid=uuid4(),
                                     balance=max(norm.rvs(50, 20), 1),
                                     is_sequencer=False,
                                     is_prover=True,
                                     is_relay=False,
                                     staked_amount=5)
        Sqn3Prv3_agents.append(a)

    
    Sqn3Prv3_dict = {a.uuid: a for a in Sqn3Prv3_agents}
    Sqn3Prv3 = {**BASE_AGENTS_DICT, **Sqn3Prv3_dict}


    initial_state = AztecModelState(
        time_l1=0,
        delta_l1_blocks=0,
        advance_l1_blocks=0,

        agents=Sqn3Prv3,

        current_process=None,
        transactions=dict(),

        gas_fee_l1=float('nan'),
        gas_fee_blob=float('nan'),

        finalized_blocks_count=0,
        cumm_block_rewards=INITIAL_CUMM_REWARDS,
        cumm_fee_cashback=INITIAL_CUMM_CASHBACK,
        cumm_burn=INITIAL_CUMM_BURN,

        token_supply=INITIAL_SUPPLY
    )



    sweep_params: dict[str, list] = dict(label=['default'],
                                        timestep_in_blocks=[1],

                                        uncle_count=[0], # TODO
                                        reward_per_block=[1.0], # HACK: consider alternate values
                                        fee_subsidy_fraction=[1.0], # TODO

                                        # Phase Durations
                                        phase_duration_proposal_min_blocks=[0, 3],# HACK: consider alternate values
                                        phase_duration_proposal_max_blocks=[3, 12], 
                                        phase_duration_reveal_min_blocks = [0, 3],# HACK: consider alternate values
                                        phase_duration_reveal_max_blocks = [3, 24], 
                                        phase_duration_commit_bond_min_blocks = [0, 3], # HACK: consider alternate values
                                        phase_duration_commit_bond_max_blocks=[3, 12], 
                                        phase_duration_rollup_min_blocks = [0, 3], # HACK: consider alternate values
                                        phase_duration_rollup_max_blocks=[15, 80],
                                        phase_duration_race_min_blocks = [0, 3], # HACK: consider alternate values 
                                        phase_duration_race_max_blocks=[3, 6], 

                                        stake_activation_period=[40], # TODO
                                        unstake_cooldown_period=[40], # TODO

                                        logic=[{}],


                                        # Behavioral Parameters
                                        proposal_probability_per_user_per_block=[0.1],
                                        block_content_reveal_probability=[0.01, 0.5], 
                                        tx_proof_reveal_probability=[0.01, 0.5], 
                                        rollup_proof_reveal_probability=[0.01, 0.5],
                                        commit_bond_reveal_probability=[0.01, 0.5], 


                                        gas_threshold_for_tx=[50], 
                                        blob_gas_threshold_for_tx=[50], 
                                        proving_marketplace_usage_probability=[0.0],
                                        
                                        rewards_to_provers=[0.5],
                                        rewards_to_relay=[0.0],

                                        gwei_to_tokens=[1e-9], 

                                        gas_estimators=[DEFAULT_DETERMINISTIC_GAS_ESTIMATOR],
                                        tx_estimators=[DEFAULT_DETERMINISTIC_TX_ESTIMATOR],
                                        slash_params=[SLASH_PARAMS],
                                        gas_fee_l1_time_series=GAS_FEE_L1_TIME_SERIES_LIST,
                                        gas_fee_blob_time_series=GAS_FEE_BLOB_TIME_SERIES_LIST,

                                        commit_bond_amount = [10.0], # HACK: consider alternate values
                                        op_costs=[0.0] # XXX
                                        )  
    



    combinations = 1
    for v in sweep_params.values():
        combinations *= len(v)
    combinations *= N_samples
    print(combinations)

    

    sweep_params_cartesian_product = sweep_cartesian_product(sweep_params)


    sweep_params_cartesian_product = {k: list(v) for k, v in sweep_params_cartesian_product.items()}

    sweep_params_cartesian_product = {k: sample(v, N_sweep_samples) if N_sweep_samples > 0 else v 
                                                               for k, v in sweep_params_cartesian_product.items()}

    # Load simulation arguments
    sim_args = (initial_state,
                sweep_params_cartesian_product,
                AZTEC_MODEL_BLOCKS,
                N_timesteps,
                N_samples)

    print('Performing PSuU run')
    # Run simulation

    assign_params = {'stake_activation_period', 'phase_duration_commit_bond_min_blocks', 'gas_threshold_for_tx', 'op_costs', 'proving_marketplace_usage_probability', 'gas_fee_l1_time_series', 'phase_duration_reveal_min_blocks', 'gwei_to_tokens', 'slash_params', 'gas_fee_blob_time_series', 'phase_duration_proposal_max_blocks', 'rewards_to_relay', 'phase_duration_rollup_max_blocks', 'phase_duration_rollup_min_blocks', 'phase_duration_reveal_max_blocks', 'fee_subsidy_fraction', 'phase_duration_race_min_blocks', 'timestep_in_blocks', 'rewards_to_provers', 'label', 'reward_per_block', 'blob_gas_threshold_for_tx', 'phase_duration_race_max_blocks', 'unstake_cooldown_period', 'proposal_probability_per_user_per_block', 'block_content_reveal_probability', 'commit_bond_reveal_probability', 'phase_duration_commit_bond_max_blocks', 'commit_bond_amount', 'uncle_count', 'tx_proof_reveal_probability', 'rollup_proof_reveal_probability', 'phase_duration_proposal_min_blocks'}

    sim_df = sim_run(*sim_args, exec_mode='single', assign_params=assign_params)
    return sim_df