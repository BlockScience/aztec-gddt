from aztec_gddt.logic import *
from aztec_gddt.types import *
from aztec_gddt.helper import check_for_censorship
from copy import deepcopy

AZTEC_MODEL_BLOCKS: list[dict] = [
    {
        "label": "Time Tracking",
        "ignore": False,
        "desc": "Updates the time in the system",
        "policies": {"evolve_time": p_evolve_time},
        "variables": {
            "time_l1": s_block_time,
            "delta_blocks": s_delta_blocks,
            "current_process": s_current_process_time,
        },
    },
    {
        "label": "Exogenous Processes",
        "ignore": False,
        "policies": {},
        "variables": {"gas_fee_l1": s_gas_fee_l1, "gas_fee_blob": s_gas_fee_blob},
    },
    {
        "label": "Agent Actions",
        "ignore": False,
        "policies": {},
        "variables": {
            "transactions": s_transactions_new_proposals,
            "agents": s_agent_restake,
        },
    },
    {
        "label": "Evolve Block Process",
        "ignore": False,
        "policies": {
            "init_process": p_init_process,
            "select_sequencer": p_select_proposal,
            "submit_commit_bond": p_commit_bond,
            "reveal_block_content": p_reveal_content,
            "submit_block_proof": p_submit_proof,
            "submit_block_proof_content_race": p_race_mode,
        },
        "variables": {
            "current_process": s_process,
            "transactions": s_transactions,
            "advance_l1_blocks": s_advance_blocks,
            "slashes_to_sequencers": s_slashes_to_sequencer,
            "slashes_to_provers": s_slashes_to_prover,
            "agents": s_agent_transfer,
            "is_censored": s_is_censored,
        },
    },
    {
        "label": "Payouts",
        "ignore": False,
        "policies": {
            "block_reward": p_block_reward,
            #            'fee_cashback': p_fee_cashback,
            "fee_from_users": p_fee_from_users,
        },
        "variables": {
            "total_rewards_provers": s_total_rewards_provers,
            "total_rewards_sequencers": s_total_rewards_sequencers,
            "total_rewards_relays": s_total_rewards_relays,
            "agents": s_agents_rewards,
            "cumm_block_rewards": s_cumm_block_rewards,
            #            'cumm_fee_cashback': lambda _1,_2,_3,s1,s2: ('cumm_fee_cashback', s2['fee_cashback'] + s1['cumm_fee_cashback'])
        },
    },
    {
        "label": "Dynamically Evolve Time",
        "ignore": False,
        "policies": {"conditionally_evolve_time": p_evolve_time_dynamical},
        "variables": {
            "time_l1": s_block_time,
            "delta_blocks": s_delta_blocks,
            "current_process": s_current_process_time_dynamical,
            "advance_l1_blocks": s_reset_advance,
        },
    },
    {
        "label": "Metrics",
        "ignore": False,
        "policies": {},
        "variables": {
            "token_supply": s_token_supply,
            "finalized_blocks_count": s_finalized_blocks_count_lambda_function,
        },
    },
    {
        "label": "Meta Stuff",
        "ignore": False,
        "policies": {},
        "variables": {"timestep": s_erase_history},
    },
]


blocks: list[dict] = []
for block in [b for b in AZTEC_MODEL_BLOCKS if b.get("ignore", False) != True]:
    _block = deepcopy(block)
    for variable, suf in block.get("variables", {}).items():
        if suf == add_suf:
            _block["variables"][variable] = add_suf(variable)
        elif suf == replace_suf:
            _block["variables"][variable] = replace_suf(variable)

    blocks.append(_block)

AZTEC_MODEL_BLOCKS = [
    block for block in AZTEC_MODEL_BLOCKS if block.get("ignore", False) is False
]
