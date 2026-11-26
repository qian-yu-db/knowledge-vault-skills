---
type: guide
domain: ml
sources: ["https://docs.vllm.ai"]
last_verified: 2026-10-20
---
# Serving with vLLM

Set `--gpu-memory-utilization` so the [[concept-kv-cache]] gets the memory left after weights.
vLLM relies on [[concept-paged-attention]]. For lower latency, consider [[concept-speculative-decoding]].
