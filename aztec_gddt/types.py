from typing import Annotated, TypedDict, Union
from dataclasses import dataclass


Blocks = Annotated[float, 'blocks']  # Number of days

class AztecModelState(TypedDict):
    block_time: Blocks
    delta_blocks: Blocks

class AztecModelParams(TypedDict):
    label: str
    timestep_in_blocks: Blocks

class AztecModelSweepParams(TypedDict):
    label: list[str]
    timestep_in_blocks: list[Blocks]