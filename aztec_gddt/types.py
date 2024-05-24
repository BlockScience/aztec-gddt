from typing import Annotated, Dict, TypedDict, NamedTuple, Optional
from typing import Any, Callable, Concatenate, ParamSpec, Sequence
from enum import IntEnum, Enum, auto
from math import floor
import numpy as np
from pydantic import FiniteFloat
from pydantic.dataclasses import dataclass

# Units


ETH = float
L1Blocks = Annotated[int, "blocks"]  # Number of L1 Blocks (time dimension)
L2Blocks = Annotated[int, "blocks"]  # Number of L2 Blocks (time dimension)
ContinuousL1Blocks = Annotated[float, "blocks"]  # (time dimension)
Seconds = Annotated[int, "s"]
Probability = Annotated[float, "probability"]
Tokens = Annotated[
    float, "tokens"
]  # Tokens are currently set to ETH via gwei_to_tokens conversion

AgentUUID = Annotated[object, "uuid"]
TxUUID = Annotated[object, "uuid"]
ProcessUUID = Annotated[object, "uuid"]

Bytes = Annotated[int, "bytes"]
Gas = Annotated[int, "gas"]
Gwei = Annotated[int, "gwei"]
BlobGas = Annotated[int, "blob_gas"]
Percentage = Annotated[float, "%"]
FunctionalParameterizationString = str  # A string representing the functional paramterization option to use, i.e. "Basic Function"


class L1TransactionType(Enum):
    BlockProposal = auto()
    CommitmentBond = auto()
    ContentReveal = auto()
    RollupProof = auto()


@dataclass
class TransactionL1:
    who: AgentUUID
    when: L1Blocks
    uuid: TxUUID
    gas: Gas
    fee: Gwei

    @property
    def gas_price(self):
        return self.fee / self.gas


# Types for representing entities


class SelectionPhase(IntEnum):
    pending_proposals = 1
    pending_commit_bond = 2
    pending_reveal = 3
    pending_rollup_proof = 4
    finalized = 5
    skipped = -1
    proof_race = -2


@dataclass
class TokenSupply:
    circulating: Tokens
    staked: Tokens
    burnt: Tokens
    issued: Tokens

    @property
    def user(self) -> FiniteFloat:
        return self.circulating + self.staked

    @property
    def invariant(self) -> FiniteFloat:
        return (self.staked + self.burnt) + (self.circulating - self.issued)

    @staticmethod
    def from_state(state: "AztecModelState") -> "TokenSupply":
        obj = TokenSupply(
            circulating=sum(
                a.balance for a in state["agents"].values() if a.uuid != "burnt"
            ),
            staked=sum(
                a.staked_amount for a in state["agents"].values() if a.uuid != "burnt"
            ),
            burnt=sum(a.balance for a in state["agents"].values() if a.uuid == "burnt"),
            issued=state["cumm_block_rewards"] + state["cumm_fee_cashback"],
        )
        return obj


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

    # Agent-related info
    leading_sequencer: Optional[AgentUUID] = None
    uncle_sequencers: Optional[list[AgentUUID]] = None

    # Process State
    proofs_are_public: bool = False
    block_content_is_revealed: bool = False
    commit_bond_is_put_down: bool = False
    rollup_proof_is_commited: bool = False
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
            raise ValueError("Attempted to add Process to another non-null object")


@dataclass
class Agent:
    uuid: AgentUUID
    balance: ETH
    is_sequencer: bool = False
    is_prover: bool = False
    is_relay: bool = False
    staked_amount: ETH = 0.0

    logic: Optional[Dict[str, Callable[[Dict], Any]]] = (
        None  # placeholder for general agent logic
    )

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
    size: Bytes
    public_composition: Percentage


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
    transaction_avg_size: float
    transaction_avg_fee_per_size: Tokens

    @property
    def total_tx_fee(self) -> Tokens:
        return (
            self.transaction_count
            * self.transaction_avg_size
            * self.transaction_avg_fee_per_size
        )


@dataclass
class RollupProof(TransactionL1):
    pass


AnyL1Transaction = (
    TransactionL1 | Proposal | CommitmentBond | ContentReveal | RollupProof
)

SelectionResults = dict[ProcessUUID, tuple[Proposal, list[Proposal]]]

# Definition for simulation-specific types


