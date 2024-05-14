## Summary

- Update the process
## Code

<pre lang="python"><code>
def s_process(
    params: AztecModelParams,
    _2,
    _3,
    state: AztecModelState,
    signal: SignalEvolveProcess,
):
    """
    Logic for updating process.
    """
    updated_process = signal.get("update_process", state["current_process"])
    # Update only if there's an relevant signal.
    value = updated_process if updated_process is not None else state["current_process"]
    return ("current_process", value)
</code></pre>