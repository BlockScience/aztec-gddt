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
@click.option('-p', '--pickle', 'pickle', default=False, is_flag=True)
def main(experiment_run: bool, pickle: bool) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    if experiment_run is False:
        df = sim_run(*default_run_args)
    else:
        df = psuu_exploratory_run()
    if pickle:
        df.to_pickle(
            f"data/simulations/multi-run-{timestamp}.pkl.gz", compression="gzip")


if __name__ == "__main__":
    main()
