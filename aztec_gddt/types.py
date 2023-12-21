from typing import Annotated, TypedDict, Union, NamedTuple, Optional
from enum import IntEnum, Enum, auto, Flag
from math import floor
from pydantic import BaseModel, PositiveInt, FiniteFloat
from typing import Callable
from pydantic.dataclasses import dataclass
from uuid import uuid4
from typing import Sequence

# Units

L1Blocks = Annotated[int, 'blocks']  # Number of L1 Blocks (time dimension)
L2Blocks = Annotated[int, 'blocks']  # Number of L2 Blocks (time dimension)
ContinuousL1Blocks = Annotated[float, 'blocks']  # (time dimension)
Seconds = Annotated[int, 's']
Probability = Annotated[float, 'probability']
Tokens = Annotated[float, 'tokens']  # Amount of slashable tokens

AgentUUID = Annotated[object, 'uuid']
TxUUID = Annotated[object, 'uuid']
ProcessUUID = Annotated[object, 'uuid']

Gas = Annotated[int, 'gas']
Gwei = Annotated[int, 'gwei']
BlobGas = Annotated[int, 'blob_gas']
Percentage = Annotated[float, "%"]



class L1TransactionType(Enum):
    BlockProposal=auto()
    CommitmentBond=auto()
    ContentReveal=auto()
    RollupProof=auto()

@dataclass
class TransactionL1():
    who: AgentUUID
    when: L1Blocks
    uuid: TxUUID
    gas: Gas
    fee: Gwei

    @property
    def gas_price(self):
        return self.fee / self.gas


# Types for representing entities

class SelectionPhase(IntEnum):  # XXX
    # Expected phases
    pending_proposals = 1
    pending_commit_bond = 2
    pending_reveal = 3
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
    current_phase_init_time: L1Blocks
    duration_in_current_phase: L1Blocks

    phase: SelectionPhase = SelectionPhase.pending_proposals


    # Relevant L1 Transactions
    tx_winning_proposal: Optional[TxUUID] = None
    tx_commitment_bond: Optional[TxUUID] = None
    tx_content_reveal: Optional[TxUUID] = None
    tx_rollup_proof: Optional[TxUUID] = None
    tx_finalization: Optional[TxUUID] = None

    # Agent-related info
    leading_sequencer: Optional[AgentUUID] = None
    uncle_sequencers: Optional[list[AgentUUID]] = None

    # Process State
    proofs_are_public: bool = False
    block_content_is_revealed: bool = False
    commit_bond_is_put_down: bool = False #Commitment bond is put down / rename from proof 
    rollup_proof_is_commited: bool = False
    finalization_tx_is_submitted: bool = False
    entered_race_mode: bool = False
    process_aborted: bool = False


    def __add__(self, other):
        """
        This is a HACK for allowing Policy Aggregation over Process.
        Specifically, the instantiated Process plus None should result in the
        instantiated Process. Else, throw an error.
        """
        if other is None:
            return self
        else:
            raise ValueError('Attempted to add Process to another non-null object')


@dataclass
class Agent(): 
    uuid: AgentUUID
    balance: Tokens
    is_sequencer: bool = False
    is_prover: bool = False
    is_relay: bool = False
    staked_amount: Tokens = 0.0

    def slots(self, tokens_per_slot: Tokens) -> Tokens:
        return floor(self.staked_amount / tokens_per_slot)
    

@dataclass
class TransactionL1Blob(TransactionL1):
    blob_gas: BlobGas
    blob_fee: Gwei

    @property
    def blob_gas_price(self):
        return self.blob_fee / self.blob_gas
@dataclass
class Proposal(TransactionL1):
    """
    NOTE: Instantiation of this class can be understood as a 
    L1T_proposer_submit_proposal event.
    """
    score: FiniteFloat
        
    #TODO: add bond_uiid: /generaluserUUID
    #TODO: before, we only needed to track proposals, as that was the only way a block came into existence. 
    #Now with race mode, it might be nice to reuse this container - a Proposal with "score: None" could be a block that was made in race mode. Otherwise, nothing really changes.   


