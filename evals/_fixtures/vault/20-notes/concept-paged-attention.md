---
type: concept
domain: ml
confidence: learning
sources: ["https://arxiv.org/abs/2309.06180"]
last_verified: 2026-10-15
---
# Paged Attention

Stores the [[concept-kv-cache]] in fixed-size blocks, like virtual-memory pages, so memory is not reserved
for the maximum sequence length up front. Waste drops from 60–80% to under 4% in the vLLM paper.
