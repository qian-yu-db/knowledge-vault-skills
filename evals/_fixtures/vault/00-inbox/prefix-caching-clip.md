---
source: https://example.com/blog/prefix-caching
clipped: 2026-11-20
---
# Prefix caching in inference servers

Automatic prefix caching reuses KV cache blocks across requests that share a prompt prefix (for example, a long
system prompt). With paged attention, blocks are hashed by their token content, so a cache hit skips prefill for
those tokens. Reported speedups: time-to-first-token drops 2–5× for chat workloads with a shared 2k-token system prompt.
Trade-off: cached blocks compete with active sequences for KV memory, so eviction policy (LRU) matters.
