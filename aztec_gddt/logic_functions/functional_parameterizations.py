from typing import Tuple


def determine_profitability(phase: str, params: dict) -> Tuple[float, float, bool]:
    if params["fp_determine_profitability"] == "Always Pass":
        return determine_profitability_always_pass(phase, params)
    else:
        assert (
            False
        ), "The param of {} for fp_determine_profitability is not valid".format(
            params["fp_determine_profitability"]
        )


def determine_profitability_always_pass(
    phase: str, params: dict
) -> Tuple[float, float, bool]:
    if phase == "Reveal Content":
        # expected_rewards = params['daily_block_reward']
        # expected_rewards *= rewards_to_sequencer(params)
        # expected_rewards /= expected_l2_blocks_per_day
        expected_rewards = 1  # XXX: Temporary to ignore economic assumptions.
        assert (
            expected_rewards >= 0
        ), "REVEAL_CONTENT: Expected rewards should be positive."

        # expected_costs: float = params["op_cost_sequencer"]
        # expected_costs += fee
        # expected_costs += SAFETY_BUFFER
        # expected_costs *= params['gwei_to_tokens']
        expected_costs = 0  # XXX: Temporary to ignore economic assumptions.
        assert expected_costs == 0, "REVEAL_CONTENT: Expected costs should be zero."

        payoff_reveal = expected_rewards - expected_costs
        return expected_rewards, expected_costs, payoff_reveal
    elif phase == "Submit Proof":
        expected_rewards, expected_costs, payoff_reveal = determine_profitability(
            "Reveal Content", params
        )

        # expected_rewards = params['daily_block_reward']
        # expected_rewards *= params['rewards_to_provers']
        # expected_rewards /= expected_l2_blocks_per_day
        expected_rewards = 1
        assert (
            expected_rewards >= 0
        ), "SUBMIT PROOF: Expected rewards should be positive."

        # expected_costs: float = params["op_cost_prover"]
        # expected_costs += fee
        # expected_costs += SAFETY_BUFFER
        # expected_costs *= params['gwei_to_tokens']
        expected_costs = 0
        assert expected_costs == 0, "SUBMIT PROOF: Expected costs should be zero."

        payoff_reveal = expected_rewards - expected_costs
        return expected_rewards, expected_costs, payoff_reveal
    else:
        assert False, "Not implemented for phase {}".format(phase)
