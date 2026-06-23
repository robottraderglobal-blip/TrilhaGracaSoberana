---
task: "Write Devotional"
responsavel: "@ryle-writer"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - raw_devotional_text
  - exegesis_notes
  - hebrew_greek_roots
Saida: |
  - enriched_devotional_text
Checklist:
  - "[ ] Validate input parameters"
  - "[ ] Execute main logic"
  - "[ ] Format output"
  - "[ ] Return result"
---

# *write-devotional

Task generated from squad design blueprint for devotional-enrichment-squad.

## Usage

```
@ryle-writer
*write-devotional
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `raw_devotional_text` | string | Yes | raw devotional text |
| `exegesis_notes` | string | Yes | exegesis notes |
| `hebrew_greek_roots` | string | Yes | hebrew greek roots |

## Output

- **enriched_devotional_text**: enriched devotional text

## Origin

Confidence: 92%
