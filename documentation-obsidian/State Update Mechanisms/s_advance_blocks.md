## Summary

- Just log the advance_l1_blocks signal
## Code

<pre lang="python"><code>
def s_advance_blocks(_1, _2, _3, state, signal: SignalEvolveProcess):

return ("advance_l1_blocks", signal.get("advance_l1_blocks", 0))
</code></pre>