# PSuU Workflow

## Step 1. Preparation

## Step 2. Run Local Tests

## Step 3. Run a Full set of trajectories on the Cloud

1. On this project, we're using AWS SageMaker Notebooks for cloud computing on an 
`ml.m6id.32xlarge` instance (128 vCPUs, 512 GiB RAM, 2 TB SSD). 
Before the first run, some items should be prepared:
   1. Make sure that it is set up for using an AWS CodeCommit repository on which the Simulations Operator has read/write access
   2. Make sure that there's a created S3 Bucket for storing and reading the simulation results
   3. Ensure the simulation code is configured for using the S3 bucket. Precisely, the `s3.upload_file` calls in `__main__.py` should reflect the setup.
2. On the local machine, push the model's current state to the CodeCommit repository.
   1. If it is your first time you have to add in security credentials for codecommit under HTTPS Git credentials for AWS CodeCommit and use these as the username and password when pushing
3. Start the instance. Typically, it takes about ~5min to start. Open JupyeterLab when done.
4. Pull the CodeCommit repository, e.g., `git pull` You may need to `stash` or `clean` before.
5. Install requirements, e.g. `pip install -r requirements.txt.`
6. Do a small test run before doing all trajectories, eg. `python -m aztec-gddt -p -c -s 100 -r 5 -t 10`. If there are errors or warnings, try to fix them before doing the extensive run. 
7. Do the entire run, eg. `python -m aztec-gddt -p -c`. 
8. Stop the instance when done.

It can be essential to plan the experiment in terms of the trajectory coverage & budget. On commit `5b4442215`, the instance could compute `123,560` State Measurements per second or `965` State Measurements per vCPU * seconds. The formula for estimating how many state measurements a given trajectory set will comprise is `Number of Sweeps * Number of MC Runs * (Number of Timesteps + 1)`. If one does `10,000` sweeps, `10` MC runs, and `1000` timesteps, the predicted simulation time under the above numbers would be `121` minutes.

Additionally, there's a post-processing step that depends on the state measurements. Typically, it consumes 50% of the simulation time, e.g., 60 minutes.

Taken together, we would expect the simulation to take about `181` minutes.

## Step 4. Analysis & Interpretation

Files are at https://us-east-2.console.aws.amazon.com/s3/buckets/aztec-gddt

1. `python -m aztec_gddt -e -s N_SWEEP_SAMPLES -r N_RUNS -t N_TIMESTEPS -z N_PROCESSES` will run the `psuu_exploratory_run` experiment.
2. `python aztec_gddt/psuu/tensor_transform.py` will generate the relevant per-trajectory file, as per the configuration set in `data/config.json`
3. `report/Report Aztec Scenario Template.ipynb` contains the scaffold for the report.