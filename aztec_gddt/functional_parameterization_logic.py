from aztec_gddt.helper import bernoulli_trial, trial_probability


def commit_bond_reveal_behavior(state, params):
    if params["fp_commit_bond_reveal"] == "Bernoulli":
        return bernoulli_trial(
            probability=trial_probability(
                params["phase_duration_commit_bond_max_blocks"],
                params["final_probability"],
            )
        )
    else:
        assert False, "Not implemented"
