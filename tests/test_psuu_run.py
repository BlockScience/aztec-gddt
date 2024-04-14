import pandas as pd
from aztec_gddt.experiment import psuu_exploratory_run
from aztec_gddt.types import Agent
import pytest as pt
import pandera as pa


@pt.fixture(scope="module", params=[(10, 2, 1_000), (500, 1, 20)])
def sim_df(request) -> pd.DataFrame:
    (N_sweep_samples, N_samples, N_timesteps) = request.param
    return psuu_exploratory_run(N_sweep_samples=N_sweep_samples,
                                N_samples=N_samples,
                                N_timesteps=N_timesteps,
                                parallelize_jobs=False,
                                supress_cadCAD_print=True)  # type: ignore

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


def test_skipped_fraction(sim_df: pd.DataFrame):
    fig_df = sim_df.copy()
    fig_df['process_order'] = fig_df.current_process.map(lambda x: x.phase.value if x is not None else None)
    fig_df['process_label'] = fig_df.current_process.map(lambda x: x.phase.name if x is not None else None)
    assert len(fig_df.process_label.dropna().unique()) > 2


def test_token_conservation(sim_df: pd.DataFrame):
    id_cols = ["simulation", "subset", "run"]
    for i, gdf in sim_df.groupby(["simulation", "subset", "run"]):
        tdf = gdf.set_index(id_cols).query('timestep > 2').token_supply.apply(lambda x: pd.Series(x.__dict__)).diff()
        assert ((tdf['circulating'] + tdf['staked'] + tdf['burnt'] - tdf['issued']).dropna().abs() < 1e-6).mean() == 1.0


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
