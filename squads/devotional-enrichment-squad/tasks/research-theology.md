---
task: "Research Theology"
responsavel: "@exegete-researcher"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - passage_reference
  - context_text
Saida: |
  - exegesis_notes
  - hebrew_greek_roots
Checklist:
  - "[ ] Validate input parameters"
  - "[ ] Execute main logic"
  - "[ ] Format output"
  - "[ ] Return result"
---

# *research-theology

Task generated from squad design blueprint for devotional-enrichment-squad.

## Usage

```
@exegete-researcher
*research-theology
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `passage_reference` | string | Yes | passage reference |
| `context_text` | string | Yes | context text |

## Output

- **exegesis_notes**: exegesis notes
- **hebrew_greek_roots**: hebrew greek roots

## Origin

Confidence: 95%
