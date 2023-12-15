# Background Rules

TODO delete background rules before publication

**Proposed Collaboration Structure and Rules**
TODO Discuss ✔️
TODO Consensus ✔️

1. For purposes of this sprint, please use a new branch for every new edit session. Naming Convention: `edit/name/date/brief-description`, e.g. this one will be `edit-main/ock/dec-13/create-README` 
2. Small pull requests are preferable, so that editing decisions are independent. 
3. Each tags the other as reviewer for every pull request. Please do not commit directly to main. 
4. Branches are deleted after approval. 
5. For async discussion, open an Issue in GitHub **and** signal in Slack. 
6. Ideas for things that need to be included but not sure where go in comments (like this one). Please include TODO in the comment; everything should have an action as to what needs to be completed to consider it final.
7. Once a TODO is completed, please delete the comment. 
8. Final editor (likely Jakob) is responsible for ensuring all TODOs are removed prior to publication. 

**Document Thoughts**
TODO Discuss ✔️
TODO Consensus ✔️

1. Of the READMEs I considered, I liked [Risk Adjusted Bonding Curves](https://github.com/BlockScience/Risk-Adjusted-Bonding-Curves) the best. 
2. 8 like lots of hyperlinks, images, code blocks, etc. 
3. Use hyperlinks within the document for ease of navigation. 
4. Let's put technical things like "How to Install cadCAD" towards the end. My preference is to write primarily for the two extremes: the reader who won't install the model, and the one who already knows how to do so. 
]: #

[
**Proposed Main Document Outline**
TODO Discuss ✔️
TODO Reach Consensus ✔️

# 🏴‍☠️🐙Actual Document Begins Here

# Title TBD 

## Introduction

TODO approve as acceptable
TODO approve as final

This repository provides a cadCAD simulation model of the Aztec system, focusing on the design and implementation of the Fernet Sequencer Selection Protocol. The goal of the model is to understand the effect of design parameters and agent behaviors on the health of the Aztec network, as measured through various Key Performance Indicators (KPIs).

This document provides:
* an overview of the system under consideration, focussing on the Sequencer Selection Protocol "Fernet"
* mathematical and software specifications for the cadCAD simulation model for the system, and
* information about how to use the model. 

## Overview of Aztec System

TODO approve as acceptable
TODO approve as final 

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

* *Users*, who create transactions that they wish to have inluded in the network. 
* *Nodes*, who propagate information on the network.
* *Sequencers*, who are responsible for structuring the transactions into blocks.
* *Provers*, who are responsible for providing the necessary proofs to accompany a block.
* *Protocol*, describing the algorithms by which various computational decisions regarding the network's state are made (e.g. which Sequencer is selected for the Proposal phase).

#### Phases

TODO approve as acceptable
TODO approve as final

The process of performing Aztec's fundamental activities proceeds in a few well-defined phases.

**Ongoing Processes**
* Sequencers make the decision to (un-)stake funds with the network, making themselves (in-)eligible to be selected in the Selection phase after a defined (de-)activation period. 
* Information is propagated through the network, with Nodes collecting information in their mempools, receiving information through both public ("public mempool") and private ("private mempool") means.

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

# Note: Finalization Phase commented out, as not needed anymore.
# **Phase 5 (Finalization Phase)**
# A final L1 transaction is needed to finalize the rollup block. This pays out rewards to Sequencer and Prover. 

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

#### Purpose of Model

A healthy Aztec network will have reliable throughput, consistently recording a sufficiently large number of its user's transactions on the underlying Layer 1. Our simulation model is intended to offer insight into how the Aztec network could perform in a variety of situations. Of particular interest are situations where the network's Agents act in ways that are not in the best interests of the network. Network agents may be unable to perform their role in a specific moment, due to either simple inability or economic incentives. It can also be used to explore the impact of L1 actors, who may be inclined to censor Aztec transactions. This insight can aid decision-makers in the Aztec network with respect to system attributes, including: economic incentive structure, high-risk scenarios to monitor, and other important questions. 

## Model Overview

TODO approve as acceptable
TODO approve as final

The simulation model is written in cadCAD. (TODO how to describe cadCAD?) In this section we will describe the variables and parameters recorded in the simulation.  We will also describe how various aspects of the cadCAD model structure correspond to specific parts of the Aztec system in general, and the Fernet model in particular. 

### Model Variables

All variables of the Aztec system recorded in the model are implemented in an `AztecModelState` class. The model has the following attributes: 

TODO bullet point list of attributes
* `example_var`: an example of a variable that a model might have

### Model  Parameters

Parameters represent aspects of the simulation which are fixed before the beginning of a single model run. 

## Model Overview 

### Partial State Update Blocks 

### Policies

### State Update Functions



<a name="overview-of-aztec-system"></a>


## Technical Details 
### How to Install cadCAD
### Project Directory Structure

## Future Work

## References 
may be unnecessary due to hyperlinks
-->

<--

 # Raw Materials 
TODO Take relevant parts from this earlier draft below and use it to fill in the final draft. 

An earlier draft. Definitely useful as raw materials for the final. 

This document is intended to provide additional documentation on the approach and decisions behind our model of the Aztec network. 

## Overview 
 
This repository provides a cadCAD model of the Aztec system, focusing on the design and implementation of the Fernet Sequencer Selection Protocol. The goal of the model is to understanding the effect of design parameters on various Key Performance Indicators (KPIs) under a wide range of possible scenarios. This document provides an overview of the system under consideration, the mathematical and software specifications of a simulation model for the system, and results of the research undertaken with this model. 

## Overview of Aztec Network

The stated goal of [Aztec Network](https://aztec.network/) is "A no-compromises privacy-first Layer 2 on Ethereum." To achieve this goal, Aztec uses zero-knowledge infrastructure to publish summaries of Layer 2 blocks on the Ethereum blockchain. Fulfillment of these goals depends on performance of various agents through specific processes, described below. 



## Overview of System

This section is in progress.

### System Goals 

The primary system goal is to provide a reliable source of L2 blockspace, offering both performance and privacy. The issue is that these two goals are often in tension. 

### System Parameters
These are the sliders (continuous) and switches (discrete) that can impact the system response to user behavior. 

**TODO** 

### KPIs

TODO: Describe KPIs. Be sure that they are not exogeneous variables. 

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

]: #


 
