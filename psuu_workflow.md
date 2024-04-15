# PSuU Workflow



## Step 1. Preparation


## Step 2. Run Local Tests


## Step 3. Run Full set of trajectories on the Cloud

1. On this project, we're using AWS SageMaker Notebooks for cloud compute on an 
`ml.m6id.32xlarge` instance (128 vCPUs, 512 GiB RAM, 2 TB SSD). 
Before the first run, some items should be prepared:
   1. Make sure that it is set-up for using a AWS CodeCommit repository on which the Simulations Operator has read/write access
   2. Make sure that there's an created S3 Bucket for storing and reading the simulations results
   3. Make sure that the simulation code is configured for using the S3 bucket. In specific, the `s3.upload_file` calls in `__main__.py` should be reflective of the setup.
2. On the local machine, push the current state of the model to the CodeCommit repository.
3. Start the instance. Typically takes about ~5min to start. Open JupyeterLab when done.
4. Pull the CodeCommit repository, eg, `git pull`. You may need to `stash` or `clean` before.
5. Install requirements, eg. `pip install -r requirements.txt`
6. Do a small test run before doing all trajectories, eg. `python -m aztec-gddt -p -c -s 100 -r 5 -t 10`. If there are errors or warnings, you could try to fix before doign the large run. 
7. Do the full run, eg. `python -m aztec-gddt -p -c`. 
8. Stop the instance when done.

## Step 4. Analysis & Interpretation




1. `python -m aztec_gddt -e -s N_SWEEP_SAMPLES -r N_RUNS -t N_TIMESTEPS -z N_PROCESSES` will run the `psuu_exploratory_run` experiment.
2. `python aztec_gddt/psuu/tensor_transform.py` will generate the relevant per-trajectory file, as per the configuration set in `data/config.json`
3. `report/Report Aztec Scenario Template.ipynb` contains the scaffold for the report.