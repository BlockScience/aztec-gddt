## Summary

- Finds whether there is censoring by either builder or validator being censored coming from the exogenous signals passed

## Code

<pre lang="python"><code>
lambda p, _1, _2, s, _5: ('is_censored', check_for_censorship(p, s))
</code></pre>