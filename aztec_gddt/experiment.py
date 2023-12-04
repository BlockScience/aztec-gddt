import pandas as pd # type: ignore
from aztec_gddt.params import INITIAL_STATE
from aztec_gddt.params import SINGLE_RUN_PARAMS
from aztec_gddt.structure import AZTEC_MODEL_BLOCKS
from pandas import DataFrame
from aztec_gddt.utils import sim_run

def standard_run() -> DataFrame:
    """Function which runs the cadCAD simulations

    Returns:
        DataFrame: A dataframe of simulation data
    """
    # The number of timesteps for each simulation to run
    N_timesteps = 360

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
