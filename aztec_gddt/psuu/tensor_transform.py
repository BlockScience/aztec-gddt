import pandas as pd # type: ignore
from typing import Iterable
import aztec_gddt.metrics as m
import aztec_gddt.plot_tools as pt
from tqdm.auto import tqdm # type: ignore

TensorPerTrajectory = object


KPIs = {"proportion_race_mode": m.find_proportion_race_mode,
                      "find_proportion_slashed_due_to_prover": m.find_proportion_slashed_due_to_prover,
                       "proportion_slashed_prover": m.find_proportion_slashed_due_to_sequencer,
                       "proportion_skipped": m.find_proportion_skipped,
                       "find_average_duration_finalized_blocks": m.find_average_duration_finalized_blocks,
                       "find_stddev_duration_finalized_blocks": m.find_stddev_duration_finalized_blocks,
                       "find_average_duration_nonfinalized_blocks": m.find_average_duration_nonfinalized_blocks,
                       "find_stddev_duration_nonfinalized_blocks": m.find_stddev_duration_nonfinalized_blocks
                       }


COLS_TO_DROP = ['simulation', 'subset', 'run']


def timestep_files_to_trajectory(per_timestep_tensor_paths: list[str]) -> Iterable[TensorPerTrajectory]:
    for path in tqdm(per_timestep_tensor_paths):
        df_per_timestep = pd.read_pickle(path)
        df_per_trajectory = pt.extract_df(m.process_df(df_per_timestep), trajectory_kpis=KPIs, cols_to_drop=COLS_TO_DROP)
        yield df_per_trajectory
