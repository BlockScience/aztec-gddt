## Summary
- Delete all but the last substep for history

## Code

<pre lang="python"><code>
def s_erase_history(
    params: AztecModelParams,
    _2,
    history,
    state: AztecModelState,
    signal: SignalEvolveProcess,
):
    """
    Logic for token supply.
    """

    for t, timestep_state in enumerate(history):
        # We may want to drop the transactions key if running on `multi_mode`
        # history[t] = [{k: v for k, v in history[t][-1].items() if k != 'transactions'}]
        # Or not, if on `single_mode`
        history[t] = [history[t][-1]]
    #     # for i, substep_state in enumerate(timestep_state):
    #     #     if i > 0:
    #     #         history[t]
    # print(f"{state['timestep']}, {len(pickle.dumps(state))}, {len(pickle.dumps(history))}")
    # dict(sorted({k: len(pickle.dumps(v)) for k, v in state.items()}.items(), key=lambda it: it[1], reverse=True))
    return ("timestep", state["timestep"])  # type: ignore
</code></pre>