import pandas as pd
from aztec_gddt.experiment import psuu_exploratory_run
from aztec_gddt.types import Agent
import pytest as pt


N_sweep_samples = 2
N_samples = 2
N_timesteps = 100


@pt.fixture
def sim_df() -> pd.DataFrame:
    return psuu_exploratory_run(N_sweep_samples=N_sweep_samples,
                                N_samples=N_samples,
                                N_timesteps=N_timesteps,
                                parallelize_jobs=False,
                                supress_cadCAD_print=True) # type: ignore


def test_n_rows(sim_df: pd.DataFrame):
    expected_rows = (N_timesteps + 1) * N_samples * N_sweep_samples
    assert sim_df.shape[0] == expected_rows


def test_agents_stake_not_negative(sim_df: pd.DataFrame):
    _df = sim_df.set_index(["subset", "run", "timestep"])
    agents_per_timestep: pd.Series[list[Agent]] = _df.agents # type: ignore
    for index, agents in agents_per_timestep.items():
        for agent_name, agent in agents.items():
            assert agent.staked_amount >= 0, f"Assert failed for {agent_name=} at (subset, run, timestep)={index}"