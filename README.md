# Aztec Granular Design Digital Twin Model

**Last Updated:** Nov 17 2023 by Octopus :octopus:

**INTERNAL:** This document is intended for partial fulfillment of the first deliverable [here](https://hackmd.io/@blockscience/r1AXUlQb6?type=view) for Aztec Network: "Documentation on the modeling approach and decisions."  


## Overview 
 
This repository provides a cadCAD model of the Aztec system, focusing on the design and implementation of the Fernet Sequencer Selection Protocol. The goal of the model is to understanding the effect of design parameters on various Key Performance Indicators (KPIs) under a wide range of possible scenarios. This document provides an overview of the system under consideration, the mathematical and software specifications of a simulation model for the system, and results of the research undertaken with this model. 

## Overview of Aztec Network

The stated goal of [Aztec Network](https://aztec.network/) is "A no-compromises privacy-first Layer 2 on Ethereum." To achieve this goal, Aztec uses zero-knowledge infrastructure to publish summaries of Layer 2 blocks on the Ethereum blockchain. Fulfillment of these goals depends on performance of various agents through specific processes, described below. 

### Description of System

**Internal Note:** :octopus: My description of the system is based on:
* [this document](https://hackmd.io/@aztec-network/fernet)
* conversations with Jakob
* the November 13 Slack communication from Jakob regarding updates to system design. 

#### Actions

Overall, the system needs to perform the following actions:
1. Propagate transaction information amongst network participants. 
2. Package these transactions into blocks (by selecting and ordering).
3. Provide zero-knowledge proofs attesting to the validity of the block. 
4. Publish the information from Steps 2 and 3 to the Ethereum blockchain. 

#### Agents

The following agents are fundamental to understanding the network: 

* Nodes who propagate information on the network.
* Sequencers, who are responsible for structuring the transactions into blocks.
* Provers, who are responsible for providing the necessary proofs to accompany a block.
* Protocol, describing the algorithms by which various computational decisions regarding the network's state are made (e.g. which Sequencer is selected for the Proposal phase).

#### Phases

The process of performing Aztec's fundamental activities proceeds in a few well-defined phases.

**Ongoing Processes**
* Sequencers make the decision to (un)stake funds with the network, making themselves (in)eligible to be selected in the Selection phase. 
* Provers make the decision to (un)stake funds with the network, making themselves (in)eligible to do work in the Prover phase.
* Information propagates through the network, with Nodes distributing information through both public and private mempools.

**For a Specific Block** 

**Phase 0: Sequencers Determine Eligibility** 
**Step 1:** each Sequencer decides whether or not it wishes to make itself available to perform work in this Block.

**Phase 1 (Proposal Phase)**
**Step 1:** each Sequencer who self-selected in Step 0 commits a **block proposal** consisting of necessary data. 
**Step 2:** based on the proposals from Step 1, the Protocol selects a Sequencer is selected to perform the work. (It is possible that other Sequencers and their Proposals may continue as **Uncles**, available in case the selected Sequencer does not fulfill work. This is a design choice.)

**Phase 2 (Reveal Phase)**
The Sequencer reveals the contents of the block. This is necessary for the block to be valid.
:octopus: :question: If the contents are not revealed, how are potential uncles involved here?

**Phase 3 (Proving Phase)**
Provers are able to provide proofs necessary for completion of the block. 

**End Result**
At the end of this process, there are two possible outcomes.
**Success:** 
* A suitable completed L2 block is produced and is published to L1. 
* The Agents involved in work receive appropriate consequences (i.e. token emissions)
* The L2 block number is incremented by 1. 
* The system returns to Phase 1. 
**Failure:**
* A suitable completed block is not produced. (We assume any produced valid block will be published.)
* The Agents responsible for failure of work receive appropriate consequences (e.g. some portion of stake is slashed)
* The L2 block height remains the same.
* The system returns to Phase 1. 



## Overview of System

**Internal Note:** These are largely :octopus: own personal thoughts that are intended as a starting point with the other team members. 

### System Goals 

The primary system goal is to provide a reliable source of L2 blockspace, offering both performance and privacy. The issue is that these two goals are often in tension. 

### System Parameters
These are the sliders (continuous) and switches (discrete) that can impact the system response to user behavior. 

**TODO** 

### KPIs

:octopus: All of the KPIs I have are related to performance. Other KPIs could be developed related to 

* Number of Sequencers available overall 
* Number of Sequencers available per session (probability distribution or statistical knowledge)
* Rate of Failed Blocks
* Distribution of Failed Block Runs (consecutive blocks which are not produced)

## Modeling and Simulation

### Design of Model

TODO: Give a description of the phases of the model. 

The fundamental structure of a cadCAD model uses **policy functions** and **partial state update blocks** 

### Key Questions and Hypotheses

TODO: Look at key questions doc and extract what we can. 

### Scenarios

TODO: Provide scenarios. 

## Data Analysis

TODO: Provide details on data analysis currently underway. 

## References



# Software Stuff

## File structure

```
├── README.md
├── aztec_gddt: the `cadCAD` model as encapsulated by a Python Module
│   ├── __init__.py
│   ├── __main__.py
│   ├── experiment.py: Code for running experiments
│   ├── logic.py: All logic for substeps
│   ├── params.py: System parameters
│   ├── structure.py: The PSUB structure
│   └── types.py: Types used in model
├── notebooks: Notebooks for aiding in development
├── requirements-dev.txt: Dev requirements
├── requirements.txt: Production requirements
```

## What is cadCAD

### Installing cadCAD for running this repo

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