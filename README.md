# Trilha Graça Soberana

Este repositório abriga todo o projeto da Trilha Graça Soberana: a automação de IA geradora de estudos e material teológico e também seu Frontend em React de consumo/portal dos estudos diários.

## Arquitetura e Visão Global
O sistema é constituído principalmente por pipelines autônomas e interativas codificadas em Python que buscam estruturá-los diariamente salvando os estados de Devocionais no Supabase e uma via React/Next para entregar o material com design rico.

Para o entendimento rápido dos fundamentos, leia o guia de [Arquitetura em `/docs/architecture.md`](docs/architecture.md).

## Documentações do Projeto
Visite a pasta `/docs` para entender minuciosamente como operar o sistema caso esteja entrando ou precisando recriar e manter o projeto:

- [Visão Geral de Arquitetura (`/docs/architecture.md`)](docs/architecture.md)
- [Guia da Pipeline de Automação Backend (`/docs/pipelines-guide.md`)](docs/pipelines-guide.md)
- [Guia do Frontend (`/docs/frontend-guide.md`)](docs/frontend-guide.md)

## Destaques de Navegação
O repositório foi limpo para facilitar e focar em diretórios chave:
*   `ryle_pipeline/` e `nicodemos_pipeline_100/`: Corações de Processamento AI em Python. Cada um com seus agentes e prompt-chains.
*   `web/`: Interface Frontend.
*   `scripts/`: Todos os utilitários criados e usados pelo mantenedor para testar lógicas ad-hoc, rodar batches isolados, analisar JSON ou revisar notas dos devocionais.
*   `logs/`: Despejo consolidado das rodadas autônomas.

Para operar, referencie o manual que guie devidamente a stack. Os Scripts agora vivem numa pasta designada garantindo isolamento da base principal.

> "Soli Deo Gloria"
