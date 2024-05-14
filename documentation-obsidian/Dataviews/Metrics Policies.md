```dataview
table file.name as Linked_File from "Policies"
WHERE contains(file.inlinks, [[Metrics PSUB]])
```
