from aztec_gddt.params import SINGLE_RUN_PARAMS, INITIAL_STATE
from aztec_gddt.structure import AZTEC_MODEL_BLOCKS
from aztec_gddt.utils import sim_run

def test_default_run():
    N_timesteps = 5
    N_samples = 2
    sweep_params = {k: [v] for k, v in SINGLE_RUN_PARAMS.items()}
    sim_args = (INITIAL_STATE,
                sweep_params,
                AZTEC_MODEL_BLOCKS,
                N_timesteps,
                N_samples)
    sim_df = sim_run(*sim_args)

    expected_rows = N_samples * (1 + N_timesteps)
    assert len(sim_df) == expected_rows

def test_standard_run():
    from aztec_gddt.experiment import standard_run
    df = standard_run().set_index('time_l1')