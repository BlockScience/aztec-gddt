## Summary

- Simple transfer functionality between source and destination
## Code

<pre lang="python"><code>
def s_agent_transfer(
    params: AztecModelParams,
    _2,
    _3,
    state: AztecModelState,
    signal: SignalEvolveProcess,
):
    """
    Logic for transferring tokens between agents and burn sink.
    """
    updated_agents = state["agents"].copy()
    transfers: Sequence[Transfer] = signal.get("transfers", [])  # type: ignore

    for transfer in transfers:
        if transfer.kind == TransferKind.conventional:
            updated_agents[transfer.source].balance -= transfer.amount
            updated_agents[transfer.destination].balance += transfer.amount
        elif transfer.kind == TransferKind.slash_sequencer:
            updated_agents[transfer.source].staked_amount -= transfer.amount
            updated_agents[transfer.destination].balance += transfer.amount
        elif transfer.kind == TransferKind.slash_prover:
            updated_agents[transfer.source].balance -= transfer.amount
            updated_agents[transfer.destination].balance += transfer.amount
        else:
            raise Exception(f'Transfer logic is undefined for {transfer.kind}')

    return ("agents", updated_agents)
</code></pre>