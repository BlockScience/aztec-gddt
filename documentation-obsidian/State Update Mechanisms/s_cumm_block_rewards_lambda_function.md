## Summary

- Add current block reward to the cumulative

## Code

<pre lang="python"><code>
lambda _1,_2,_3,s1,s2: ('cumm_block_rewards', s2['block_reward'] + s1['cumm_block_rewards'])
</code></pre>