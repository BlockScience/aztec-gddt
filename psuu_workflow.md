1. `python -m aztec_gddt -e -s N_SWEEP_SAMPLES -r N_RUNS -t N_TIMESTEPS -z N_PROCESSES` will run the `psuu_exploratory_run` experiment.
2. `python aztec_gddt/psuu/tensor_transform.py` will generate the relevant per-trajectory file, as per the configuration set in `data/config.json`
3. `report/Report Aztec Scenario Template.ipynb` contains the scaffold for the report.