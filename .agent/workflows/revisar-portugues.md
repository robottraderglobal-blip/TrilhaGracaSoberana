---
description: Ativa o Revisor de Português para devocionais publicadas
---

# Revisão de Português — Devocionais Publicadas

Workflow para revisar e corrigir erros de português, vocativos, demonstrativos e estilo nas devocionais já publicadas no Supabase.

## Pré-requisitos

- `.env` configurado com `SUPABASE_URL` e `SUPABASE_SERVICE_ROLE_KEY`
- Python 3.10+ com `supabase` instalado
- Devocionais da semana-alvo com status `aprovado` no `plano_devocional`

## Modo Automático (Script)

Para correções automáticas baseadas em regras (vocativos, demonstrativos, pontuação):

### 1. Verificar problemas (dry-run)

```powershell
python scripts/python/revisar_portugues.py --semana <N> --dry-run --verbose
```

### 2. Aplicar correções automáticas

```powershell
python scripts/python/revisar_portugues.py --semana <N> --verbose
```

### 3. Aplicar em dia específico

```powershell
python scripts/python/revisar_portugues.py --semana <N> --dia <D> --verbose
```

### 4. Gerar log de revisão

```powershell
python scripts/python/revisar_portugues.py --semana <N> --log logs/revisao_s<N>.json
```

## Modo Manual (IA Assistida)

Para revisões que exigem julgamento humano ou contextual (reformulação de frases, ajustes de coesão, padronização entre dias da semana), use o Antigravity:

### 1. Carregar a skill

Leia o arquivo `100_devocionais/SKILL_revisor_portugues.md` e siga suas instruções.

### 2. Solicitar revisão

Formato do pedido:

```
Revise a semana <N> usando a SKILL_revisor_portugues.md.
Faça a revisão completa (vocativos, demonstrativos, estilo, perguntas excessivas)
e atualize no Supabase.
```

Ou para um dia específico:

```
Revise o dia <N>/<D> usando a SKILL_revisor_portugues.md.
```

### 3. Revisão IA + Script

Para máxima qualidade, rode o script primeiro (pega os padrões óbvios) e depois peça revisão manual à IA (pega os problemas contextuais):

```powershell
# Passo 1: Automático
python scripts/python/revisar_portugues.py --semana <N> --verbose

# Passo 2: Manual (peça ao Antigravity)
# "Revise a semana <N> — o script já rodou, agora faça a revisão fina."
```

## Checklist de Revisão

O revisor verifica (por ordem de prioridade):

1. ✅ Vocativos artificiais ("Você,", "Meu amigo,", "Leitor,", "Alma,")
2. ✅ Demonstrativos incorretos (nesse/neste, nessas/nestas)
3. ✅ Pronomes possessivos sem artigo ou com maiúscula indevida
4. ✅ Perguntas retóricas excessivas (eco "Felizes... Você [verbo]?")
5. ✅ Redundâncias ("palavras acima", "Venha depressa!")
6. ✅ Pontuação (vírgulas, travessões, ponto e vírgula)
7. ✅ Concordância e regência
8. ✅ Consistência de estilo dentro da semana

## Referência

- **Skill completa**: `100_devocionais/SKILL_revisor_portugues.md`
- **Script automático**: `scripts/python/revisar_portugues.py`
- **Skill do Revisor Teológico** (complementar): `100_devocionais/SKILL_revisor_devocional.md`
