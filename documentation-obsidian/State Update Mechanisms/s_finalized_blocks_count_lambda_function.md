## Summary
- Increment finalized_block_count by 1 if the phase is finalized
## Code

<pre lang="python"><code>
lambda _1, _2, _3, s, _5:  ('finalized_blocks_count', s['finalized_blocks_count'] + 1 if s['current_process'].phase == SelectionPhase.finalized else s['finalized_blocks_count'])
</code></pre>