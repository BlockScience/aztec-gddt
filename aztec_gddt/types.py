from typing import Annotated, TypedDict, Union
from dataclasses import dataclass
from enum import Enum, auto
from math import floor

## Units

L1Blocks = Annotated[int, 'blocks']  # Number of L1 Blocks (time dimension)
L2Blocks = Annotated[int, 'blocks'] # Number of L2 Blocks (time dimension)
Seconds = Annotated[int, 's']
Probability = Annotated[float, 'probability']
Tokens = Annotated[float, 'tokens'] # Amount of slashable tokens

ProcessUUID = Annotated[object, 'uuid']
SequencerUUID = Annotated[object, 'uuid']
ProposalUUID = Annotated[object, 'uuid']


Tokens = Annotated[float, 'tokens']


class Events(Enum):
    """
    Pattern for event naming: {time}_{agent}_{desc}
    RT: Real Time
    L1T: L1 Blocks Time
    """
    L1T_protocol_init_block_process = auto() # Triggers block process transition from 0->1
    L1T_protocol_finish_proposal_phase = auto() # Triggers block process transition 1->2

    # Proposal related events
    L1T_proposer_submit_proposal = auto() # OK 

    # Leading sequencer related events
    L1T_lead_submit_block_content = auto() # Triggers block process transition from 2-> 3 or -1
    RT_lead_reveal_tx_proofs = auto() 
    RT_prover_submit_rollup_proof = auto() # Proving Network sends rollup proof to lead
    L1T_lead_submit_rollup_proof = auto()  # Triggers block process transition from  3-> 4 or -2
    L1T_lead_submit_finalization_tx = auto() # Triggers block process transition from  4-> 5 or -3 

    # Misc
    RT_nonlead_transition_state = auto() 

## Types for representing entities
class SelectionPhase(Enum): # XXX
    # Expected phases
    pending_proposals = 1
    pending_reveal = 2
    pending_rollup_proof = 3
    pending_finalization = 4
    finalized = 5

    # Non-expected phases
    skipped = -1
    reorg = -2
    finalized_without_rewards = -3 # XXX

@dataclass
class SelectionProcess:
    uuid: ProcessUUID 
    current_phase: SelectionPhase
    leading_sequencer: SequencerUUID
    uncle_sequencers: set[SequencerUUID]

    current_phase_init_time: L1Blocks
    duration_in_current_phase: L1Blocks

    proofs_are_public: bool
    process_aborted: bool
    


@dataclass
class Sequencer(): # XXX
    staked_amount: Tokens

    def slots(self, tokens_per_slot):
        return floor(self.staked_amount / tokens_per_slot)



    # TODO: discuss what is an Sequencer on our model


@dataclass
class Proposal():
    # Skipping having a Process UUID as the proposals container
    # already uses it as a key.
    uuid:  ProposalUUID
    proposer_uuid: SequencerUUID
    score: float
    submission_time: L1Blocks


## Definition for simulation-specific types
class AztecModelState(TypedDict):
    # Time progression
    time_l1: L1Blocks
    delta_l1_blocks: L1Blocks

    # Metrics
    finalized_blocks_count: int

    # Global State
    interacting_users: list[Sequencer]
    # Order matters. lastest elements are newer processes
    block_processes: list[SelectionProcess] 

    # Flattened Meso State
    proposals: dict[ProcessUUID, list[Proposal]]


    # TODO: should L1/Gossip/RT events be a global or meso state?
    # How are they defined in terms of types?

class AztecModelParams(TypedDict):
    label: str# XXX
    timestep_in_blocks: L1Blocks# XXX

    stake_activation_period: L1Blocks# XXX
    unstake_cooldown_period: L1Blocks# XXX

    # Behavioral Parameters
    block_reveal_probability: Probability# XXX



