Generate a 5-question quiz for weekly knowledge reinforcement.

## Skill Rotation Schedule
Rotate through priority skills based on week number (5-week cycle):
- Week 1, 6, 11...: **Agentic Design**
- Week 2, 7, 12...: **LLM Fine-tuning**
- Week 3, 8, 13...: **LLM/Agent Ops**
- Week 4, 9, 14...: **LLM Inference**
- Week 5, 10, 15...: **AI Productivity**

## Quiz Generation Process

1. **Determine skill** based on current week number (week % 5)
2. **Search vault** for recent notes on the topic:
   - Agentic Design: `20-notes/*agent*`, `20-notes/*agentic*`
   - LLM Fine-tuning: `20-notes/*fine-tun*`, `20-notes/*fsdp*`, `20-notes/*lora*`
   - LLM/Agent Ops: `20-notes/*mlops*`, `20-notes/*mlflow*`, `20-notes/*deploy*`
   - LLM Inference: `20-notes/*inference*`, `20-notes/*serving*`, `20-notes/*vllm*`
   - AI Productivity: `20-notes/*productivity*`, `20-notes/*claude-code*`
3. **Web search** for latest developments in the skill area
4. **Generate 5 questions** mixing:
   - 2 conceptual (definitions, comparisons)
   - 2 applied (scenarios, design decisions)
   - 1 cutting-edge (recent papers, tools, techniques)

## Question Format

```markdown
### Q[n]: [Topic Area]
**Question:** [Clear, specific question]

<details>
<summary>Show Answer</summary>

**Answer:** [Concise correct answer]

**Explanation:** [Why this matters, common misconceptions]

**Related Notes:** [[note-link-if-exists]]

</details>
```

## Output

After quiz completion:
1. Calculate score
2. Identify 1-2 gap areas
3. Recommend specific resources (vault notes or external)
4. Log results in current week's log file

## Arguments
- `$ARGUMENTS` can override skill: e.g., `/weekly-quiz agentic-design`
