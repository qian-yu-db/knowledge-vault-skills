---
type: concept
domain: ml
confidence: solid
sources: ["raw/2026-10/kv-cache-sizing.md"]
last_verified: 2026-10-15
---
# KV Cache

The KV cache stores attention keys and values for every previous token so decoding does not recompute them.

## Sizing
Per token, the cache holds `2 × layers × kv_heads × head_dim × bytes_per_value`. For the team's 8B model
(32 layers, 8 KV heads, head dim 128, fp16) that is **128 KiB per token**, so a single 8k-token sequence
needs about **1 GiB**. With 24 GiB left after weights, that caps concurrent 8k sequences at roughly 20.

## Why it limits batch size
Batch size is bounded by free GPU memory divided by per-sequence cache size, not by compute.
[[concept-paged-attention]] reduces fragmentation so more of that memory is usable.
