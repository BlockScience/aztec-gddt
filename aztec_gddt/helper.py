from aztec_gddt.types import *
import numpy as np





def proposals_from_tx(transactions: dict[TxUUID, TransactionL1]) -> dict[TxUUID, Proposal]:
    """
    Selects all proposals from the transactions state variable.
    """
    return {k: v for k, v in transactions.items()
            if type(v) == Proposal}


#######################################
## Helper functions for Selection    ##
#######################################


def select_processes_by_state(processes: list[Process], phase_to_select: SelectionPhase) -> list[Process]:
    selected_processes = [proc for proc in processes if proc.phase == phase_to_select]
    return selected_processes


def has_blown_phase_duration(process) -> bool:
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




def max_phase_duration(p: AztecModelParams) -> L1Blocks:
    return (p['phase_duration_proposal_max_blocks'] + 
            p['phase_duration_reveal_max_blocks'] + 
            p['phase_duration_commit_bond_max_blocks'] + 
            p['phase_duration_rollup_max_blocks'])




def rewards_to_sequencer(p: AztecModelParams) -> Percentage:
    return (1 - p['rewards_to_provers'] - p['rewards_to_relay'])