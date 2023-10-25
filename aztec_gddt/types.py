from typing import Annotated, TypedDict, Union
from dataclasses import dataclass
from enum import Enum, auto

L1Blocks = Annotated[float, 'blocks']  # Number of L1 Blocks
L2Blocks = Annotated[float, 'blocks'] # Number of L2 Blocks



class SelectionPhase(Enum):
    pre_proposal = 0
    proposal = 1
    block_reveal = 2
    proving = 3
    finalization = 4
    finished = 5
@dataclass
class SelectionProcess:
    expected_l2_block: L2Blocks
    current_phase: SelectionPhase



class AztecModelState(TypedDict):
    time_l1: L1Blocks
    time_l2: L2Blocks
    delta_l1_blocks: L1Blocks
    active_processes: list[SelectionProcess]

class AztecModelParams(TypedDict):
    label: str
    timestep_in_blocks: L1Blocks

class AztecModelSweepParams(TypedDict):
    label: list[str]
    timestep_in_blocks: list[L1Blocks]


