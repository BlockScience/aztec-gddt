from aztec_gddt.types import *
import numpy as np

def active_processes(processes: list[Process]) -> list[Process]:
    return [p for p in processes
            if p.phase > 0
            and p.phase != SelectionPhase.finalized]


def most_advanced_active_process(processes: list[Process]) -> Process:
    sorted_processes_by_phase = sorted(active_processes(processes),
                                       key=lambda p: p.phase)

    most_advanced_process = sorted_processes_by_phase[-1]
    return most_advanced_process


def last_active_process(processes: list[Process]) -> Process:
    # XXX: this assumes that the process list is ordered correctly
    return active_processes(processes)[-1]

#######################################
## Helper functions for Selection    ##
#######################################


def select_processes_by_state(processes: list[Process], phase_to_select: SelectionPhase) -> list[Process]:
    selected_processes = [proc for proc in processes if proc.phase == phase_to_select]
    return selected_processes


def has_blown_phase_duration(process) -> bool:
    # TODO: Determine if a process has blown its phase duration. (Not sure what this means or how to calculate at moment.)
    return False

#######################################
## Helper functions for decisions    ##
#######################################

def bernoulli_trial(probability: float) -> bool:
    if probability > 1 or probability < 0:
        raise ValueError(f"Probability must be be between 0 and 1, was given {probability}.")

    # TODO: refactor so that the seed is properly tracked
    rng = np.random.default_rng()
    rand_num = rng.uniform(low = 0, high = 1)
    hit = (rand_num <= probability)

    return hit 
