## Summary
- "Initializes a specific process."
-  "Logical check to determine if a new process will be  initiated. Checks to see if current phase of last process is one of pending_rollup_proof, skipped, or reorg."
- No current process means do do_init_process = True as well as a finalized current process or a skipped current process.
## Code

<pre lang="python"><code>
def p_init_process(
    params: AztecModelParams, _2, _3, state: AztecModelState
) -> SignalEvolveProcess:
    """
    Initializes a specific process.

    Args:
         params (AztecModelParams): The current parameters of the model.
         state (AztecModelState): The current state of the model.

    Returns:
         Signal: The new process to be considered in the system.

    """

    #######################################
    ## Logical check to determine if     ##
    ## a new process will be  initiated. ##
    ## Checks to see if current phase    ##
    ## of last process is one of         ##
    ## pending_rollup_proof, skipped,    ##
    ## or reorg.                         ##
    #######################################

    if state["current_process"] is None:
        # Assumption: Lack of active process implies a new one being initiated
        do_init_process = True
    else:
        # Else, check if the current one is finalized
        do_init_process = state["current_process"].phase == SelectionPhase.finalized
        do_init_process |= state["current_process"].phase == SelectionPhase.skipped

    #######################################
    ## Logic to create new process       ##
    #######################################

    if do_init_process:
        new_process = Process(
            uuid=uuid4(),
            phase=SelectionPhase.pending_proposals,
            leading_sequencer=None,
            uncle_sequencers=None,
            current_phase_init_time=state["time_l1"],
            duration_in_current_phase=0,
            proofs_are_public=False,
            block_content_is_revealed=False,
            commit_bond_is_put_down=False,
            rollup_proof_is_commited=False,
            process_aborted=False,
        )
    else:
        new_process = None

    return {"update_process": new_process}
</code></pre>