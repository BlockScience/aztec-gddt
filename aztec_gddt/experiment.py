from pandas import DataFrame
from typing import Dict, List
from pathlib import Path

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
from datetime import datetime, timedelta
from tqdm.auto import tqdm # type: ignore
from joblib import Parallel, delayed # type: ignore
import logging
from aztec_gddt import DEFAULT_LOGGER
logger = logging.getLogger(DEFAULT_LOGGER)

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
    



def psuu_exploratory_run(N_sweep_samples=-1,
                         N_samples=3,
                         N_timesteps=500,
                         N_jobs=-1,
                         parallelize_jobs=True,
                         supress_cadCAD_print=False,
                         output_path = '',
                         timestep_tensor_prefix='',
                         N_sequencer=10,
                         N_prover=10) -> Optional[DataFrame]:
    """Function which runs the cadCAD simulations

    Returns:
        DataFrame: A dataframe of simulation data
    """
    invoke_time = datetime.now()
    logger.info(f"PSuU Exploratory Run invoked at {invoke_time}")
    # Relay Agent
    Sqn3Prv3_agents = []

    assign_params = {'stake_activation_period', 'phase_duration_commit_bond_min_blocks', 'gas_threshold_for_tx', 'proving_marketplace_usage_probability', 'gas_fee_l1_time_series', 'phase_duration_reveal_min_blocks', 'gwei_to_tokens', 'slash_params', 'gas_fee_blob_time_series', 'phase_duration_proposal_max_blocks', 'rewards_to_relay', 'phase_duration_rollup_max_blocks', 'phase_duration_rollup_min_blocks', 'phase_duration_reveal_max_blocks', 'fee_subsidy_fraction', 'phase_duration_race_min_blocks', 'timestep_in_blocks', 'rewards_to_provers', 'label', 'daily_block_reward', 'blob_gas_threshold_for_tx', 'phase_duration_race_max_blocks', 'unstake_cooldown_period', 'phase_duration_commit_bond_max_blocks', 'commit_bond_amount', 'uncle_count', 'phase_duration_proposal_min_blocks', 'final_probability', 'op_cost_sequencer', 'op_cost_prover'}

    for _ in range(N_sequencer):
        a = Agent(uuid=uuid4(),
                                     balance=max(norm.rvs(50, 20), 1),
                                     is_sequencer=True,
                                     is_prover=False,
                                     is_relay=False,
                                     staked_amount=32)
        Sqn3Prv3_agents.append(a)
    for _ in range(N_prover):
        a = Agent(uuid=uuid4(),
                                     balance=max(norm.rvs(160, 10), 16),
                                     is_sequencer=False,
                                     is_prover=True,
                                     is_relay=False,
                                     staked_amount=0.0)
        Sqn3Prv3_agents.append(a)

    
    Sqn3Prv3_dict = {a.uuid: a for a in Sqn3Prv3_agents}
    Sqn3Prv3 = {**BASE_AGENTS_DICT, **Sqn3Prv3_dict}


    initial_state = INITIAL_STATE.copy()
    initial_state['agents'] = Sqn3Prv3
    initial_state['token_supply'] = TokenSupply.from_state(initial_state)

    sweep_params = {k: [v] for k, v in SINGLE_RUN_PARAMS.items()}

    sweep_params_upd: dict[str, list] = dict( 
                                    # Phase Durations
                                        phase_duration_proposal_min_blocks=[0, 3],
                                        phase_duration_proposal_max_blocks=[3, 12], 
                                        phase_duration_reveal_min_blocks = [0],
                                        phase_duration_reveal_max_blocks = [3, 24], 
                                        phase_duration_commit_bond_min_blocks = [0],
                                        phase_duration_commit_bond_max_blocks=[3, 12], 
                                        phase_duration_rollup_min_blocks = [0],
                                        phase_duration_rollup_max_blocks=[15, 80],
                                        phase_duration_race_min_blocks = [0],
                                        phase_duration_race_max_blocks=[2], 
                                    
#                                        rewards_to_provers=[0.3, 0.5],
#                                        rewards_to_relay=[0.0, 0.01],

                                        gas_estimators=[DEFAULT_DETERMINISTIC_GAS_ESTIMATOR],
                                        tx_estimators=[DEFAULT_DETERMINISTIC_TX_ESTIMATOR],
                                        slash_params=[SLASH_PARAMS],
                                        gas_fee_l1_time_series=GAS_FEE_L1_TIME_SERIES_LIST,
                                        gas_fee_blob_time_series=GAS_FEE_BLOB_TIME_SERIES_LIST,
                                        )  
    
    sweep_params = {**sweep_params, **sweep_params_upd} # type: ignore


    sweep_combinations: int = 1
    for v in sweep_params.values():
        sweep_combinations *= len(v)
    
    n_sweeps = N_sweep_samples if N_sweep_samples > 0 else sweep_combinations

    traj_combinations = n_sweeps * N_samples
    
    sweep_params_cartesian_product = sweep_cartesian_product(sweep_params)

    N_measurements = n_sweeps * N_timesteps * N_samples
    logger.info(f'PSuU Exploratory Run Dimensions: {N_jobs=:,}, {N_timesteps=:,}, N_sweeps={n_sweeps:,}, {N_samples=:,}, N_trajectories={traj_combinations:,}, N_measurements={N_measurements:,}')

    

    sweep_params_cartesian_product = {k: list(v) for k, v in sweep_params_cartesian_product.items()}

    sweep_params_cartesian_product = {k: sample(v, N_sweep_samples) if N_sweep_samples > 0 else v 
                                                               for k, v in sweep_params_cartesian_product.items()}


    sim_start_time = datetime.now()
    logger.info(f"PSuU Exploratory Run starting at {sim_start_time}, ({sim_start_time - invoke_time} since invoke)")
    if N_jobs <= 1:
        # Load simulation arguments
        sim_args = (initial_state,
                    sweep_params_cartesian_product,
                    AZTEC_MODEL_BLOCKS,
                    N_timesteps,
                    N_samples)
        # Run simulation
        sim_df = sim_run(*sim_args, exec_mode='single', assign_params=assign_params, supress_cadCAD_print=supress_cadCAD_print)
    else:
        sweeps_per_process = 25
        processes = N_jobs

        chunk_size = sweeps_per_process
        split_dicts = [
            {k: v[i:i + chunk_size] for k, v in sweep_params_cartesian_product.items()}
            for i in range(0, len(list(sweep_params_cartesian_product.values())[0]), chunk_size)
        ]

        def run_chunk(i_chunk, sweep_params):
            logger.debug(f"{i_chunk}, {datetime.now()}")
            sim_args = (initial_state,
                        sweep_params,
                        AZTEC_MODEL_BLOCKS,
                        N_timesteps,
                        N_samples)
            # Run simulationz
            sim_df = sim_run(*sim_args, exec_mode='single', assign_params=assign_params, supress_cadCAD_print=supress_cadCAD_print)
            output_filename = Path(output_path) / f'{timestep_tensor_prefix}_{i_chunk}.pkl.zip'
            sim_df['simulation'] = i_chunk
            logger.debug(f"n_groups: {sim_df.groupby(['simulation', 'run', 'subset']).ngroups}")
            sim_df.to_pickle(output_filename)

        args = enumerate(split_dicts)
        if parallelize_jobs:
            Parallel(n_jobs=processes)(delayed(run_chunk)(i_chunk, sweep_params) for (i_chunk, sweep_params) in tqdm(args, desc='Simulation Chunks', total=len(split_dicts)))
        else: 
            for (i_chunk, sweep_params) in tqdm(args):
                sim_args = (initial_state,
                            sweep_params,
                            AZTEC_MODEL_BLOCKS,
                            N_timesteps,
                            N_samples)
                # Run simulationz
                sim_df = sim_run(*sim_args, exec_mode='single', assign_params=assign_params, supress_cadCAD_print=supress_cadCAD_print)
                output_filename = output_path + f'-{i_chunk}.pkl.zip'
                sim_df.to_pickle(output_filename)
    end_start_time = datetime.now()
    duration: float = (end_start_time - sim_start_time).total_seconds()
    logger.info(f"PSuU Exploratory Run finished at {end_start_time}, ({end_start_time - sim_start_time} since sim start)")
    logger.info(f"PSuU Exploratory Run Performance Numbers; Duration (s): {duration:,.2f}, Measurements Per Second: {N_measurements/duration:,.2f} M/s, Measurements per Job * Second: {N_measurements/(duration * N_jobs):,.2f} M/(J*s)")

    if 'sim_df' in locals():
        return sim_df
    else:
        return None