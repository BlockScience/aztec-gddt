import pandas as pd # type: ignore
import json
import os
import time
from typing import List, Tuple, Iterable

import aztec_gddt.metrics as m
import aztec_gddt.plot_tools as pt
from tqdm.auto import tqdm # type: ignore


TensorPerTrajectory = object

KPIs = {"proportion_race_mode": m.find_proportion_race_mode,
        "roportion_slashed_prover": m.find_proportion_slashed_due_to_prover,
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
        config = json.load(file)
        data_directory = config['data_directory'] # Where to look for the data. 
        data_prefix = config['data_prefix'] # Take only files with this prefix in the name. 
    
    files_to_use  = [f"{data_directory}\{data_prefix}-{num}.pkl.gz" 
                    for num 
                    in num_range]
    return files_to_use
            
    

def timestep_files_to_trajectory(per_timestep_tensor_paths: list[str]) -> Iterable[TensorPerTrajectory]:
    for path in tqdm(per_timestep_tensor_paths):
        df_per_timestep = pd.read_pickle(path)
        df_per_trajectory = pt.extract_df(
                                          m.process_df(df_per_timestep),   
                                          trajectory_kpis = KPIs                                                    
                                         )
        yield df_per_trajectory

def process_timestep_files_to_csv(per_timestep_tensor_paths: list[str],
                                  filename: str) -> pd.DataFrame:
    dfs_to_concat = [df
                     for df
                     in timestep_files_to_trajectory(per_timestep_tensor_paths)]
    final_df = pd.concat(dfs_to_concat).to_csv(filename)
    return final_df


if __name__ == "__main__":

    start_time = time.time()

    timestep_files = get_timestep_files_from_info()
    num_files = len(timestep_files)
    trajectory_list = process_timestep_files_to_csv(per_timestep_tensor_paths = timestep_files, 
                                                    filename = "test.csv")

    end_time = time.time()

    execution_time = end_time - start_time

    print(f"Processed {num_files} files.")
    print(f"Execution time: {execution_time} seconds")





