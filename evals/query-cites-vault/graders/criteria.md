---
type: llm
---

PASS if the answer states about 1 GiB per 8k-token sequence (128 KiB per token), explains that batch size is bounded by free GPU memory divided by per-sequence cache size, and cites the vault note as [[concept-kv-cache]].
FAIL if the numbers are missing or different, or if no vault note is cited.
