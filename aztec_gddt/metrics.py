from typing import Callable
import numpy as np
import pandas as pd
from typing import Callable, Any
from tqdm.auto import tqdm # type: ignore


from aztec_gddt.types import SelectionPhase
import logging
from aztec_gddt import DEFAULT_LOGGER
logger = logging.getLogger(DEFAULT_LOGGER)

#################################
## Begin data grouping.        ##
#################################

G1 = [("proportion_race_mode", "below"),
    ("proportion_slashed_prover", "below"),
    ("proportion_slashed_sequencer", "below"),
    ("proportion_skipped", "below")]

G2 = [("average_duration_finalized_blocks", "below"),
      ("stddev_duration_finalized_blocks", "below"),
      ("average_duration_nonfinalized_blocks", "below"),
      ("stddev_duration_nonfinalized_blocks", "below")
      ]

#################################
## Begin helper functions      ##
#################################

def process_df(sim_df: pd.DataFrame):
    new_df = sim_df.copy(deep=True).dropna(axis='index')
    new_df['process_id'] = new_df['current_process'].apply(lambda x: None if x is None else x.uuid )
    new_df['process_phase'] = new_df['current_process'].apply(lambda x: None if x is None else x.phase)
    return new_df


def time_spent(trajectory: pd.DataFrame, process_id: str) -> float:
    first_step = trajectory[trajectory['process_id'] == process_id].iloc[0].time_l1
    last_step = trajectory[trajectory['process_id'] == process_id].iloc[-1].time_l1
    return last_step - first_step

def find_finalized_blocks(trajectory: pd.DataFrame) -> list[Any]:
    processes = [x for x in trajectory['process_id'].unique() if not (x is None)]
    finalized_blocks = [proc_id 
                        for proc_id 
                        in processes 
                        if trajectory[trajectory['process_id'] == proc_id]['process_phase'].apply(lambda x: x == SelectionPhase.finalized.value).sum() > 0]
    return finalized_blocks

def find_nonfinalized_blocks(trajectory: pd.DataFrame) -> list[Any]:
    processes = [x for x in trajectory['process_id'].unique() if not (x is None)]
    nonfinalized_blocks = [proc_id 
                           for proc_id 
                           in processes 
                           if trajectory[trajectory['process_id'] == proc_id]['process_phase'].apply(lambda x: x == SelectionPhase.skipped.value).sum() > 0]
    return nonfinalized_blocks

def find_finalized_block_times(trajectory: pd.DataFrame):
    finalized_blocks = find_finalized_blocks(trajectory)
    finalized_block_times = np.array([time_spent(trajectory, proc_id)
                                     for proc_id 
                                     in finalized_blocks])
    return finalized_block_times

def find_nonfinalized_block_times(trajectory: pd.DataFrame):
    nonfinalized_blocks = find_nonfinalized_blocks(trajectory)
    nonfinalized_block_times = np.array([time_spent(trajectory, proc_id)
                                         for proc_id 
                                         in nonfinalized_blocks])
    return nonfinalized_block_times

def find_times_sequencer_slashed(trajectory: pd.DataFrame) -> float:
    slashes_to_sequencers = trajectory['slashes_to_sequencers'].max()
    return slashes_to_sequencers

def find_times_prover_slashed(trajectory: pd.DataFrame) -> float:
    slashes_to_provers = trajectory['slashes_to_provers'].max()
    return slashes_to_provers


####################################
## End helper functions           ##
####################################

####################################
## Begin Group 1 Metrics          ##
####################################

# Group 1: T1 Metric
def find_proportion_race_mode(trajectory: pd.DataFrame) -> float:
    """
    Find the proportion of blocks that entered race mode. 
    """
    processes = [x for x in trajectory['process_id'].unique() if not (x is None)]

    proportion_race_mode = np.array([trajectory[trajectory['process_id'] == proc_id]['process_phase'].apply(lambda x: x == SelectionPhase.proof_race.value).sum() > 0
                for proc_id in processes]).mean()
    return proportion_race_mode 

# Group 1: T2 Metric
def find_proportion_slashed_due_to_prover(trajectory: pd.DataFrame) -> float:
    """
    Determine which proportion of unsuccessful blocks were due to prover.
    """
    num_processes: int = len([x for x in trajectory['process_id'].unique() if not (x is None)])
    slashes_to_provers = find_times_prover_slashed(trajectory)
    proportion_slashed_due_to_prover = slashes_to_provers/num_processes

    return proportion_slashed_due_to_prover