class AztecModelState(TypedDict):
    # Time progression
    timestep: int
    substep: int
    time_l1: L1Blocks
    delta_l1_blocks: L1Blocks
    advance_l1_blocks: L1Blocks

    # Rewards and Punishments
    total_rewards_provers: Tokens
    total_rewards_sequencers: Tokens
    total_rewards_relays: Tokens

    slashes_to_provers: Tokens
    slashes_to_sequencers: Tokens

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
    cumm_block_rewards: Tokens
    cumm_fee_cashback: Tokens
    cumm_burn: Tokens
    is_censored: bool

    token_supply: TokenSupply


P = ParamSpec("P")
GasEstimator = Callable[Concatenate[AztecModelState, P], Gas]
BlobGasEstimator = Callable[Concatenate[AztecModelState, P], BlobGas]
BaseIntEstimator = Callable[Concatenate[AztecModelState, P], int]
BaseFloatEstimator = Callable[Concatenate[AztecModelState, P], float]


@dataclass
class L1GasEstimators:
    proposal: GasEstimator
    commitment_bond: GasEstimator
    content_reveal: GasEstimator
    content_reveal_blob: BlobGasEstimator
    rollup_proof: GasEstimator


@dataclass
class UserTransactionEstimators:
    transaction_count: BaseIntEstimator
    proposal_average_size: BaseIntEstimator
    transaction_average_fee_per_size: BaseFloatEstimator


@dataclass
class SlashParameters:
    failure_to_commit_bond: ETH
    failure_to_reveal_block: ETH


class AztecModelParams(TypedDict):
    # random_seed: int #Random seed for simulation model variation.

    label: str  # Defines Labels as strings
    timestep_in_blocks: L1Blocks  # Defines timesteps in L1Blocks

    # Economic Parameters
    uncle_count: int
    daily_block_reward: ETH
    l1_blocks_per_day: int
    fee_subsidy_fraction: Percentage
    minimum_stake: ETH

    # Phase Durations
    # These have both minimum and maximum numbers of blocks
    phase_duration_proposal_min_blocks: L1Blocks
    phase_duration_proposal_max_blocks: L1Blocks
    phase_duration_reveal_min_blocks: L1Blocks
    phase_duration_reveal_max_blocks: L1Blocks
    phase_duration_commit_bond_min_blocks: L1Blocks
    phase_duration_commit_bond_max_blocks: L1Blocks
    phase_duration_rollup_min_blocks: L1Blocks
    phase_duration_rollup_max_blocks: L1Blocks
    phase_duration_race_min_blocks: L1Blocks
    phase_duration_race_max_blocks: L1Blocks

    stake_activation_period: L1Blocks  # Defines stake_activation in L1 blocks
    unstake_cooldown_period: L1Blocks  # Defines stake_deactivation in L1 blocks

    # Behavioral Parameters
    logic: Dict[str, Callable[[Dict], Any]]  # placeholder for general system logic
    gas_threshold_for_tx: Gwei
    blob_gas_threshold_for_tx: Gwei
    proving_marketplace_usage_probability: Probability
    final_probability: Probability

    gwei_to_tokens: Tokens

    rewards_to_provers: Percentage
    rewards_to_relay: Percentage

    censorship_series_builder: dict[L1Blocks, bool]
    censorship_series_validator: dict[L1Blocks, bool]

    gas_estimators: L1GasEstimators
    tx_estimators: UserTransactionEstimators
    slash_params: SlashParameters
    gas_fee_l1_time_series: np.ndarray
    gas_fee_blob_time_series: np.ndarray

    commit_bond_amount: float
    op_cost_sequencer: Gwei
    op_cost_prover: Gwei

    safety_factor_commit_bond: float
    safety_factor_reveal_content: float
    safety_factor_rollup_proof: float

    past_gas_weight_fraction: Percentage
    fp_determine_profitability: FunctionalParameterizationString
    top_up_amount: ETH


class SignalTime(TypedDict, total=False):
    delta_blocks: L1Blocks


class TransferKind(Enum):
    conventional = auto()
    slash_sequencer = auto()
    slash_prover = auto()


class Transfer(NamedTuple):
    source: AgentUUID
    destination: AgentUUID
    amount: Tokens
    kind: TransferKind
    to_prover: bool = False
    to_sequencer: bool = False


class SignalEvolveProcess(TypedDict, total=False):
    new_transactions: Sequence[AnyL1Transaction]
    update_process: Optional[Process]
    advance_l1_blocks: Optional[int]
    transfers: Optional[Sequence[Transfer]]


class SignalPayout(TypedDict, total=False):
    block_reward: Tokens
    fee_cashback: Tokens
    fee_from_users: Tokens
