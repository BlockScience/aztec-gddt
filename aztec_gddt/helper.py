from aztec_gddt.types import *





def active_processes(processes: list[Process]) -> list[Process]:
    return [p for p in processes
            if p.current_phase > 0
            and p.current_phase != SelectionPhase.finalized]

def most_advanced_active_process(processes: list[Process]) -> Process:
    sorted_processes_by_phase = sorted(active_processes(processes), 
                                       key=lambda p: p.current_phase)
    
    most_advanced_process = sorted_processes_by_phase[-1]
    return most_advanced_process

def last_active_process(processes: list[Process]) -> Process:
    # XXX: this assumes that the process list is ordered correctly
    return active_processes(processes)[-1]

#######################################
## Helper functions for Selection    ##
#######################################

def select_processes_by_state(processes: list[Process], phase: SelectionPhase) -> list[Process]:
    # TODO: For a collection of processes, return only those that are in a specific phase.
    pass

def has_blown_phase_duration(process) -> bool:
    # TODO: Determine if a process has blown its phase duration. (Not sure what this means or how to calculate at moment.)
    pass 
