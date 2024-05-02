from aztec_gddt.experiment import psuu_exploratory_run
from datetime import datetime
import click
import logging
from pathlib import Path
from multiprocessing import cpu_count
from aztec_gddt import DEFAULT_LOGGER
from aztec_gddt.psuu import tensor_transform as tt
import boto3 # type: ignore
import os

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
              default=5)
@click.option('-t',
              '--timesteps',
              default=1_000)
@click.option('-p',
              '--process',
              default=False,
              is_flag=True)
@click.option('-c',
              '--upload_to_cloud',
              default=False,
              is_flag=True)
@click.option('--no_parallelize',
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
def main(process: bool,
         n_jobs: int,
         sweep_samples: int,
         mc_runs: int,
         timesteps: int,
         log_level: str,
         upload_to_cloud: bool,
         no_parallelize: bool) -> None:
    
    CLOUD_BUCKET_NAME = 'aztec-gddt'

    if upload_to_cloud:
        session = boto3.Session()
        s3 = session.client("s3")

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
                         parallelize_jobs=~no_parallelize,
                         supress_cadCAD_print=True,
                         output_path=str(output_path),
                         timestep_tensor_prefix=timestep_tensor_prefix,
                         base_folder=folder,
                         cloud_stream=upload_to_cloud)
    
    if upload_to_cloud:
        files: list[str] = os.listdir(output_path)
        for f in files:
            s3.upload_file(str(output_path / f),
                           CLOUD_BUCKET_NAME,
                           str(Path(folder) / f))

    if process is True:
        traj_file_name = "trajectory_tensor.csv.zip"
        traj_output_path = str(output_path / traj_file_name)
        tt.process_folder_files(
            output_path, timestep_tensor_prefix, traj_output_path)
        
        if upload_to_cloud:
            s3.upload_file(str(traj_output_path),
                           CLOUD_BUCKET_NAME,
                           str(Path(folder) / traj_file_name))
    else:
        pass


if __name__ == "__main__":
    main()
