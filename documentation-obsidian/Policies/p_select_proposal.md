## Summary
- "Select a sequencer from list of eligible sequencers, and determine uncle sequencers."
- Must be in pending proposals phase to run and have max_phase_duration - process.duration_in_current_phase less than 0
- Grab the proposals from the transaction and filter to be only ones that are after the process.current_phase_init_time
- If length of proposals is 0, then do skip for the block and terminate here
- Get proposals and rank by the score of the proposal
- Highest score is the proposer, the remaining up to the max uncle number are uncle blocks
- Fill in process metadata
## Code

<pre lang="python"><code>
def p_select_proposal(
    params: AztecModelParams, _2, _3, state: AztecModelState
) -> SignalEvolveProcess:
    """
    Select a sequencer from list of eligible sequencers, and
    determine uncle sequencers.

    Args:
        params (AztecModelParams): The current parameters of the model.
        state (AztecModelState): The current state of the model.

    Returns:
         Signal: The new process to be considered in the system.
    """

    #######################################
    ## Decide which processes are valid  ##
    ## 1. current phase of process must  ##
    ##    be pending proposals           ##
    ## 2. the duration is greater than   ##
    ##    proposal duration.             ##
    #######################################
    process = state["current_process"]
    updated_process: Optional[Process] = None

    max_phase_duration = params["phase_duration_proposal_max_blocks"]

    if process is None:
        pass
    else:
        if process.phase == SelectionPhase.pending_proposals:
            remaining_time = max_phase_duration - process.duration_in_current_phase
            if remaining_time < 0:
                raw_proposals: dict[TxUUID, Proposal] = proposals_from_tx(
                    state["transactions"]
                )

                proposals = {k: p for k, p in raw_proposals.items()
                             if p.when >= process.current_phase_init_time}

                if len(proposals) > 0:
                    number_uncles: int = min(
                        len(proposals) - 1, params["uncle_count"])

                    ranked_proposals: list[Proposal] = sorted(
                        proposals.values(), key=lambda p: p.score, reverse=True
                    )

                    winner_proposal: Proposal = ranked_proposals[0]
                    if len(ranked_proposals) > 1:
                        uncle_proposals: list[Proposal] = ranked_proposals[
                            1: number_uncles + 1
                        ]
                    else:
                        uncle_proposals = []

                    updated_process = copy(process)

                    # BUG: do this for all phase evolving logic.
                    # BUG: make sure that this is compatible when the time evolution is dynamical, eg, 1 ts = many blocks
                    updated_process.current_phase_init_time = state["time_l1"]

                    updated_process.phase = SelectionPhase.pending_commit_bond
                    updated_process.duration_in_current_phase = 0
                    updated_process.leading_sequencer = winner_proposal.who
                    updated_process.uncle_sequencers = [
                        p.who for p in uncle_proposals]
                    updated_process.tx_winning_proposal = winner_proposal.uuid
                else:
                    updated_process = copy(process)
                    updated_process.phase = SelectionPhase.skipped
                    updated_process.duration_in_current_phase = 0
            else:
                pass
        else:
            pass

    return {"update_process": updated_process}
</code></pre>