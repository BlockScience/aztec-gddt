# Aztec Granular Design Digital Twin

<img src="media/cover.jpg" style="width:80%;display:block;margin-left: auto;margin-right: auto;"/>
<i style="font-size:0.6em; text-align:center;display: block;">Cactus on the Madrid Botanical Garden, Danilo L. Bernardineli, 2023</i>
<br>

## Quickstart

There are 3 main ways to interact with the model:
1. Through Python CLI: `python -m aztec_gddt`, which is going to run a pre-programmed experiment.
2. Through Jupyter Notebooks: an example can be found at `notebooks/`
3. Through tests: we use `pytest` as the testing framework.


## Introduction

This repository provides a cadCAD simulation model of the Aztec system, focusing on the design and implementation of the Fernet Sequencer Selection Protocol. The goal of the model is to understand the effect of design parameters and agent behaviors on the health of the Aztec network, as measured through various Key Performance Indicators (KPIs).

### What Is In This Document

This document provides:
* an overview of the system under consideration, focussing on the Sequencer Selection Protocol "Fernet"
* mathematical and software specifications for the cadCAD simulation model for the system, and
* information about how to use the model.

### What This Model Enables

Using the model, it is possible to run simulations and track the effect of various parameter values on final metrics and KPIs of interest. Possibilities include parameter sweeps, A/B testing, visualization of trajectories and more. 

## Model Overview

The simulation model is written in cadCAD. In this section we will record the overall structure of the cadCAD model. 

There are five important aspects of a cadCAD mode:
* Model Variables
* Model Parameters
* Partial State Update Blocks
* Policies
* State Update Functions

For more general information about the purpose each piece serves in a cadCAD model, please see [this overview](https://github.com/cadCAD-org/cadCAD/blob/master/documentation/README.md). 

### Model Variables

All variables of the Aztec system recorded in the model are implemented in an `AztecModelState` class, which can be accessed in `types.py`. 
In general, the model variables record important system aspects, including: the current stage of the process, states of individual agents engaged with the system, number of blocks produced, and token metrics like current supply and amount burned. There are also system variables for things like  the L1 time and gas fees. 

### Model Parameters

Parameters represent aspects of the simulation which are fixed before the beginning of a single model run. In this model, parameters are implemented in the `AztecModelParams` class, available in `types.py`. There are *endogeneous parameters*, corresponding to aspects of the system under Aztec's control, such as reward parameters, or duration of various production phases,. In addition, the model includes *exogeneous parameters* which correspond to necessary assumptions about agent behavior, such as probability that an agent reveals a rollup proof. 

## Technical Details 

In this section we describe how to run the model on their own computer, if desired. 

### How to Install cadCAD

#### 1. Pre-installation Virtual Environments with [`venv`](https://docs.python.org/3/library/venv.html) (Optional):
It's a good package managing practice to create an easy to use virtual environment to install cadCAD. You can use the built in `venv` package. Note that this repo requires cadCAD 0.5, which is the latest version released December 2023. 

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
Requires [>= Python 3.11](https://www.python.org/downloads/) 

**Install Using [pip](https://pypi.org/project/cadCAD/)** 
```bash
$ pip3 install cadcad
```

**Install all packages with requirement.txt**
```bash
$ pip3 install -r requirements.txt
```

### Demonstration Notebook

A basic demonstration notebook is available in `notebooks/demo-notebook.ipynb`. 

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



