```dataview
table file.lists.text AS Summary from "Policies"
WHERE contains(file.inlinks, [[Metrics PSUB]])
```