@dataclass
class CommitmentBond(TransactionL1):
    """
    NOTE: Instantiation of this class can be understood as a 
    L1T_lead_submit_commit_bond event.
    """
    proposal_tx_uuid: TxUUID
    prover_uuid: AgentUUID
    bond_amount: float

@dataclass 
class ContentReveal(TransactionL1Blob):
    transaction_count: int
    transaction_avg_size: int
    transaction_avg_fee_per_size: Tokens

    @property
    def total_tx_fee(self) -> Tokens:
        return self.transaction_count * self.transaction_avg_size * self.transaction_avg_fee_per_size

@dataclass 
class RollupProof(TransactionL1):
    pass


AnyL1Transaction = TransactionL1 | Proposal | CommitmentBond | ContentReveal | RollupProof

SelectionResults = dict[ProcessUUID, tuple[Proposal, list[Proposal]]]

# TODO: commit_bond aka Prover Commitment Bond Object -> tracking bond UUID (might be different from sequencer UUID, bond amount). 
# Alternative is to include prover UUID and bond amount in proposal class, but to set to "None" when instantiating.  

# Definition for simulation-specific types
class AztecModelState(TypedDict):
    # Time progression
    time_l1: L1Blocks
    delta_l1_blocks: L1Blocks

    # Agents
    agents: dict[AgentUUID, Agent]

    # Process State
    current_process: Optional[Process]
    transactions: dict[TxUUID, AnyL1Transaction]

    # Environmental / Behavioral Variables
    gas_fee_l1: Gwei
    gas_fee_blob: Gwei

    # Metrics
    finalized_blocks_count: int
    disbursed_block_rewards: Tokens
    disbursed_fee_cashback: Tokens



GasEstimator = Callable[[AztecModelState], Gas]
BlobGasEstimator = Callable[[AztecModelState], BlobGas]
BaseIntEstimator = Callable[[AztecModelState], int]
BaseFloatEstimator = Callable[[AztecModelState], float]

@dataclass
class L1GasEstimators():
    proposal: GasEstimator
    commitment_bond: GasEstimator
    content_reveal: GasEstimator
    content_reveal_blob: BlobGasEstimator
    rollup_proof: GasEstimator




@dataclass
class UserTransactionEstimators():
    transaction_count: BaseIntEstimator
    transaction_average_size: BaseIntEstimator
    transaction_average_fee_per_size: BaseFloatEstimator

class AztecModelParams(TypedDict):
    # random_seed: int #Random seed for simulation model variation. 
    
    label: str  # XXX
    timestep_in_blocks: L1Blocks  # XXX

    # Economic Parameters
    uncle_count: int
    reward_per_block: Tokens
    fee_subsidy_fraction: Percentage

    # Phase Durations
    phase_duration_proposal: L1Blocks
    phase_duration_reveal: L1Blocks
    phase_duration_commit_bond: L1Blocks
    phase_duration_rollup: L1Blocks
    phase_duration_finalize: L1Blocks
    phase_duration_race: L1Blocks

    stake_activation_period: L1Blocks  # XXX
    unstake_cooldown_period: L1Blocks  # XXX

    # Behavioral Parameters

    # XXX: assume that each interacting user
    # has an fixed probability per L1 block
    # to submit an proposal
    proposal_probability_per_user_per_block: Probability

    # XXX In reveal phase, lead might not reveal content
    block_content_reveal_probability: Probability
    # XXX If lead does not reveal tx proofs, Provers can't do their work
    tx_proof_reveal_probability: Probability
    # XXX If Provers don't send back rollup proof, lead can't submit
    rollup_proof_reveal_probability: Probability
    # XXX If noone commits to put up a bond for Proving, sequencer loses their privilege and we enter race mode
    commit_bond_reveal_probability: Probability 

    proving_marketplace_usage_probability: Probability


    rewards_to_provers: Percentage
    rewards_to_relay: Percentage

    gas_estimators: L1GasEstimators
    tx_estimators: UserTransactionEstimators



class SignalTime(TypedDict, total=False):
    delta_blocks: L1Blocks

class SignalEvolveProcess(TypedDict, total=False):
    new_transactions: Sequence[AnyL1Transaction]
    update_process: Process | None

class SignalPayout(TypedDict, total=False):
    block_reward: Tokens
    fee_cashback: Tokens
    fee_from_users: Tokens