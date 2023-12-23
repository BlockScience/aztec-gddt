# Aztec Granular Design Digital Twin

<img src="media/cover.jpg" style="width:80%;display:block;margin-left: auto;margin-right: auto;"/>
<i style="font-size:0.6em; text-align:center;display: block;">Cactus on the Madrid Botanical Garden, Danilo L. Bernardineli, 2023</i>
<br>

## Quickstart

There are 3 main ways to interact with the model:
1. Through Python CLI: `python -m aztec_gddt`, which is going to run a pre-programmed experiment.
2. Through Jupyter Notebooks: some examples can be found at `notebooks/`
3. Through tests: we use `pytest` as the testing framework.


## Introduction

This repository provides a cadCAD simulation model of the Aztec system, focusing on the design and implementation of the Fernet Sequencer Selection Protocol. The goal of the model is to understand the effect of design parameters and agent behaviors on the health of the Aztec network, as measured through various Key Performance Indicators (KPIs).

This document provides:
* an overview of the system under consideration, focussing on the Sequencer Selection Protocol "Fernet"
* mathematical and software specifications for the cadCAD simulation model for the system, and
* information about how to use the model. 

## Overview of Aztec System 

The stated goal of [Aztec Network](https://aztec.network/) is "A no-compromises privacy-first Layer 2 on Ethereum."  Aztec uses zero-knowledge infrastructure and economic incentives to publish Layer 2 (L2) transactions, batched into single zero-knowledge "rollup" proofs, on the Layer 1 (L1) Ethereum blockchain. Achieving this goal sustainably and reliably without centralized intermediaries depends on Agents playing different roles through a sequence of phases. 

The decentralized and anonymous nature of Aztec creates risks that participants in the network may be either unreliable or malicious in intent. 

### Description of System

Our description of the system is based on [the Fernet documentation](https://hackmd.io/@aztec-network/fernet) and discussions with Aztec Labs and colleagues. 

#### Actions

Overall, the real system needs to perform the following actions:
1. Propagate transaction information amongst network participants. 
2. Package these transactions into blocks (by selecting and ordering).
3. Provide batch zero-knowledge proofs attesting to the validity of the entire block. 
4. Publish the information from Steps 2 and 3 to the Ethereum blockchain.

#### Agents

The following agents are fundamental to understanding the network: 

* *Agents*, who create transactions that they wish to have inluded in the network. 
* *Nodes*, who propagate information on the network.
* *Sequencers*, who are responsible for structuring the transactions into blocks.
* *Provers*, who are responsible for providing the necessary proofs to accompany a block.
* *Protocol*, describing the algorithms by which various computational decisions regarding the network's state are made (e.g. which Sequencer is selected for the Proposal phase).

#### Phases

The process of performing Aztec's fundamental activities proceeds in a few well-defined phases.

**Ongoing Processes**
* Sequencers make the decision to (un-)stake funds with the network, making themselves (in-)eligible to be selected in the Selection phase after a defined (de-)activation period. 
* Information is propagated through the network, with Nodes collecting information in their mempools, receiving information through both public ("public mempool") and private ("private mempool") means. In this first version of the model, this information is naively represented with `size` of proposals (blocks). 

**For a Specific Block** 
![Aztec - Spec](https://github.com/BlockScience/aztec-gddt/assets/80513714/05746e08-97c4-46ff-979b-e3af3cd976e0)

**Phase 0: Sequencers (Un-)Stake** 
**Step 1:** Each Sequencer decides whether or not they wish to remain / make themself available to perform work for the network, requiring to wait out a defined (de-)activation period.

**Phase 1 (Proposal Phase)**
**Step 1:** Each Sequencer who has at least the minimum stake active, and is not currently waiting out a (de-)activation period, decides whether they deem their score high enough to commit a **block proposal** consisting of necessary data. 
**Step 2:** based on the proposals from Step 1, the Protocol selects the Sequencer with the highest score as selected to perform the work for this block. (It is possible that other Sequencers and their Proposals may continue as **Uncles**, available in case the selected Sequencer does not fulfill work. This is a design choice.)

**Phase 2 (Commitment Bond Phase)**
The Sequencer decides whether they want to prove the block themselves (putting down the bond), or whether they have an agreement with another Prover (or 3rd party proving marketplace) who commits to prove the block (and puts down the bond). 

**Phase 3 (Reveal Phase)**
The Sequencer reveals the contents of the block. This is necessary for the protocol to consider the block to be valid.

**Phase 4a (Proving Phase)**
The Prover computes the necessary proof(s) and commits them on L1, triggering the finalization of this block and any respective payouts. 

**Phase 4b (Proof Race Phase)**
If either no bond was put down, or the content was not revealed, the priorly chosen sequencer loses their privilege. Instead of a regular Proving Phase, anyone can now submit a valid rollup proof for any valid block (which does not have to be a proof for any priorly committed proposal). The first valid rollup proof on L1 wins, triggering finalization of this block and any respective payouts. 

**End Result**
At the end of this process, there are two possible outcomes.
**Success:** 
* A valid, completed L2 block rollup proof is produced and published to L1. 
* The Agents involved in the work receive appropriate consequences (i.e. token emissions and fee payouts, as well as portions of stake slashed in case a chosen sequencer fails their obligation resulting in race mode)
* The L2 block number is incremented by 1. 
* The system returns to Phase 1 (or in this model - to Phase 0).
**Failure:**
* A valid, completed L2 block rollup proof is not published to L1 in time.
* The Agents responsible for failure of work receive appropriate consequences (i.e. some portion of stake or commitment bond is slashed)
* The L2 block height remains the same.
* The system returns to Phase 1.

#### Purpose of this Model

A healthy Aztec network will be *lively*, consistently recording blocks on the underlying Layer 1. Additionally, it will have high *throughput*: blocks will contain a large number of transactions, according to user demand. 

Our simulation model is intended to offer insight into how the Aztec network may perform under a variety of circumstances. Of particular interest are situations where the network's Agents act in ways that are not in the best interests of the network, for economic or other reasons. Network agents may be unable to perform their role in a specific moment, due to either simple inability or economic incentives. It can also be used to explore the impact of L1 actors, who may be inclined to censor Aztec transactions. This insight can aid decision-makers in the Aztec network with respect to system attributes, including: economic incentive structure, high-risk scenarios to monitor, and other important questions. 

## Model Overview

TODO approve as acceptable
TODO approve as final
TODO how to describe cadCAD 

The simulation model is written in cadCAD. In this section we will describe the variables and parameters recorded in the simulation.  We will also describe how various aspects of the cadCAD model structure correspond to specific parts of the Aztec system in general, and the Fernet model in particular. 

There are five important aspects of a cadCAD mode:
* Model Variables
* Model Parameters
* Partial State Update Blocks
* Policies
* State Update Functions

For more general information about the purpose each piece serves in a cadCAD model, please see [this overview](https://github.com/cadCAD-org/cadCAD/blob/master/documentation/README.md). 

### Model Variables

All variables of the Aztec system recorded in the model are implemented in an `AztecModelState` class. The model has the following attributes: 

* `example_var`: an example of a variable that a model might have


**Time Progression Variables** 
* `time_l1`: the current time as measured in L1 blocks 
* `delta_l1_blocks`: TODO
* `advance_l1_blocks`: TODO

**Agents Variables** 
* `agents`: a dictionary containing IDs of agents and the agents themselves

**Process State Variables** 
* `current_process`: TODO
* `transactions`: TODO
* `gas_fee_l1`: TODO
* `gas_fee_blob`: TODO

**Metrics*
* `finalized_blocks_count`: TODO
* `cumm_block_rewards`: Tokens
* `cumm_fee_cashback`: Tokens
* `cumm_burn`: Tokens
* `token_supply`: TokenSupply

**Estimator Methods**
* `GasEstimator`: 
* `BlobGasEstimator`:
* `BaseIntEstimator`:
* `BaseFloatEstimator`:

### Model Parameters

Parameters represent aspects of the simulation which are fixed before the beginning of a single model run. 
* `example_par`: an example of a parameter that can be set

**Logistics**
* `label`: TODO
* `timestep_in_blocks`: TODO

**Economic Parameters**
* `uncle_count`: TODO
* `reward_per_block`: TODO
* `fee_subsidy_fraction`: TODO

**Time Variables** 
* `phase_duration_proposal`: TODO
* `phase_duration_reveal`: TODO
* `phase_duration_commit_bond`: TODO
* `phase_duration_rollup`: TODO
* `phase_duration_race`: TODO

**Time Periods for System Actions**
* `stake_activation_period`: TODO  # XXX
* `unstake_cooldown_period`: TODO  # XXX

**Probabilities for Agent Actions**
 * `block_content_reveal_probability`: the probability that the Lead Sequencer (does not reveal?) reveals the content. 
* `tx_proof_reveal_probability`: the probability that the Lead Sequencer (does not reveal? ) reveals their proof, thus preventing the Provers from doing their work. 
* `rollup_proof_reveal_profitability`: the probability that the provers (don't send?) send a rollup proof to the Lead Sequencer, preventing the Sequencer from submitting.
* `commit_bond_reveal_profitability`: the probability that at least one prover puts up a bond for proving, in which case the Lead Sequencer loses their privilege and we enter Race Mode. 
* `proving_marketplace_usage_probability`: TODO. NOTE: 8 think this goes here. 

**Rewards Parameters**
* `rewards_to_provers`: TODO a percentage of something
* `rewards_to_relay`: TODO a percentage of something

**Gas Threshold Parameters** 
* `gas_threshold_for_tx`: Gwei
* `blob_gas_threshold_for_tx`: Gwei

**Estimators to Use**
* `gas_estimators`: L1GasEstimators
* `tx_estimators`: UserTransactionEstimators

### Partial State Update Blocks 

### Policies

**NOTE:** 8 don't know that we need to include these 

### State Update Functions
**NOTE:** Please consider the below. 



## Technical Details 

In this section we ensure that the reader will be able to run the model on their own computer, if desired. 

### How to Install cadCAD

#### 1. Pre-installation Virtual Environments with [`venv`](https://docs.python.org/3/library/venv.html) (Optional):
It's a good package managing practice to create an easy to use virtual environment to install cadCAD. You can use the built in `venv` package.

***Create** a virtual environment:*
```bash
$ python3 -m venv ~/cadcad
```

***Activate** an existing virtual environment:*
```bash
$ source ~/cadcad/bin/activate
(cadcad) $
```

***Deactivate** virtual environment:*
```bash
(cadcad) $ deactivate
$
```

#### 2. Installation: 
Requires [>= Python 3.6](https://www.python.org/downloads/) 

**Install Using [pip](https://pypi.org/project/cadCAD/)** 
```bash
$ pip3 install cadcad
```

**Install all packages with requirement.txt**
```bash
$ pip3 install -r requirements.txt
```

### Demonstration Notebook

TODO instructions on using the notebooks to gain insight, and modifying them for experiments. 

### Project Directory Structure

```
├── README.md
├── LICENSE
├── aztec_gddt: the `cadCAD` model as encapsulated by a Python Module
│   ├── __init__.py
│   ├── __main__.py
│   ├── experiment.py: Code for running experiments
│   ├── logic.py: All logic for substeps
│   ├── params.py: System parameters
│   ├── structure.py: The PSUB structure
│   └── types.py: Types used in model
├── media: TODO images used in the repo
├── notebooks: Notebooks for aiding in development
├── tests: Tests for ensuring correct functionality
├── requirements.txt: Production requirements
```

## Future Work

-->

<--

 # Raw Materials 
TODO: Take relevant parts from this earlier draft below and use it to fill in the final draft. 
Note: Jakob took out most of below, as it was used above. 

# Software Stuff

## File structure

```
├── README.md
├── LICENSE
├── aztec_gddt: the `cadCAD` model as encapsulated by a Python Module
│   ├── __init__.py
│   ├── __main__.py
│   ├── experiment.py: Code for running experiments
│   ├── logic.py: All logic for substeps
│   ├── params.py: System parameters
│   ├── structure.py: The PSUB structure
│   └── types.py: Types used in model
├── media: TODO images used in the repo
├── notebooks: Notebooks for aiding in development
├── tests: Tests for ensuring correct functionality
├── requirements.txt: Production requirements
```




 
