# Guia de Execução das Pipelines de Automação

As pipelines do projeto representam a automação central em Python (`ryle_pipeline/` e `nicodemos_pipeline_100/`). Elas cuidam de todo o processo orquestrado de conversação com o modelo de Linguagem, interações com NotebookLM/OpenRouter, montagem das estruturas teológicas e posterior salvação no banco de dados.

## Fluxo da Pipeline

Cada pipeline tem um script integrador (geralmente `run_pipeline_bg.py` ou `<autor>_pipeline.py`). O workflow segue o fluxo:
1.  **Montagem do Plano:** O banco busca quais semanas e dias devem ser gerados/processados.
2.  **Pesquisa / Elicitação Base:** Extrai trechos bíblicos e fontes através de prompts baseados no material (PDFs/Apostilas pré-carregadas); 
3.  **Processo do Agente Exegeta / Pesquisador:** Envia essas partes via API (`openrouter/gemini` ou NotebookLM MCP) e molda notas e rascunhos.
4.  **Revisão (QA / Revisor):** Aprovação do material. Se as pontuações e conformidades caírem abaixo do mínimo aceitável (ex. falha na pontuação $< 90$ de consistência teológica), o devocional cai em *refazer*.
5.  **Merge & Distribuição:** Persiste as tabelas de estado (Devocional concluída) no `Supabase`.

## Executando as Pipelines

### 1. Preparação de Ambiente
Instale os requisitos rodando no Python (se certifique de ter um Virtualenv ativado, ou os pacotes instalados globalmente caso estritamente necessário no servidor):

```bash
pip install -r requirements.txt # (Ou instale os pacotes principais das chamadas: supabase, httpx, asyncio etc.)
```

Certifique-se que o seu arquivo `.env` na raiz está formatado corretamente conforme o `.env.example`, incluindo as varíaveis do Supabase e as API Keys (`OPENROUTER_API_KEY` ou `GEMINI_API_KEY`).

### 2. Rodando a Pipeline Base (Nicodemos ou Ryle)
Para invocar o ciclo (loop continuo), você pode usar os scripts principais de integração que já estão desenhados no projeto. Por exemplo:
```powershell
python run_pipeline_bg.py
# ou
python nicodemos_pipeline_100\pipeline.py
```

Isto vai instanciar a automação. 

### 3. Usando Utilitários (Tools/Scripts)
Com o debug, separamos diversos scripts em `/scripts/python/` e `/scripts/js/`. Se a pipeline travar, falhar conexão ou gerar material inadequado, use:
-   `python scripts/python/refazer_abaixo90.py`: Retoma Devocionais que o `QA` pontuou baixo mas não foram refeitos.
-   `node scripts/js/limpar_abaixo90.js`: Exemplo de script limpador utilitário.
-   `python scripts/python/limpar_travamentos.py`: Limpa pendencias do Queue na base para reativar geração limpa.

### Tratamentos e Debug
-   Sempre observe em `/logs/` os arquivos como `ryle_pipeline.log` para inferências paralisadas com erro `Timeout` ou `Quota`.
-   Verifique o `Cache`. A estrutura do NotebookLM cria um DB cache no supabase (Tabela `nlm_cache`). O erro de "Cache Miss" apenas gasta chamadas, não impacta dados.
