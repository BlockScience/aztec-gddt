from copy import deepcopy

import pandas as pd # type: ignore
from pandas import DataFrame
from typing import Dict, List

from IPython.display import display, Markdown

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
    

# TODO: Create method that creates params to sweep. 
# # Begin by copying the indicated default settings. 
#     sweep_params = deepcopy(default_params)
#     # Modify the parameters that need to be modified. 
#     for k,v in params_to_modify:
#         if isinstance(v, list):
#             sweep_params[k] = v
#         else:
#             sweep_params[k] = [v]

def create_model_params_table(model_name: str = "Experiment",
                        default_params: AztecModelParams = None,
                        params_to_modify: Dict[str, List] = None,
                        allowed_types: tuple = None, 
                        params_to_exclude = None,
                        display_to_screen = False
                       ) -> str:
    """
    Automatically creates a parameter table showing the values used for a given run.

    Args:
       model_name(str): An identifier for the current experiment or model.
       params_dict (Dict[str,List]): A dictionary mapping variable names to lists of values.
       allowed_types (tuple): A tuple of types that should be included. 


    Returns:
    """

    ##############################
    ## Set standards if needed. ##
    ##############################
    
    if allowed_types is None: 
        allowed_types = (object)
    
    if params_to_exclude is None:
        params_to_exclude = []

    if default_params is None:
        default_params = SINGLE_RUN_PARAMS

    ##############################
    ## Make a final dictionary  ##
    ## that represents both the ##
    ## default values and those ##
    ## being modified.          ##
    ##############################

    final_params_dict = deepcopy(default_params)
    final_params_dict.update(params_to_modify)

    ##############################
    ## Make the table.          ##
    ##############################
    
    params_table_title = f"## Current Parameter Values for {model_name} \n"
    params_table = "| Parameter | Values to Use |\n| --- | --- |\n"
    for k, v in final_params_dict.items():
        if isinstance(v, allowed_types) and not(k in params_to_exclude):
            params_table += f"| {k} | {v} |\n"

    final_params_markdown = params_table_title + params_table

    ##############################
    ## Display if desired.      ##
    ## NOTE that this is only   ##
    ## valid inside a Jupyter   ##
    ## notebook.                ##
    ##############################

    if display_to_screen:
        display(Markdown(final_params_markdown))

    return final_params_markdown

def process_data(df: pd.DataFrame,
                inplace: bool = True) -> pd.DataFrame:
    # TODO: A method that processes the data based on things that have been input. 
    pass 


