"""
Migração: Atualiza e limpa os cabeçalhos das devocionais das Semanas 1 a 5 (dias 1-35) no banco
e injeta as letras oficiais dos Hinos do Novo Cântico.
"""
import sys
import io
import re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from nicodemos_pipeline_100.db.client import get_client
from nicodemos_pipeline_100.utils import get_hymn_formatted_for_day
from nicodemos_pipeline_100.pipeline import _limpar_cabecalhos

def main():
    sb = get_client()
    
    # Buscar dias 1 a 35
    r = sb.table('nico_devocionais_final').select('id, dia, conteudo_md').gte('dia', 1).lte('dia', 35).order('dia').execute()
    
    if not r.data:
        print("Nenhuma devocional encontrada para os dias 1-35.")
        return
    
    print(f"Iniciando a migração e limpeza das devocionais dos Dias 1 a 35...")
    
    updated = 0
    for row in r.data:
        dia = row['dia']
        md = row['conteudo_md']
        if not md:
            continue
        
        # 1. Limpar cabeçalhos (remover emojis e parênteses)
        cleaned_md = _limpar_cabecalhos(md)
        
        # 2. Injetar hino oficial
        hymn_title, hymn_formatted = get_hymn_formatted_for_day(dia)
        
        header_match = re.search(r'###\s*7\..*?Melodia no Lar[^\n]*\n', cleaned_md, re.IGNORECASE)
        if header_match:
            index = header_match.start()
            conteudo_antes = cleaned_md[:index]
            new_section_7 = f"### 7. Melodia no Lar\n\n[{hymn_title}]\n\n{hymn_formatted}\n"
            new_md = conteudo_antes.strip() + "\n\n" + new_section_7
        else:
            new_section_7 = f"\n\n### 7. Melodia no Lar\n\n[{hymn_title}]\n\n{hymn_formatted}\n"
            new_md = cleaned_md.strip() + new_section_7
            
        # 3. Salvar se houver modificações
        if new_md != md:
            sb.table('nico_devocionais_final').update({
                'conteudo_md': new_md
            }).eq('id', row['id']).execute()
            updated += 1
            print(f"  Dia {dia:03d}: ATUALIZADO com cabeçalhos limpos e hino [{hymn_title}]")
        else:
            print(f"  Dia {dia:03d}: sem alterações necessárias")
            
    print(f"\n✅ Concluído! Total de devocionais migradas: {updated}")

if __name__ == '__main__':
    main()
