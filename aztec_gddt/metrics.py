import numpy as np
import pandas as pd # type: ignore
from typing import Callable

from aztec_gddt.types import SelectionPhase


#################################
## Begin helper functions      ##
#################################

def process_df(sim_df: pd.DataFrame):
    new_df = sim_df.copy(deep=True).dropna(axis='index')
    new_df['process_id'] = new_df['current_process'].apply(lambda x: None if x is None else x.uuid )
    new_df['process_phase'] = new_df['current_process'].apply(lambda x: None if x is None else x.phase)
    return new_df


def time_spent(trajectory: pd.DataFrame, process_id: str):
    first_step = trajectory[trajectory['process_id'] == process_id].iloc[0].time_l1
    last_step = trajectory[trajectory['process_id'] == process_id].iloc[-1].time_l1
    return last_step - first_step

def find_finalized_blocks(trajectory: pd.DataFrame):
    processes = [x for x in trajectory['process_id'].unique() if not (x is None)]
    finalized_blocks = [proc_id 
                        for proc_id 
                        in processes 
                        if trajectory[trajectory['process_id'] == proc_id]['process_phase'].apply(lambda x: x == SelectionPhase.finalized.name).sum() > 0]
    return finalized_blocks

def find_nonfinalized_blocks(trajectory: pd.DataFrame):
    processes = [x for x in trajectory['process_id'].unique() if not (x is None)]
    nonfinalized_blocks = [proc_id 
                           for proc_id 
                           in processes 
                           if trajectory[trajectory['process_id'] == proc_id]['process_phase'].apply(lambda x: x == SelectionPhase.skipped.name).sum() > 0]
    return nonfinalized_blocks

def find_finalized_block_times(trajectory: pd.DataFrame):
    finalized_blocks = find_finalized_blocks(trajectory)
    finalized_block_times = np.array([time_spent(trajectory, proc_id) for proc_id in finalized_blocks])
    return finalized_block_times

def find_nonfinalized_block_times(trajectory: pd.DataFrame):
    nonfinalized_blocks = find_nonfinalized_blocks(trajectory)
    nonfinalized_block_times = np.array([time_spent(trajectory, proc_id) for proc_id in nonfinalized_blocks])
    return nonfinalized_block_times

def find_times_sequencer_slashed(trajectory: pd.DataFrame):
    slashes_to_sequencer = trajectory['slashes'].iloc[-1].get("to_sequencers", 0)
    return slashes_to_sequencer

def find_times_prover_slashed(trajectory: pd.DataFrame):
    slashes_to_prover = trajectory['slashes'].iloc[-1].get("to_provers", 0)
    return slashes_to_prover


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

    proportion_race_mode = np.array([trajectory[trajectory['process_id'] == proc_id]['process_phase'].apply(lambda x: x == SelectionPhase.proof_race.name).sum() > 0
                for proc_id in processes]).mean()
    return proportion_race_mode 

# Group 1: T2 Metric
def find_proportion_slashed_due_to_prover(trajectory: pd.DataFrame) -> float:
    """
    Determine which proportion of unsuccessful blocks were due to prover.
    """
    num_processes = len([x for x in trajectory['process_id'].unique() if not (x is None)])
    slashes_to_prover = find_times_prover_slashed(trajectory)
    proportion_slashed_due_to_prover = slashes_to_prover/num_processes

    return proportion_slashed_due_to_prover

# Group 1: T3 Metric
def find_proportion_slashed_due_to_sequencer(trajectory: pd.DataFrame) -> float:
    """
    Determine which proportion of unsuccessful blocks were due to sequencer.
    """

    num_processes = len([x for x in trajectory['process_id'].unique() if not (x is None)])
    slashes_to_sequencer = find_times_sequencer_slashed(trajectory)
    proportion_slashed_due_to_sequencer = slashes_to_sequencer/num_processes

    return proportion_slashed_due_to_sequencer 


# Group 1: T4 Metric 
def find_proportion_skipped(trajectory: pd.DataFrame) -> float:
    processes = [x for x in trajectory['process_id'].unique() if not (x is None)]

    proportion_skipped = np.array([trajectory[trajectory['process_id'] == proc_id]['process_phase'].apply(lambda x: x == SelectionPhase.skipped.name).sum() > 0
                for proc_id in processes]).mean()
    return proportion_skipped 

####################################
## End Group 1 Metrics            ##
####################################

####################################
## Begin Group 2 Metrics          ##
####################################

# Group 2, Metrics T5 

