import pandas as pd # type: ignore
from pandas import DataFrame

from aztec_gddt.params import INITIAL_STATE
from aztec_gddt.params import SINGLE_RUN_PARAMS
from aztec_gddt.structure import AZTEC_MODEL_BLOCKS
from aztec_gddt.types import AztecModelParams, AztecModelState
from aztec_gddt.utils import sim_run

def standard_run() -> DataFrame:
    """Function which runs the cadCAD simulations

    Returns:
        DataFrame: A dataframe of simulation data
    """

    # Set the number of timesteps for a single simulation. 
    N_timesteps = 700

    # Set the number of monte carlo runs for a single parameter. 
    N_samples = 1

  
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
               params_to_sweep:AztecModelParams = None,
               model_blocks:list[dict] = None,
               N_timesteps:int = 700,
               N_samples:int = 1) -> DataFrame:
    """
    Function to run a custom cadCAD simulation

    Args:
        initial_state (AztecModelState): The initial state for the simulation
        params_to_sweep (AztecModelParams): The parameters to sweep during the simulation
        model_blocks (list[dict]): The model blocks for the simulation
        N_timesteps (int): Number of timesteps to run the simulation
        N_samples (int): Number of Monte Carlo runs to perform

    Returns:
        DataFrame: A dataframe of simulation data
    """ 
    # Set default values.

    if initial_state is None:
        initial_state = INITIAL_STATE
    if params_to_sweep is None:
        params_to_sweep = SINGLE_RUN_PARAMS
    if model_blocks is None:
        model_blocks = AZTEC_MODEL_BLOCKS


     # Get the sweep params in the form of single length arrays
    sweep_params = {} # Create empty dict. 
    for k,v in params_to_sweep.items():
        if isinstance(v, list):
            sweep_params[k] = [v]
        else:
            sweep_params[k] = v

    # Load simulation arguments
    sim_args = (initial_state,
                params_to_sweep,
                model_blocks,
                N_timesteps,
                N_samples)

    # Run simulation
    sim_df = sim_run(*sim_args)
    return sim_df



