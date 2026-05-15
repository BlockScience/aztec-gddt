## Summary

- Get the value from the time series for gas_fee_blob
- New value is weighted average of this and the last value, making an exponentially weighted formula

## Code

<pre lang="python"><code>
def s_gas_fee_blob(p: AztecModelParams, _2, _3, s, _5): 
    key = "gas_fee_blob"
    random_value =  value_from_param_timeseries_suf(p, s, "gas_fee_blob_time_series", key)
    past_value = s[key]
    value = round(p['past_gas_weight_fraction'] * past_value + (1 - p['past_gas_weight_fraction']) * random_value)
    return (key, value)
</code></pre>