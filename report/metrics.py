import numpy as np
import pandas as pd

from aztec_gddt.types import SelectionPhase

####################################
## Begin Group 1 Metrics          ##
####################################

# Group 1: T1 Metric
def find_proportion_race_mode(trajectory: pd.DataFrame) -> float:
    processes = [x for x in trajectory['process_id'].unique() if not (x is None)]

    proportion_race_mode = np.array([trajectory[trajectory['process_id'] == proc_id]['process_phase'].apply(lambda x: x == SelectionPhase.proof_race.name).sum() > 0
                for proc_id in processes]).mean()
    return proportion_race_mode 

# Group 1: T2 Metric
def find_proportion_slashed_due_to_prover(trajectory: pd.DataFrame) -> float:
    processes = [x for x in trajectory['process_id'].unique() if not (x is None)]

    proportion_slashed_due_to_prover = -1 # TODO: change

    print("Not implemented yet.")
    pass 

# Group 1: T3 Metric
def find_proportion_slashed_due_to_sequencer(trajectory: pd.DataFrame) -> float:

    processes = [x for x in trajectory['process_id'].unique() if not (x is None)]
    proportion_slashed_due_to_sequencer = -1 # TODO: change


    print("Not implemented yet.")
    pass 


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

# Helper Functions

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

# Group 2, Metrics T5 

def find_average_duration_finalized_blocks(trajectory: pd.DataFrame) -> float:
    return np.mean(find_finalized_block_times(trajectory))

# Group 2, Metric T6

def std_dev_duration_finalized_blocks(trajectory: pd.DataFrame) -> float:
    return np.std(find_finalized_block_times(trajectory))

# Group 2, Metric T7

def average_duration_nonfinalized_blocks(trajectory: pd.DataFrame) -> float:
    return np.mean(find_nonfinalized_block_times(trajectory))


# Group 2, Metric T8

def stddev_duration_nonfinalized_blocks(trajectory: pd.DataFrame) -> float:
    return np.std(find_nonfinalized_block_times(trajectory))

####################################
## End Group 2 Metrics            ##
####################################

####################################
## Begin Group 3 Metrics          ##
####################################

# TODO: The Group 3 Metrics

####################################
## End Group 3 Metrics            ##
####################################

####################################
## PostProcessing                 ##
####################################

def is_above_median_across_trajectories(grouped_data, custom_func: Callable):
    mapped_values = grouped_data.apply(custom_func)
    median_mapped_values = mapped_values.median()
    return int(mapped_values >= median_mapped_values)

def is_below_median_across_trajectories(grouped_data, custom_func: Callable):
    mapped_values = grouped_data.apply(custom_func)
    median_mapped_values = mapped_values.median()
    return int(mapped_values < median_mapped_values)

