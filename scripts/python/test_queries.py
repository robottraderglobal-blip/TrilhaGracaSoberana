import sys, os
sys.path.insert(0, os.getcwd())

print("1. Importing modules...")
from ryle_pipeline.agents.pesquisador import AgentePesquisador, NOMES_AUTORES
from ryle_pipeline.models.exegese import Exegese, Doutrina
print("2. Modules imported.")

# Simular exegese simples
exegese = Exegese(
    plano_id='test-id',
    id='test-exegese-id',
    doutrinas=[
        Doutrina(nome='A Soberania de Deus na Salvação', base_textual='Efésios 2.8-9', palavras_chave=['graça', 'fé', 'dom de Deus']),
        Doutrina(nome='A Exclusão das Obras como Mérito', base_textual='Efésios 2.9', palavras_chave=['obras', 'jactância', 'mérito']),
    ]
)

pesquisador = AgentePesquisador()
queries = pesquisador._gerar_queries('sproul', 'Efésios 2.8-9', 'A Salvação pela Graça', exegese)

print("\n=== QUERIES GERADAS (v2) ===")
for i, q in enumerate(queries):
    print(f"\nQuery {i+1}:")
    print(q)

print("\n=== COMPARAÇÃO ===")
print(f"\nQuery ANTIGA (v1):")
doutrinas = ", ".join(d.nome for d in exegese.doutrinas)
query_antiga = f"Baseado puramente no material indexado deste notebook, o que você ensina ou comenta sobre as doutrinas de {doutrinas} que aparecem na passagem bíblica de Efésios 2.8-9 (A Salvação pela Graça)?"
print(query_antiga)
print(f"\nChars query antiga: {len(query_antiga)}")
print(f"Chars query v2-1:   {len(queries[0])}")
print(f"Chars query v2-2:   {len(queries[1])}")
