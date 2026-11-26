---
type: llm
---

PASS if the response presents a triage plan for the prefix-caching clip (CREATE, MERGE, or SPLIT, naming target note files), mentions archiving the source under raw/, and asks the user to approve before writing anything.
FAIL if it reports notes as already created or merged, or does not ask for approval.
