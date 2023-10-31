from typing import Annotated, TypedDict, Union
from dataclasses import dataclass
from enum import Enum, auto

L1Blocks = Annotated[int, 'blocks']  # Number of L1 Blocks (time dimension)
L2Blocks = Annotated[int, 'blocks'] # Number of L2 Blocks (time dimension)

Probability = Annotated[float, 'probability']
Tokens = Annotated[float, 'tokens'] # Amount of slashable tokens



class SelectionPhase(Enum):
    pre_proposal = 0
    proposal = 1
    reveal = 2
    proving = 3
    finalization = 4
    done = 5

@dataclass
class SelectionProcess:
    expected_l2_block: L2Blocks
    current_phase: SelectionPhase
    duration_in_current_phase: L1Blocks


@dataclass
class Sequencer():
    stake_amount: Tokens
    # TODO: discuss what is an Sequencer on our model

@dataclass
class Proposal():
    relevant_l2_block: L2Blocks
    score: float


class AztecModelState(TypedDict):
    time_l1: L1Blocks
    time_l2: L2Blocks
    delta_l1_blocks: L1Blocks
    active_processes: list[SelectionProcess]

class AztecModelParams(TypedDict):
    label: str
    timestep_in_blocks: L1Blocks

    stake_activation_period: L1Blocks
    unstake_cooldown_period: L1Blocks

    # Behavioral Parameters
    block_reveal_probability: Probability

class AztecModelSweepParams(TypedDict):
    label: list[str]
    timestep_in_blocks: list[L1Blocks]


