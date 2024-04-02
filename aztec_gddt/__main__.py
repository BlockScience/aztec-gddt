from pandas import DataFrame
from aztec_gddt import default_run_args
from aztec_gddt.experiment import standard_run, psuu_exploratory_run
from aztec_gddt.utils import sim_run
from datetime import datetime
import click
import os


@click.command()
@click.option('-e', '--experiment-run',
              default=False,
              is_flag=True,
              help="Make an experiment run instead")
@click.option('-z', '--parallelize',
              default=False,
              is_flag=True)
@click.option('-s',
              '--sweep_samples',
              default=-1)
@click.option('-r',
              '--mc_runs',
              default=3)
@click.option('-t',
              '--timesteps',
              default=-500)
@click.option('-p',
              '--pickle',
              default=False,
              is_flag=True)
def main(experiment_run: bool, pickle: bool, parallelize: bool, sweep_samples: int, mc_runs: int, timesteps: int) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    prefix = 'standard-run'

    if experiment_run is False:
        df: DataFrame = sim_run(*default_run_args)
    else:
        prefix = 'psuu-run'
        if parallelize == False:
            df = psuu_exploratory_run(N_sweep_samples=sweep_samples, 
                                      N_timesteps=timesteps,
                                      N_samples=mc_runs)
        else:
            df = psuu_exploratory_run(parallelize=True,
                                      use_joblib=True,
                                      N_timesteps=timesteps,
                                      N_sweep_samples=sweep_samples, 
                                      N_samples=mc_runs)
    if pickle:
        df.to_pickle(
            f"data/simulations/{prefix}-{timestamp}.pkl.gz", compression="gzip")


if __name__ == "__main__":
    main()
