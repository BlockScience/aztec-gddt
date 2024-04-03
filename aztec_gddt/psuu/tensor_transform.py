import sys
sys.path.append(".")

from tqdm.auto import tqdm  # type: ignore
import aztec_gddt.plot_tools as pt
import aztec_gddt.metrics as m
import pandas as pd
import json
import os
import time
from typing import List, Tuple, Iterable
from pathlib import Path
from multiprocessing import Pool
import logging
from aztec_gddt import DEFAULT_LOGGER
logger = logging.getLogger(DEFAULT_LOGGER)


TensorPerTrajectory: pd.DataFrame

KPIs = {"proportion_race_mode": m.find_proportion_race_mode,
        "proportion_slashed_prover": m.find_proportion_slashed_due_to_prover,
        "proportion_slashed_sequencer": m.find_proportion_slashed_due_to_sequencer,
        "proportion_skipped": m.find_proportion_skipped,
        "average_duration_finalized_blocks": m.find_average_duration_finalized_blocks,
        "stddev_duration_finalized_blocks": m.find_stddev_duration_finalized_blocks,
        "average_duration_nonfinalized_blocks": m.find_average_duration_nonfinalized_blocks,
        "stddev_duration_nonfinalized_blocks": m.find_stddev_duration_nonfinalized_blocks,
        #       "stddev_payoffs_to_sequencers": m.find_stddev_payoffs_to_sequencers,
        #       "stddev_payoffs_to_provers": m.find_stddev_payoffs_to_provers,
        "delta_total_revenue_agents": m.find_delta_total_revenue_agents
        }


# COLS_TO_DROP = ['simulation', 'subset', 'run']

def get_timestep_files_from_info(config_file: str = "config.json",
                                 num_range: List[int] = [0]):
    with open(config_file, "r") as file:
        config: dict = json.load(file)
        # Where to look for the data.
        data_directory = Path(config['data_directory'])
        # Take only files with this prefix in the name.
        data_prefix = config['data_prefix']

    files_to_use = [data_directory / f for f in os.listdir(data_directory)
                    if data_prefix in f
                    and ".pkl" in f]
    return files_to_use


def timestep_file_to_trajectory(path: str) -> pd.DataFrame:
    df_per_timestep = pd.read_pickle(path)
    df_to_use = m.process_df(df_per_timestep)
    df_per_trajectory: pd.DataFrame = pt.extract_df(df_to_use,
                                                    trajectory_kpis=KPIs)
    return df_per_trajectory


def process_timestep_files_to_csv(per_timestep_tensor_paths: list[str],
                                  filename: str) -> pd.DataFrame:
    dfs_to_concat = Pool(4).map(timestep_file_to_trajectory, per_timestep_tensor_paths)
    final_df = pd.concat(dfs_to_concat)
    final_df.to_csv(filename)
    return final_df


if __name__ == "__main__":

    start_time = time.time()

    config_path = "data/config.json"
    with open(config_path, "r") as file:
        config: dict = json.load(file)

    output_path = config['output_path']
    timestep_files = get_timestep_files_from_info(config_path)
    num_files = len(timestep_files)
    trajectory_list = process_timestep_files_to_csv(per_timestep_tensor_paths=timestep_files,
                                                    filename=output_path)

    end_time = time.time()

    execution_time = end_time - start_time

    logger.info(f"Processed {num_files} files.")
    logger.info(f"Execution time: {execution_time} seconds")
