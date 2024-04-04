from aztec_gddt.experiment import psuu_exploratory_run
from datetime import datetime
import click
import logging
from pathlib import Path
from multiprocessing import cpu_count
from aztec_gddt import DEFAULT_LOGGER
from aztec_gddt.psuu import tensor_transform as tt

logger = logging.getLogger(DEFAULT_LOGGER)
log_levels = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


@click.command()
@click.option('-z', '--parallelize', 'n_jobs',
              default=cpu_count())
@click.option('-s',
              '--sweep_samples',
              default=-1)
@click.option('-r',
              '--mc_runs',
              default=3)
@click.option('-t',
              '--timesteps',
              default=500)
@click.option('-p',
              '--process',
              default=False,
              is_flag=True)
@click.option(
    "-l",
    "--log-level",
    "log_level",
    type=click.Choice(list(log_levels.keys()), case_sensitive=False),
    default="info",
    help="Set the logging level.",
)
def main(process: bool, n_jobs: int, sweep_samples: int, mc_runs: int, timesteps: int, log_level: str) -> None:

    logger.setLevel(log_levels[log_level])

    timestamp = datetime.now().strftime("%Y-%m-%dT%H%M%SZ%z")
    prefix = 'psuu_run'
    folder_path = "data/simulations/"
    folder = f'{prefix}_{timestamp}'

    timestep_tensor_prefix = f"timestep_tensor" 
    output_path: Path = Path(folder_path) / folder
    output_path.mkdir(parents=True, exist_ok=True)

    psuu_exploratory_run(N_jobs=n_jobs,
                         N_timesteps=timesteps,
                         N_sweep_samples=sweep_samples,
                         N_samples=mc_runs,
                         supress_cadCAD_print=True,
                         output_path=output_path,
                         timestep_tensor_prefix=timestep_tensor_prefix)

    if process is True:
        traj_output_path = str(output_path / f"trajectory_tensor.csv.zip")
        tt.process_folder_files(output_path, timestep_tensor_prefix, traj_output_path)
    else:
        pass


if __name__ == "__main__":
    main()