# Group 1: T3 Metric
def find_proportion_slashed_due_to_sequencer(trajectory: pd.DataFrame) -> float:
    """
    Determine which proportion of unsuccessful blocks were due to sequencer.
    """

    num_processes = len([x for x in trajectory['process_id'].unique() if not (x is None)])
    slashes_to_sequencers = find_times_sequencer_slashed(trajectory)
    proportion_slashed_due_to_sequencer = slashes_to_sequencers/num_processes

    return proportion_slashed_due_to_sequencer 


# Group 1: T4 Metric 
def find_proportion_skipped(trajectory: pd.DataFrame) -> float:
    processes = [x for x in trajectory['process_id'].unique() if not (x is None)]

    proportion_skipped = np.array([trajectory[trajectory['process_id'] == proc_id]['process_phase'].apply(lambda x: x == SelectionPhase.skipped.value).sum() > 0
                for proc_id in processes]).mean()
    return proportion_skipped 

####################################
## End Group 1 Metrics            ##
####################################

####################################
## Begin Group 2 Metrics          ##
####################################

# Group 2, Metrics T5 

def find_average_duration_finalized_blocks(trajectory: pd.DataFrame) -> float | np.floating:
    block_times = find_finalized_block_times(trajectory)
    if len(block_times) == 0:
        avg_dur = np.nan
    else:
        avg_dur = np.mean(block_times)
    return avg_dur

# Group 2, Metric T6

def find_stddev_duration_finalized_blocks(trajectory: pd.DataFrame) -> float | np.floating:
    block_times = find_finalized_block_times(trajectory)
    if len(block_times) == 0:
        std_dur = np.nan
    else:
        std_dur = np.std(block_times)
    return std_dur

# Group 2, Metric T7

def find_average_duration_nonfinalized_blocks(trajectory: pd.DataFrame) -> float | np.floating:
    block_times = find_nonfinalized_block_times(trajectory)
    if len(block_times) == 0:
        avg_dur = np.nan
    else:
        avg_dur = np.mean(block_times)
    return avg_dur

# Group 2, Metric T8

def find_stddev_duration_nonfinalized_blocks(trajectory: pd.DataFrame) -> float | np.floating:
    block_times = find_finalized_block_times(trajectory)
    if len(block_times) == 0:
        std_dur = np.nan
    else:
        std_dur = np.std(block_times)
    return std_dur

####################################
## End Group 2 Metrics            ##
####################################

####################################
## Begin Group 3 Metrics          ##
####################################

def find_stddev_payoffs_to_sequencers(trajectory: pd.DataFrame) -> float | np.floating:
    logger.warn("Not yet implemented")
    return float('nan') 

def find_stddev_payoffs_to_provers(trajectory: pd.DataFrame) -> float | np.floating:
    logger.warn("Not yet implemented")
    return float('nan')  

def find_delta_total_revenue_agents(trajectory: pd.DataFrame) -> float | np.floating:
    initial_balance_agents = sum([agent.balance for agent in trajectory["agents"].iloc[0].values()])
    final_balance_agents = sum([agent.balance for agent in trajectory["agents"].iloc[-1].values()])
    delta_balance_agents = final_balance_agents - initial_balance_agents
    return delta_balance_agents


####################################
## End Group 3 Metrics            ##
####################################

####################################
## Begin PostProcessing/KPIs      ##
####################################


def check_median_across_trajectories(df: pd.DataFrame, 
                                     column_name: str,
                                      direction: str):
    # Extract the specified column's values
    column_values = df[column_name]
    
    # Calculate the median of the specified column
    median_column_values = column_values.median()
    
    # Determine direction of comparison
    if direction == 'above':
        return column_values > median_column_values
    elif direction == 'below':
        return column_values < median_column_values
    else:
        raise ValueError("The 'direction' parameter must be either 'above' or 'below'.")

def calculate_goal_score(grouped_df: pd.DataFrame, 
                         group: list[tuple[str, str]],
                         new_column_name: str) -> pd.DataFrame:
    
    scores_df = grouped_df.copy()
    scores_df[new_column_name] = 0
    
    for column_name, direction in group:
        # For each metric, add a new column to scores_df to store individual column scores
        scores_df[f'score_{column_name}'] = check_median_across_trajectories(grouped_df,
                                                    column_name, 
                                                    direction).astype(int)        
        scores_df[new_column_name] += scores_df[f'score_{column_name}']
    
    return scores_df


####################################
## End PostProcessing/KPIs        ##
####################################
