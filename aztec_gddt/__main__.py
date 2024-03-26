from aztec_gddt import default_run_args
from aztec_gddt.experiment import standard_run, psuu_exploratory_run
from aztec_gddt.utils import sim_run
from datetime import datetime
import click
import os


@click.command()
@click.option('-e', '--experiment-run', 'experiment_run',
              default=False,
              is_flag=True,
              help="Make an experiment run instead")
@click.option('-z', 'parallelize',
              default=False,
              is_flag=True,
              help="")
@click.option('-p', '--pickle', 'pickle', default=False, is_flag=True)
def main(experiment_run: bool, pickle: bool, parallelize: bool) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    prefix ='standard-run'

    if experiment_run is False:
        df = sim_run(*default_run_args)
    else:
        prefix = 'psuu-run'
        if parallelize == False:
            df = psuu_exploratory_run()
        else:
            psuu_exploratory_run(parallelize=True, N_sweep_samples=-1, use_joblib=True)
    if pickle:
        df.to_pickle(
            f"data/simulations/{prefix}-{timestamp}.pkl.gz", compression="gzip")


if __name__ == "__main__":
    main()
