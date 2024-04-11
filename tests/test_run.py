import pandas as pd
from aztec_gddt.experiment import standard_run
from aztec_gddt.types import Agent
import pytest as pt
import pandera as pa
@pt.fixture
def sim_df() -> pd.DataFrame:
    return standard_run()  # type: ignore

# def test_n_rows(sim_df: pd.DataFrame):
#     expected_rows = (N_timesteps + 1) * N_samples * N_sweep_samples
#     assert sim_df.shape[0] == expected_rows


def test_agents_stake_not_negative(sim_df: pd.DataFrame):
    _df = sim_df.set_index(["subset", "run", "timestep"])
    agents_per_timestep: pd.Series[dict[Agent]] = _df.agents  # type: ignore
    for index, agents in agents_per_timestep.items():
        for agent_name, agent in agents.items():
            assert agent.staked_amount >= 0, f"Assert failed for {agent_name=} at (subset, run, timestep)={index}"


def test_agents_balance_not_negative(sim_df: pd.DataFrame):
    _df = sim_df.set_index(["subset", "run", "timestep"])
    agents_per_timestep: pd.Series[dict[Agent]] = _df.agents  # type: ignore
    for index, agents in agents_per_timestep.items():
        for agent_name, agent in agents.items():
            assert agent.balance >= 0, f"Assert failed for {agent_name=} at (subset, run, timestep)={index}"


def test_schema(sim_df: pd.DataFrame):

    # NOTE: this is incomplete
    schema = pa.DataFrameSchema({
        "timestep": pa.Column(int, checks=[pa.Check(lambda x: x >= 0), pa.Check(lambda x: x.mean() > 0)]),
        "time_l1": pa.Column(int, checks=[pa.Check(lambda x: x >= 0), pa.Check(lambda x: x.mean() > 0)]),


        "total_rewards_provers": pa.Column(float, checks=[pa.Check(lambda x: x >= 0)]),
        "total_rewards_sequencers": pa.Column(float, checks=[pa.Check(lambda x: x >= 0)]),
        "total_rewards_relays": pa.Column(float, checks=[pa.Check(lambda x: x >= 0)]),
        "slashes_to_provers": pa.Column(float, checks=[pa.Check(lambda x: x >= 0)]),
        "slashes_to_sequencers": pa.Column(float, checks=[pa.Check(lambda x: x >= 0)]),
        # "gas_fee_l1": pa.Column(int, checks=[pa.Check(lambda x: x >= 0)]),
        # "gas_fee_blob": pa.Column(int, checks=[pa.Check(lambda x: x >= 0)]),

        "finalized_blocks_count": pa.Column(int, checks=[pa.Check(lambda x: x >= 0)]),
        "cumm_block_rewards": pa.Column(float, checks=[pa.Check(lambda x: x >= 0)]),
        "cumm_fee_cashback": pa.Column(float, checks=[pa.Check(lambda x: x >= 0)]),
        "cumm_burn": pa.Column(float, checks=[pa.Check(lambda x: x >= 0)]),

    })

    schema.validate(sim_df)
