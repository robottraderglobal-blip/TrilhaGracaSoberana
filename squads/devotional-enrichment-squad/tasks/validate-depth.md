---
task: "Validate Depth"
responsavel: "@theological-qa"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - enriched_devotional_text
Saida: |
  - evaluation_score
  - feedback_notes
  - passed
Checklist:
  - "[ ] Validate input parameters"
  - "[ ] Execute main logic"
  - "[ ] Format output"
  - "[ ] Return result"
---

# *validate-depth

Task generated from squad design blueprint for devotional-enrichment-squad.

## Usage

```
@theological-qa
*validate-depth
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `enriched_devotional_text` | string | Yes | enriched devotional text |

## Output

- **evaluation_score**: evaluation score
- **feedback_notes**: feedback notes
- **passed**: passed

## Origin

Confidence: 90%
