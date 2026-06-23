"""
Seed: Cadastra os novos dias 151 a 196 (Semanas 22 a 28) na tabela nico_plano
com seus respectivos versículos teológicos clássicos e status 'pending'.
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from nicodemos_pipeline_100.db.client import get_client

# Novas 46 devocionais (Dias 151 a 196) com versículos clássicos
novas_entradas = [
    {"dia": 151, "ref": "Tiago 1.12", "t": "Bem-aventurado o homem que suporta, com perseverança, a provação; porque, depois de ter sido aprovado, receberá a coroa da vida, a qual o Senhor prometeu aos que o amam."},
    {"dia": 152, "ref": "Hebreus 11.1", "t": "Ora, a fé é a certeza de coisas que se esperam, a convicção de fatos que se não vêem."},
    {"dia": 153, "ref": "1 João 4.19", "t": "Nós amamos porque ele nos amou primeiro."},
    {"dia": 154, "ref": "Romanos 8.28", "t": "Sabemos que todas as coisas cooperam para o bem daqueles que amam a Deus, daqueles que são chamados segundo o seu propósito."},
    {"dia": 155, "ref": "Mateus 6.33", "t": "Buscai, pois, em primeiro lugar, o seu reino e a sua justiça, e todas estas coisas vos serão acrescentadas."},
    {"dia": 156, "ref": "Filipenses 4.13", "t": "Tudo posso naquele que me fortalece."},
    {"dia": 157, "ref": "João 3.16", "t": "Porque Deus amou ao mundo de tal maneira que deu o seu Filho unigênito, para que todo o que nele crê não pereça, mas tenha a vida eterna."},
    {"dia": 158, "ref": "Salmos 23.1", "t": "O Senhor é o meu pastor; nada me faltará."},
    {"dia": 159, "ref": "Salmos 46.10", "t": "Aquietai-vos e sabei que eu sou Deus; sou exaltado entre as nações, sou exaltado na terra."},
    {"dia": 160, "ref": "Salmos 121.1-2", "t": "Elevo os olhos para os montes: de onde me virá o socorro? O meu socorro vem do Senhor, que fez o céu e a terra."},
    {"dia": 161, "ref": "Isaías 40.31", "t": "Mas os que esperam no Senhor renovam as suas forças, sobem com asas como águias, correm e não se cansam, caminham e não se fatigam."},
    {"dia": 162, "ref": "Efésios 2.8-9", "t": "Porque pela graça sois salvos, mediante a fé; e isto não vem de vós; é dom de Deus; não de obras, para que ninguém se glorie."},
    {"dia": 163, "ref": "Gálatas 2.20", "t": "Estou crucificado com Cristo; logo, já não sou eu quem vive, mas Cristo vive em mim; e esse viver que, agora, tenho na carne, vivo-o na fé do Filho de Deus, que me amou e a si mesmo se entregou por mim."},
    {"dia": 164, "ref": "Colossenses 3.23", "t": "Tudo quanto fizerdes, fazei-o de todo o coração, como para o Senhor e não para homens,"},
    {"dia": 165, "ref": "2 Timóteo 1.7", "t": "Porque Deus não nos deu espírito de covardia, mas de poder, de amor e de moderação."},
    {"dia": 166, "ref": "1 Pedro 5.7", "t": "lançando sobre ele toda a vossa ansiedade, porque ele tem cuidado de vós."},
    {"dia": 167, "ref": "Apocalipse 21.4", "t": "E lhes enxugará dos olhos toda lágrima, e a morte já não existirá, já não haverá luto, nem pranto, nem dor, porque as primeiras coisas passaram."},
    {"dia": 168, "ref": "Josué 24.15", "t": "Porém, se vos parece mal servir ao Senhor, escolhei hoje a quem sirvais; (...) Eu e a minha casa serviremos ao Senhor."},
    {"dia": 169, "ref": "Salmos 119.9", "t": "De que maneira poderá o jovem guardar puro o seu caminho? Observando-o segundo a tua palavra."},
    {"dia": 170, "ref": "Mateus 11.28", "t": "Vinde a mim, todos os que estais cansados e sobrecarregados, e eu vos aliviarei."},
    {"dia": 171, "ref": "Hebreus 4.16", "t": "Acheguemo-nos, portanto, confiadamente, junto ao trono da graça, a fim de recebermos misericórdia e acharmos graça no momento oportuno."},
    {"dia": 172, "ref": "Lamentações 3.25", "t": "Bom é o Senhor para os que esperam por ele, para a alma que o busca."},
    {"dia": 173, "ref": "Salmos 37.5", "t": "Entrega o teu caminho ao Senhor, confia nele, e o mais ele fará."},
    {"dia": 174, "ref": "Romanos 12.1", "t": "Rogo-vos, pois, irmãos, pelas misericórdias de Deus, que apresenteis o vosso corpo por sacrifício vivo, santo e agradável a Deus, que é o vosso culto racional."},
    {"dia": 175, "ref": "Tiago 4.7", "t": "Sujeitai-vos, portanto, a Deus; mas resisti ao diabo, e ele fugirá de vós."},
    {"dia": 176, "ref": "João 14.6", "t": "Respondeu-lhe Jesus: Eu sou o caminho, e a verdade, e a vida; ninguém vem ao Pai senão por mim."},
    {"dia": 177, "ref": "Romanos 5.1", "t": "Justificados, pois, mediante a fé, temos paz com Deus por meio de nosso Senhor Jesus Cristo;"},
    {"dia": 178, "ref": "Romanos 8.1", "t": "Agora, pois, nenhuma condenação há para os que estão em Cristo Jesus."},
    {"dia": 179, "ref": "Colossenses 3.16", "t": "Habite ricamente em vós a palavra de Cristo; instruí-vos e aconselhai-vos mutuamente em toda a sabedoria, louvando a Deus, com salmos, e hinos, e cânticos espirituais, com gratidão em vosso coração."},
    {"dia": 180, "ref": "1 Tessalonicenses 5.17", "t": "Orai sem cessar."},
    {"dia": 181, "ref": "Hebreus 13.8", "t": "Jesus Cristo é o mesmo ontem, e hoje, e o será para sempre."},
    {"dia": 182, "ref": "Salmos 1.1-2", "t": "Bem-aventurado o homem que não anda no conselho dos ímpios, não se detém no caminho dos pecadores, nem se assenta na roda dos escarnecedores. Antes, o seu prazer está na lei do Senhor, e na sua lei medita de dia e de noite."},
    {"dia": 183, "ref": "Salmos 19.7", "t": "A lei do Senhor é perfeita e restaura a alma; o testemunho do Senhor é fiel e dá sabedoria aos símplices."},
    {"dia": 184, "ref": "1 João 1.7", "t": "Se, porém, andarmos na luz, como ele na luz está, mantemos comunhão uns com os outros, e o sangue de Jesus, seu Filho, nos purifica de todo pecado."},
    {"dia": 185, "ref": "Romanos 12.2", "t": "E não vos conformeis com este século, mas transformai-vos pela renovação da vossa mente, para que experimenteis qual seja a boa, agradável e perfeita vontade de Deus."},
    {"dia": 186, "ref": "Filipenses 4.6", "t": "Não andeis ansiosos de coisa alguma; em tudo, porém, sejam conhecidas diante de Deus as vossas petições, pela oração e pela súplica, com ações de graças."},
    {"dia": 187, "ref": "Hebreus 10.25", "t": "Não deixemos de congregar-nos, como é costume de alguns; antes, façamos admoestações e tanto mais quanto vedes que o Dia se aproxima."},
    {"dia": 188, "ref": "1 Pedro 2.9", "t": "Vós, porém, sois raça eleita, sacerdócio real, nação santa, povo de propriedade exclusiva de Deus, a fim de proclamardes as virtudes daquele que vos chamou das trevas para a sua maravilhosa luz;"},
    {"dia": 189, "ref": "Efésios 6.11", "t": "Revesti-vos de toda a armadura de Deus, para poderdes ficar firmes contra as ciladas do diabo;"},
    {"dia": 190, "ref": "Salmos 119.11", "t": "Guardo a tua palavra no meu coração, para não pecar contra ti."},
    {"dia": 191, "ref": "João 15.5", "t": "Eu sou a videira, vós, os ramos. Quem permanece em mim, e eu, nele, esse dá muito fruto; porque sem mim nada podeis fazer."},
    {"dia": 192, "ref": "2 Coríntios 12.9", "t": "Então, ele me disse: A minha graça te basta, porque o poder se aperfeiçoa na fraqueza. De boa vontade, pois, mais me gloriarei nas fraquezas, para que sobre mim repouse o poder de Cristo."},
    {"dia": 193, "ref": "1 Timóteo 2.5", "t": "Porquanto há um só Deus e um só Mediador entre Deus e os homens, Cristo Jesus, homem,"},
    {"dia": 194, "ref": "1 João 5.4", "t": "porque todo o que é nascido de Deus vence o mundo; e esta é a vitória que vence o mundo: a nossa fé."},
    {"dia": 195, "ref": "Salmos 127.1", "t": "Se o Senhor não edificar a casa, em vão trabalham os que a edificam; se o Senhor não guardar a cidade, em vão vigia a sentinela."},
    {"dia": 196, "ref": "Mateus 28.20", "t": "ensinando-os a guardar todas as coisas que vos tenho ordenado. E eis que estou convosco todos os dias até à consumação do século."}
]

def main():
    sb = get_client()
    
    entries = []
    for item in novas_entradas:
        dia = item["dia"]
        # Calcular semana e dia da semana de 7 em 7
        semana = ((dia - 1) // 7) + 1
        dia_semana = ((dia - 1) % 7) + 1
        
        entries.append({
            "semana": semana,
            "dia": dia,
            "dia_semana": dia_semana,
            "ref": item["ref"],
            "versiculo": item["t"],
            "status": "pending"
        })
        
    print(f"Cadastrando {len(entries)} novos dias da expansão no banco...")
    
    # Executar upsert na tabela nico_plano
    result = sb.table("nico_plano").upsert(entries, on_conflict="dia").execute()
    
    print(f"✅ Sucesso! {len(result.data)} registros populados em nico_plano.")

if __name__ == '__main__':
    main()
