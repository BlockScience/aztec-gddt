from typing import Annotated, TypedDict, Union, NamedTuple, Optional
from dataclasses import dataclass
from enum import IntEnum, Enum, auto
from math import floor

# Units

L1Blocks = Annotated[int, 'blocks']  # Number of L1 Blocks (time dimension)
L2Blocks = Annotated[int, 'blocks']  # Number of L2 Blocks (time dimension)
ContinuousL1Blocks = Annotated[float, 'blocks']  # (time dimension)
Seconds = Annotated[int, 's']
Probability = Annotated[float, 'probability']
Tokens = Annotated[float, 'tokens']  # Amount of slashable tokens

ProcessUUID = Annotated[object, 'uuid']
SequencerUUID = Annotated[object, 'uuid']
ProposalUUID = Annotated[object, 'uuid']


class EventCategories(Enum):
    """
    Pattern for event naming: {time}_{agent}_{desc}
    RT: Real Time
    L1T: L1 Blocks Time.
    """
    # Block process related events
    # Implemented through the `Process` dataclass
    # Triggers block process transition from 0->1
    L1T_protocol_init_block_process = auto()
    # Triggers block process transition 1->2
    L1T_protocol_finish_proposal_phase = auto()

    # Proposal related events
    # Implemented through the `Proposal` dataclass
    L1T_proposer_submit_proposal = auto()

    # Leading sequencer related events
    # Implemented through the `Process` dataclass
    # Triggers block process transition from 2-> 3 or -1
    L1T_lead_submit_block_content = auto()
    RT_lead_reveal_tx_proofs = auto()
    # Proving Network sends rollup proof to lead
    RT_prover_submit_rollup_proof = auto()
    # Triggers block process transition from  3-> 4 or -2
    L1T_lead_submit_rollup_proof = auto()
    # Triggers block process transition from  4-> 5 or -3
    L1T_lead_submit_finalization_tx = auto()

    # Misc
    # Implemented through the `Process` dataclass
    RT_nonlead_transition_state = auto()


class Event(NamedTuple):
    time: ContinuousL1Blocks
    type: EventCategories

# Types for representing entities


class SelectionPhase(IntEnum):  # XXX
    # Expected phases
    pending_proposals = 1
    pending_reveal = 2
    pending_commit_proof = 3
    pending_rollup_proof = 4
    pending_finalization = 5
    finalized = 6

    # Non-expected phases
    skipped = -1
    finalized_without_rewards = -2  # XXX
    proof_race = -3


@dataclass
class Process:
    uuid: ProcessUUID
    phase: SelectionPhase
    leading_sequencer: Optional[SequencerUUID]
    uncle_sequencers: Optional[list[SequencerUUID]]

    current_phase_init_time: L1Blocks
    duration_in_current_phase: L1Blocks

    proofs_are_public: bool
    block_content_is_revealed: bool
    commit_proof_is_put_down: bool #Commitment bond is put down / rename from proof 
    rollup_proof_is_commited: bool
    finalization_tx_is_submitted: bool
    process_aborted: bool
    #TODO: Think about having "global" param for minimum stake in here to make it dynamically updateable per L2 block 


@dataclass
class Sequencer():  # XXX
    staked_amount: Tokens

    def slots(self, tokens_per_slot):
        return floor(self.staked_amount / tokens_per_slot)

    # TODO:
    # discuss what is an Sequencer on our model
    # discuss how to derive proposal scores - each sequencer a random value and calculate score for each per round?
    # discuss how to separate general users (Provers mainly) and sequencers -> general class -> sequencers inherit from it 


@dataclass
class Proposal():
    """
    NOTE: Instantiation of this class can be understood as a 
    L1T_proposer_submit_proposal event.
    """
    # Skipping having a Process UUID as the proposals container
    # already uses it as a key.
    uuid:  ProposalUUID
    proposer_uuid: SequencerUUID
    score: float
    submission_time: ContinuousL1Blocks
    #TODO: add bond_uiid: /generaluserUUID 


SelectionResults = dict[ProcessUUID, tuple[Proposal, list[Proposal]]]

# TODO: commit_proof aka Prover Commitment Bond Object -> tracking bond UUID (might be different from sequencer UUID, bond amount) 

# Definition for simulation-specific types
class AztecModelState(TypedDict):
    # Time progression
    time_l1: L1Blocks
    delta_l1_blocks: L1Blocks

    # Metrics
    finalized_blocks_count: int

    # Global State
    interacting_users: list[Sequencer]
    current_process: Process

    # Flattened Meso State
    proposals: dict[ProcessUUID, list[Proposal]]

    # TODO: should L1/Gossip/RT events be a global or meso state?
    # How are they defined in terms of types?
    events: list[Event]


class AztecModelParams(TypedDict):
    label: str  # XXX
    timestep_in_blocks: L1Blocks  # XXX

    
    uncle_count: int

    # Phase Durations
    phase_duration_proposal: L1Blocks
    phase_duration_reveal: L1Blocks
    phase_duration_commit_proof: L1Blocks
    phase_duration_rollup: L1Blocks
    phase_duration_finalize: L1Blocks
    phase_duration_race: L1Blocks

    stake_activation_period: L1Blocks  # XXX
    unstake_cooldown_period: L1Blocks  # XXX

    # Behavioral Parameters
    # XXX In reveal phase, lead might not reveal content
    block_content_reveal_probability: Probability
    # XXX If lead does not reveal tx proofs, Provers can't do their work
    tx_proof_reveal_probability: Probability
    # XXX If Provers don't send back rollup proof, lead can't submit
    rollup_proof_reveal_probability: Probability
    #TODO: probability that a bond is put up for a proposal 
