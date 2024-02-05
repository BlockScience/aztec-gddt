from pandas import DataFrame
from typing import Dict, List

from aztec_gddt.params import INITIAL_STATE
from aztec_gddt.params import SINGLE_RUN_PARAMS
from aztec_gddt.structure import AZTEC_MODEL_BLOCKS
from aztec_gddt.types import AztecModelParams, AztecModelState
from aztec_gddt.utils import sim_run

def standard_run(N_timesteps=700) -> DataFrame:
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

def custom_run(initial_state:AztecModelState = None,
               default_params: AztecModelParams = None,
               params_to_modify: Dict[str,List] = None,
               model_blocks:list[dict] = None,
               N_timesteps:int = 700,
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

    # Modify the parameters that need to be modified. 
    for k,v in params_to_modify.items():
        sweep_params[k] = v
        # if isinstance(v, list):
        #     sweep_params[k] = v
        # else:
        #     sweep_params[k] = [v]
        # Load simulation arguments
    sim_args = (initial_state,
                sweep_params,
                model_blocks,
                N_timesteps,
                N_samples)

    # Run simulation
    sim_df = sim_run(*sim_args)
    return sim_df
    