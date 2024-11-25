import numpy as np
import pandas as pd
from typing import List

from aztec_gddt.types import *


def proposals_from_tx(
    transactions: dict[TxUUID, TransactionL1]
) -> dict[TxUUID, Proposal]:
    """
    Selects all proposals from the transactions state variable.
    """
    return {k: v for k, v in transactions.items() if type(v) == Proposal}


#######################################
## Helper functions for Selection    ##
#######################################


def select_processes_by_state(
    processes: list[Process], phase_to_select: SelectionPhase
) -> list[Process]:
    selected_processes = [proc for proc in processes if proc.phase == phase_to_select]
    return selected_processes


def has_blown_phase_duration(process) -> bool:
    return False


#######################################
##  Censorship functions             ##
#######################################


def build_censor_series_from_data(
    data: pd.DataFrame, index_range, column_name: str, censoring_list: List[str]
):
    """
    Given DataFrame and input range and list of censoring builders, return a time series
    describing censoring behavior.
    """
    indexed_data = data.iloc[index_range]
    censored_series = indexed_data[column_name].apply(lambda x: x in censoring_list)

    return censored_series


#######################################
## Helper functions for decisions    ##
#######################################


def bernoulli_trial(probability: float) -> bool:
    if probability > 1 or probability < 0:
        raise ValueError(
            f"Probability must be be between 0 and 1, was given {probability}."
        )

    # TODO: refactor so that the seed is properly tracked
    rng = np.random.default_rng()
    rand_num = rng.uniform(low=0, high=1)
    hit = rand_num <= probability

    return hit


def total_phase_duration(p: AztecModelParams) -> L1Blocks:
    return (
        p["phase_duration_proposal_max_blocks"]
        + p["phase_duration_reveal_max_blocks"]
        + p["phase_duration_commit_bond_max_blocks"]
        + p["phase_duration_rollup_max_blocks"]
    )


def rewards_to_sequencer(p: AztecModelParams) -> Percentage:
    return 1 - p["rewards_to_provers"] - p["rewards_to_relay"]


def trial_probability(
    n_trials: int, sample_probability: Probability = 0.99
) -> Probability:
    """
    Calculates the probability for an individual trial.
    """
    return 1 - (1 - sample_probability) ** (1 / n_trials)


def check_for_censorship(params: AztecModelParams, state: AztecModelState) -> bool:
    time_l1 = state["time_l1"]

    # XXX: If there's no data, then assume that is uncensored.
    block_is_uncensored = not (
        params["censorship_series_builder"].get(time_l1, True)
        or params["censorship_series_validator"].get(time_l1, True)
    )

    return block_is_uncensored


def value_from_param_timeseries_suf(
    params, state, param_key, var_value  # -> tuple[Any, Any]
):
    time_series = params[param_key]

    assert state["time_l1"] < len(
        time_series
    ), "The time_l1 of {} is out of bounds for the time series of {}".format(
        state["time_l1"], param_key
    )

    return time_series[state["time_l1"]]