def find_average_duration_finalized_blocks(trajectory: pd.DataFrame) -> np.floating:
    return np.mean(find_finalized_block_times(trajectory))

# Group 2, Metric T6

def find_stddev_duration_finalized_blocks(trajectory: pd.DataFrame) -> np.floating:
    return np.std(find_finalized_block_times(trajectory))

# Group 2, Metric T7

def find_average_duration_nonfinalized_blocks(trajectory: pd.DataFrame) -> np.floating:
    return np.mean(find_nonfinalized_block_times(trajectory))


# Group 2, Metric T8

def find_stddev_duration_nonfinalized_blocks(trajectory: pd.DataFrame) -> np.floating:
    return np.std(find_nonfinalized_block_times(trajectory))

####################################
## End Group 2 Metrics            ##
####################################

####################################
## Begin Group 3 Metrics          ##
####################################

def find_stddev_payoffs_to_sequencers(trajectory: pd.DataFrame) -> float:
    print("Not yet implemented")
    return float('nan') 

def find_stddev_payoffs_to_provers(trajectory: pd.DataFrame) -> float:
    print("Not yet implemented")
    return float('nan')  

####################################
## End Group 3 Metrics            ##
####################################

####################################
## Begin PostProcessing/KPIs      ##
####################################

def is_above_median_across_trajectories(grouped_data: pd.DataFrame, custom_func: Callable):
    """
    TODO: check if the behavior is matching with the workplan
    """
    mapped_values = grouped_data.apply(custom_func)
    median_mapped_values = mapped_values.median()
    return mapped_values > median_mapped_values

def is_below_median_across_trajectories(grouped_data: pd.DataFrame, custom_func: Callable):
    # NOTE: Stingy version. 
    mapped_values = grouped_data.apply(custom_func)
    median_mapped_values = mapped_values.median()
    return mapped_values < median_mapped_values

def calc_g1_score(grouped_data: pd.DataFrame) -> float:
    t1_score = is_below_median_across_trajectories(grouped_data, find_proportion_race_mode)
    t2_score = is_below_median_across_trajectories(grouped_data, find_proportion_slashed_due_to_prover)
    t3_score = is_below_median_across_trajectories(grouped_data, find_proportion_slashed_due_to_sequencer)
    t4_score = is_below_median_across_trajectories(grouped_data, find_proportion_skipped)
    final_score = t1_score + t2_score + t3_score + t4_score
    return final_score

def calc_mock_g1_score(grouped_data: pd.DataFrame) -> float:
    t1_score = is_below_median_across_trajectories(grouped_data, find_proportion_race_mode)
    t4_score = is_below_median_across_trajectories(grouped_data, find_proportion_skipped)
    final_score = t1_score +  t4_score
    return final_score

def calc_g2_score(grouped_data: pd.DataFrame) -> float:
    t5_score = is_below_median_across_trajectories(grouped_data, find_average_duration_finalized_blocks)
    t6_score = is_below_median_across_trajectories(grouped_data, find_stddev_duration_finalized_blocks)
    t7_score = is_below_median_across_trajectories(grouped_data, find_average_duration_nonfinalized_blocks)
    t8_score = is_below_median_across_trajectories(grouped_data, find_stddev_duration_nonfinalized_blocks)
    final_score = t5_score + t6_score + t7_score + t8_score
    return final_score


def calc_g3_score(grouped_data: pd.DataFrame) -> float:
    t9_score = is_below_median_across_trajectories(grouped_data, find_stddev_payoffs_to_sequencers)
    t10_score = is_below_median_across_trajectories(grouped_data, find_stddev_payoffs_to_provers)
    final_score = t9_score + t10_score
    return final_score

####################################
## End PostProcessing/KPIs        ##
####################################

####################################
## Begin Mock Metrics             ##
####################################

def mock_proportion_race_mode(trajectory: pd.DataFrame) -> float:
    fuzz_val = np.random.uniform()
    return fuzz_val

def mock_proportion_slashed_due_to_prover(trajectory: pd.DataFrame) -> float:
    fuzz_val = np.random.uniform()
    return fuzz_val

def mock_proportion_slashed_due_to_sequencer(trajectory: pd.DataFrame) -> float:
    fuzz_val = np.random.uniform()
    return fuzz_val

def mock_proportion_skipped(trajectory: pd.DataFrame) -> float:
    fuzz_val = np.random.uniform()
    return fuzz_val




####################################
## End Mock Metrics               ##
####################################