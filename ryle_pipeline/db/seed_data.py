"""
Ryle Pipeline — Seed Data
Plano Devocional Anual: 52 Semanas, 364 Dias.
Gerado a partir do plano 'Caminhando com Deus: Um Ano nas Escrituras'.
"""

# Formato: (semana, dia_semana, dia_nome, mes, tema_mes, tema_semana, texto_biblico, tema_central)
# dia_semana: 1=Sáb, 2=Dom, 3=Seg, 4=Ter, 5=Qua, 6=Qui, 7=Sex

PLANO_ANUAL: list[tuple[int, int, str, int, str, str, str, str]] = [
    # ══════════════════════════════════════════════════════════════
    # MÊS 1 — A Majestade de Deus e a Miséria do Homem (Sem 1-2)
    # ══════════════════════════════════════════════════════════════
    # Semana 1 — A Visão da Glória
    (1, 1, "Sáb", 1, "A Majestade de Deus e a Miséria do Homem", "A Visão da Glória", "Isaías 6.1-7", "A visão da glória — 'Santo, Santo, Santo' e a purificação do profeta"),
    (1, 2, "Dom", 1, "A Majestade de Deus e a Miséria do Homem", "A Visão da Glória", "Salmo 99.1-5", "O Senhor reina — tremam os povos; Ele é santo"),
    (1, 3, "Seg", 1, "A Majestade de Deus e a Miséria do Homem", "A Visão da Glória", "Apocalipse 4.8-11", "O trono celestial e a adoração incessante dos seres viventes"),
    (1, 4, "Ter", 1, "A Majestade de Deus e a Miséria do Homem", "A Visão da Glória", "1 Timóteo 6.13-16", "O Rei dos reis habita em luz inacessível"),
    (1, 5, "Qua", 1, "A Majestade de Deus e a Miséria do Homem", "A Visão da Glória", "Êxodo 15.11-13", "'Quem é como Tu entre os deuses, ó SENHOR?' — Majestade e redenção"),
    (1, 6, "Qui", 1, "A Majestade de Deus e a Miséria do Homem", "A Visão da Glória", "Salmo 29.1-4", "A voz do Senhor é poderosa e cheia de majestade"),
    (1, 7, "Sex", 1, "A Majestade de Deus e a Miséria do Homem", "A Visão da Glória", "Habacuque 2.18-20", "'O SENHOR está no Seu santo templo — cale-se diante Dele!'"),
    # Semana 2 — A Depravação Total
    (2, 1, "Sáb", 1, "A Majestade de Deus e a Miséria do Homem", "A Depravação Total", "Romanos 3.10-18", "Não há justo, nem um sequer — o retrato da humanidade caída"),
    (2, 2, "Dom", 1, "A Majestade de Deus e a Miséria do Homem", "A Depravação Total", "Efésios 2.1-5", "Mortos em delitos e pecados, mas vivificados por Deus"),
    (2, 3, "Seg", 1, "A Majestade de Deus e a Miséria do Homem", "A Depravação Total", "Jeremias 17.9-10", "O coração é enganoso acima de tudo; o Senhor o esquadrinha"),
    (2, 4, "Ter", 1, "A Majestade de Deus e a Miséria do Homem", "A Depravação Total", "Salmo 51.1-5", "Em pecado me concebeu minha mãe — o clamor de Davi"),
    (2, 5, "Qua", 1, "A Majestade de Deus e a Miséria do Homem", "A Depravação Total", "Marcos 7.20-23", "Do coração procedem os maus pensamentos — a corrupção interior"),
    (2, 6, "Qui", 1, "A Majestade de Deus e a Miséria do Homem", "A Depravação Total", "Romanos 5.12-14", "Por um só homem o pecado entrou no mundo — solidariedade em Adão"),
    (2, 7, "Sex", 1, "A Majestade de Deus e a Miséria do Homem", "A Depravação Total", "João 3.19-21", "Os homens amaram mais as trevas que a luz"),
    # ══════════════════════════════════════════════════════════════
    # MÊS 2 — A Cruz e a Ressurreição (Sem 3-6)
    # ══════════════════════════════════════════════════════════════
    # Semana 3 — O Cordeiro Substituto
    (3, 1, "Sáb", 2, "A Cruz e a Ressurreição", "O Cordeiro Substituto", "Isaías 53.4-7", "Ele foi traspassado pelas nossas transgressões — o Servo sofredor"),
    (3, 2, "Dom", 2, "A Cruz e a Ressurreição", "O Cordeiro Substituto", "1 Pedro 1.17-21", "Resgatados pelo precioso sangue de Cristo, Cordeiro sem defeito"),
    (3, 3, "Seg", 2, "A Cruz e a Ressurreição", "O Cordeiro Substituto", "2 Coríntios 5.19-21", "Aquele que não conheceu pecado, Deus o fez pecado por nós"),
    (3, 4, "Ter", 2, "A Cruz e a Ressurreição", "O Cordeiro Substituto", "Hebreus 9.22-26", "Sem derramamento de sangue não há remissão — o sacrifício perfeito"),
    (3, 5, "Qua", 2, "A Cruz e a Ressurreição", "O Cordeiro Substituto", "João 1.29-34", "'Eis o Cordeiro de Deus que tira o pecado do mundo'"),
    (3, 6, "Qui", 2, "A Cruz e a Ressurreição", "O Cordeiro Substituto", "Romanos 5.6-11", "Deus prova o seu amor — Cristo morreu por nós sendo ainda pecadores"),
    (3, 7, "Sex", 2, "A Cruz e a Ressurreição", "O Cordeiro Substituto", "Apocalipse 5.9-12", "Digno é o Cordeiro que foi morto — louvor celestial"),
    # Semana 4 — O Túmulo Vazio
    (4, 1, "Sáb", 2, "A Cruz e a Ressurreição", "O Túmulo Vazio", "1 Coríntios 15.1-5", "Morreu, foi sepultado e ressuscitou ao terceiro dia"),
    (4, 2, "Dom", 2, "A Cruz e a Ressurreição", "O Túmulo Vazio", "João 11.25-27", "'Eu sou a ressurreição e a vida' — a confissão de Marta"),
    (4, 3, "Seg", 2, "A Cruz e a Ressurreição", "O Túmulo Vazio", "Lucas 24.1-7", "'Por que buscais entre os mortos ao que vive?'"),
    (4, 4, "Ter", 2, "A Cruz e a Ressurreição", "O Túmulo Vazio", "Romanos 6.3-6", "Sepultados e ressuscitados com Ele — morte para o pecado"),
    (4, 5, "Qua", 2, "A Cruz e a Ressurreição", "O Túmulo Vazio", "Filipenses 3.10-12", "O poder da Sua ressurreição e a comunhão dos seus sofrimentos"),
    (4, 6, "Qui", 2, "A Cruz e a Ressurreição", "O Túmulo Vazio", "1 Pedro 1.3-5", "Regenerados para uma viva esperança pela ressurreição"),
    (4, 7, "Sex", 2, "A Cruz e a Ressurreição", "O Túmulo Vazio", "Apocalipse 1.17-18", "'Eu sou o que vive; estive morto, eis que vivo para todo o sempre'"),
    # Semana 5 — Justificação pela Fé
    (5, 1, "Sáb", 2, "A Cruz e a Ressurreição", "Justificação pela Fé", "Romanos 5.1-5", "Justificados pela fé, temos paz com Deus"),
    (5, 2, "Dom", 2, "A Cruz e a Ressurreição", "Justificação pela Fé", "Gálatas 2.16-19", "Não pelas obras da lei, mas pela fé em Cristo Jesus"),
    (5, 3, "Seg", 2, "A Cruz e a Ressurreição", "Justificação pela Fé", "Romanos 4.3-8", "A fé é creditada como justiça — Abraão e Davi como testemunhas"),
    (5, 4, "Ter", 2, "A Cruz e a Ressurreição", "Justificação pela Fé", "Efésios 2.4-9", "Pela graça sois salvos, por meio da fé — dom de Deus"),
    (5, 5, "Qua", 2, "A Cruz e a Ressurreição", "Justificação pela Fé", "Tito 3.4-7", "Não por obras de justiça, mas pela Sua misericórdia Ele nos salvou"),
    (5, 6, "Qui", 2, "A Cruz e a Ressurreição", "Justificação pela Fé", "Filipenses 3.7-9", "A justiça que vem de Deus e se baseia na fé"),
    (5, 7, "Sex", 2, "A Cruz e a Ressurreição", "Justificação pela Fé", "Romanos 8.1-4", "Nenhuma condenação há para os que estão em Cristo Jesus"),
    # Semana 6 — União com Cristo
    (6, 1, "Sáb", 2, "A Cruz e a Ressurreição", "União com Cristo", "João 15.4-7", "'Eu sou a videira, vós as varas' — permanecei em mim"),
    (6, 2, "Dom", 2, "A Cruz e a Ressurreição", "União com Cristo", "Gálatas 2.19-21", "Já não sou eu quem vive, mas Cristo vive em mim"),
    (6, 3, "Seg", 2, "A Cruz e a Ressurreição", "União com Cristo", "Colossenses 3.1-4", "A vossa vida está oculta com Cristo em Deus"),
    (6, 4, "Ter", 2, "A Cruz e a Ressurreição", "União com Cristo", "Romanos 6.3-7", "Unidos com Ele na semelhança da Sua morte e ressurreição"),
    (6, 5, "Qua", 2, "A Cruz e a Ressurreição", "União com Cristo", "1 Coríntios 6.17-20", "Quem se une ao Senhor é um espírito com Ele — o corpo como templo"),
    (6, 6, "Qui", 2, "A Cruz e a Ressurreição", "União com Cristo", "Efésios 1.3-6", "Abençoados com toda bênção espiritual em Cristo"),
    (6, 7, "Sex", 2, "A Cruz e a Ressurreição", "União com Cristo", "João 17.21-23", "'Eu neles, e Tu em mim' — a oração sacerdotal pela unidade"),
    # ══════════════════════════════════════════════════════════════
    # MÊS 3 — A Obra do Espírito Santo (Sem 7-10)
    # ══════════════════════════════════════════════════════════════
    # Semana 7 — O Novo Nascimento
    (7, 1, "Sáb", 3, "A Obra do Espírito Santo", "O Novo Nascimento", "João 3.3-8", "'É necessário nascer de novo' — o mistério da regeneração"),
    (7, 2, "Dom", 3, "A Obra do Espírito Santo", "O Novo Nascimento", "Ezequiel 36.25-27", "O coração de pedra trocado por coração de carne"),
    (7, 3, "Seg", 3, "A Obra do Espírito Santo", "O Novo Nascimento", "Tiago 1.17-18", "Gerados pela palavra da verdade — as primícias"),
    (7, 4, "Ter", 3, "A Obra do Espírito Santo", "O Novo Nascimento", "1 Pedro 1.22-25", "Nascidos de novo pela palavra viva e permanente"),
    (7, 5, "Qua", 3, "A Obra do Espírito Santo", "O Novo Nascimento", "2 Coríntios 5.17-19", "Se alguém está em Cristo, nova criatura é"),
    (7, 6, "Qui", 3, "A Obra do Espírito Santo", "O Novo Nascimento", "Tito 3.3-7", "O lavar regenerador e renovador do Espírito Santo"),
    (7, 7, "Sex", 3, "A Obra do Espírito Santo", "O Novo Nascimento", "Efésios 2.4-7", "Estando nós mortos, Deus nos vivificou juntamente com Cristo"),
    # Semana 8 — A Guerra Interna: Carne × Espírito
    (8, 1, "Sáb", 3, "A Obra do Espírito Santo", "A Guerra Interna: Carne × Espírito", "Gálatas 5.16-21", "Andai no Espírito — a carne milita contra ele"),
    (8, 2, "Dom", 3, "A Obra do Espírito Santo", "A Guerra Interna: Carne × Espírito", "Romanos 7.18-25", "O bem que quero não faço — quem me livrará?"),
    (8, 3, "Seg", 3, "A Obra do Espírito Santo", "A Guerra Interna: Carne × Espírito", "Romanos 8.12-14", "Pelo Espírito mortificai as obras do corpo e vivereis"),
    (8, 4, "Ter", 3, "A Obra do Espírito Santo", "A Guerra Interna: Carne × Espírito", "1 Pedro 2.11-12", "Abstende-vos das paixões carnais que combatem contra a alma"),
    (8, 5, "Qua", 3, "A Obra do Espírito Santo", "A Guerra Interna: Carne × Espírito", "Colossenses 3.5-8", "Fazei morrer o que em vós é terreno"),
    (8, 6, "Qui", 3, "A Obra do Espírito Santo", "A Guerra Interna: Carne × Espírito", "Efésios 4.22-24", "Despojai-vos do velho homem, revesti-vos do novo"),
    (8, 7, "Sex", 3, "A Obra do Espírito Santo", "A Guerra Interna: Carne × Espírito", "Gálatas 6.7-10", "Quem semeia para o Espírito, do Espírito ceifará vida eterna"),
    # Semana 9 — O Consolador e a Promessa
    (9, 1, "Sáb", 3, "A Obra do Espírito Santo", "O Consolador e a Promessa", "João 14.15-18", "'Eu rogarei ao Pai e Ele vos dará outro Consolador'"),
    (9, 2, "Dom", 3, "A Obra do Espírito Santo", "O Consolador e a Promessa", "João 16.12-15", "O Espírito da verdade vos guiará a toda a verdade"),
    (9, 3, "Seg", 3, "A Obra do Espírito Santo", "O Consolador e a Promessa", "Romanos 8.14-17", "O Espírito testifica que somos filhos e herdeiros de Deus"),
    (9, 4, "Ter", 3, "A Obra do Espírito Santo", "O Consolador e a Promessa", "Efésios 1.13-14", "Selados com o Espírito Santo da promessa"),
    (9, 5, "Qua", 3, "A Obra do Espírito Santo", "O Consolador e a Promessa", "João 7.37-39", "'Rios de água viva correrão do seu interior'"),
    (9, 6, "Qui", 3, "A Obra do Espírito Santo", "O Consolador e a Promessa", "Atos 1.6-8", "Recebereis poder ao descer o Espírito Santo sobre vós"),
    (9, 7, "Sex", 3, "A Obra do Espírito Santo", "O Consolador e a Promessa", "1 Coríntios 2.10-13", "Recebemos o Espírito que provém de Deus"),
    # Semana 10 — Os Frutos da Graça
    (10, 1, "Sáb", 3, "A Obra do Espírito Santo", "Os Frutos da Graça", "Gálatas 5.22-26", "O fruto do Espírito: amor, alegria, paz"),
    (10, 2, "Dom", 3, "A Obra do Espírito Santo", "Os Frutos da Graça", "Filipenses 1.9-11", "Cheios do fruto de justiça por meio de Jesus Cristo"),
    (10, 3, "Seg", 3, "A Obra do Espírito Santo", "Os Frutos da Graça", "João 15.5-8", "Nisto é glorificado o Pai: que deis muito fruto"),
    (10, 4, "Ter", 3, "A Obra do Espírito Santo", "Os Frutos da Graça", "Efésios 5.8-11", "O fruto da luz está em toda bondade, justiça e verdade"),
    (10, 5, "Qua", 3, "A Obra do Espírito Santo", "Os Frutos da Graça", "Colossenses 1.9-12", "Frutificando em toda boa obra e crescendo no conhecimento"),
    (10, 6, "Qui", 3, "A Obra do Espírito Santo", "Os Frutos da Graça", "Tiago 3.13-18", "A sabedoria lá do alto: pura, pacífica, cheia de frutos"),
    (10, 7, "Sex", 3, "A Obra do Espírito Santo", "Os Frutos da Graça", "2 Pedro 1.5-8", "Acrescentai à fé a virtude, o conhecimento, o domínio próprio"),
    # ══════════════════════════════════════════════════════════════
    # MÊS 4 — O Custo do Discipulado (Sem 11-14)
    # ══════════════════════════════════════════════════════════════
    (11,1,"Sáb",4,"O Custo do Discipulado","Tomando a Cruz","Mateus 16.24-27","'Se alguém quer vir após mim, negue-se a si mesmo'"),
    (11,2,"Dom",4,"O Custo do Discipulado","Tomando a Cruz","Lucas 9.23-26","Tome cada dia a sua cruz — a perda e o ganho"),
    (11,3,"Seg",4,"O Custo do Discipulado","Tomando a Cruz","Marcos 8.34-38","O chamado radical do Mestre — que aproveita ganhar o mundo?"),
    (11,4,"Ter",4,"O Custo do Discipulado","Tomando a Cruz","Lucas 14.25-27","Quem não carrega a sua cruz não pode ser meu discípulo"),
    (11,5,"Qua",4,"O Custo do Discipulado","Tomando a Cruz","Lucas 14.28-33","Calcular o custo — renunciar a tudo quanto possui"),
    (11,6,"Qui",4,"O Custo do Discipulado","Tomando a Cruz","Mateus 10.37-39","'Quem não toma a sua cruz não é digno de mim'"),
    (11,7,"Sex",4,"O Custo do Discipulado","Tomando a Cruz","João 12.24-26","O grão de trigo que morre"),
    (12,1,"Sáb",4,"O Custo do Discipulado","A Porta Estreita","Mateus 7.13-14","Estreita é a porta e apertado o caminho que conduz à vida"),
    (12,2,"Dom",4,"O Custo do Discipulado","A Porta Estreita","Lucas 13.23-27","'Esforçai-vos por entrar pela porta estreita'"),
    (12,3,"Seg",4,"O Custo do Discipulado","A Porta Estreita","Provérbios 16.25-33","Há caminho que parece certo, mas seu fim é morte"),
    (12,4,"Ter",4,"O Custo do Discipulado","A Porta Estreita","João 10.7-10","'Eu sou a porta; quem entrar por mim será salvo'"),
    (12,5,"Qua",4,"O Custo do Discipulado","A Porta Estreita","Salmo 1.1-6","Bem-aventurado quem não anda no conselho dos ímpios"),
    (12,6,"Qui",4,"O Custo do Discipulado","A Porta Estreita","Provérbios 4.14-19","Não entres na vereda dos perversos"),
    (12,7,"Sex",4,"O Custo do Discipulado","A Porta Estreita","1 João 5.18-21","O mundo inteiro jaz no Maligno — guardai-vos dos ídolos"),
    (13,1,"Sáb",4,"O Custo do Discipulado","O Mundo e Suas Ilusões","1 João 2.15-17","Não ameis o mundo nem o que nele há"),
    (13,2,"Dom",4,"O Custo do Discipulado","O Mundo e Suas Ilusões","Tiago 4.4-6","A amizade do mundo é inimizade contra Deus"),
    (13,3,"Seg",4,"O Custo do Discipulado","O Mundo e Suas Ilusões","Romanos 12.1-2","Não vos conformeis com este século — transformai-vos"),
    (13,4,"Ter",4,"O Custo do Discipulado","O Mundo e Suas Ilusões","2 Timóteo 4.9-11","Demas me abandonou, amando o presente século"),
    (13,5,"Qua",4,"O Custo do Discipulado","O Mundo e Suas Ilusões","Provérbios 23.4-5","As riquezas fazem asas e voam como a águia"),
    (13,6,"Qui",4,"O Custo do Discipulado","O Mundo e Suas Ilusões","Eclesiastes 2.10-13","Vaidade de vaidades — tudo é vaidade"),
    (13,7,"Sex",4,"O Custo do Discipulado","O Mundo e Suas Ilusões","Filipenses 3.17-21","Os que só pensam nas coisas terrenas — nossa pátria está nos céus"),
    (14,1,"Sáb",4,"O Custo do Discipulado","A Perseverança dos Santos","Filipenses 1.6","Aquele que começou a boa obra, há de completá-la"),
    (14,2,"Dom",4,"O Custo do Discipulado","A Perseverança dos Santos","João 10.27-30","'Ninguém as arrebatará da minha mão'"),
    (14,3,"Seg",4,"O Custo do Discipulado","A Perseverança dos Santos","Romanos 8.35-39","Nada nos separará do amor de Deus em Cristo Jesus"),
    (14,4,"Ter",4,"O Custo do Discipulado","A Perseverança dos Santos","1 Pedro 1.3-5","Guardados pelo poder de Deus mediante a fé"),
    (14,5,"Qua",4,"O Custo do Discipulado","A Perseverança dos Santos","Judas 24-25","Àquele que é poderoso para vos guardar de tropeçar"),
    (14,6,"Qui",4,"O Custo do Discipulado","A Perseverança dos Santos","2 Timóteo 1.12-14","'Sei em quem tenho crido' — o bom depósito"),
    (14,7,"Sex",4,"O Custo do Discipulado","A Perseverança dos Santos","Hebreus 7.23-25","Ele pode salvar totalmente os que por Ele se chegam a Deus"),
    # ══════════════════════════════════════════════════════════════
    # MÊS 5 — O Cuidado Pastoral de Deus (Sem 15-18)
    # ══════════════════════════════════════════════════════════════
    (15,1,"Sáb",5,"O Cuidado Pastoral de Deus","O Bom Pastor","Salmo 23.1-6","O Senhor é o meu pastor — nada me faltará"),
    (15,2,"Dom",5,"O Cuidado Pastoral de Deus","O Bom Pastor","João 10.11-16","O bom pastor dá a vida pelas ovelhas"),
    (15,3,"Seg",5,"O Cuidado Pastoral de Deus","O Bom Pastor","Isaías 40.10-11","Como pastor apascentará o seu rebanho"),
    (15,4,"Ter",5,"O Cuidado Pastoral de Deus","O Bom Pastor","Ezequiel 34.11-16","'Eu mesmo procurarei as minhas ovelhas'"),
    (15,5,"Qua",5,"O Cuidado Pastoral de Deus","O Bom Pastor","Lucas 15.3-7","A parábola da ovelha perdida"),
    (15,6,"Qui",5,"O Cuidado Pastoral de Deus","O Bom Pastor","1 Pedro 5.1-4","O Supremo Pastor e a coroa da glória"),
    (15,7,"Sex",5,"O Cuidado Pastoral de Deus","O Bom Pastor","Hebreus 13.20-21","O grande Pastor das ovelhas e o pacto eterno"),
    (16,1,"Sáb",5,"O Cuidado Pastoral de Deus","O Deus de Todo Consolo","2 Coríntios 1.3-7","O Pai das misericórdias e Deus de toda consolação"),
    (16,2,"Dom",5,"O Cuidado Pastoral de Deus","O Deus de Todo Consolo","Salmo 34.17-20","Perto está o Senhor dos que têm o coração quebrantado"),
    (16,3,"Seg",5,"O Cuidado Pastoral de Deus","O Deus de Todo Consolo","Salmo 42.5-8","Por que estás abatida, ó minha alma? Espera em Deus"),
    (16,4,"Ter",5,"O Cuidado Pastoral de Deus","O Deus de Todo Consolo","Mateus 11.28-30","Vinde a mim todos os que estais cansados"),
    (16,5,"Qua",5,"O Cuidado Pastoral de Deus","O Deus de Todo Consolo","Romanos 8.26-28","O Espírito intercede; todas as coisas cooperam para o bem"),
    (16,6,"Qui",5,"O Cuidado Pastoral de Deus","O Deus de Todo Consolo","Salmo 46.1-5","Deus é o nosso refúgio e fortaleza"),
    (16,7,"Sex",5,"O Cuidado Pastoral de Deus","O Deus de Todo Consolo","Isaías 43.1-3","Não temas, porque eu te remi"),
    (17,1,"Sáb",5,"O Cuidado Pastoral de Deus","A Fidelidade de Deus nas Provações","Lamentações 3.22-26","As misericórdias do Senhor renovam-se cada manhã"),
    (17,2,"Dom",5,"O Cuidado Pastoral de Deus","A Fidelidade de Deus nas Provações","Tiago 1.2-4","Considerai motivo de grande alegria as diversas provações"),
    (17,3,"Seg",5,"O Cuidado Pastoral de Deus","A Fidelidade de Deus nas Provações","1 Pedro 1.6-9","A provação da fé, mais preciosa que o ouro"),
    (17,4,"Ter",5,"O Cuidado Pastoral de Deus","A Fidelidade de Deus nas Provações","Salmo 119.67-72","Foi-me bom ter sido afligido"),
    (17,5,"Qua",5,"O Cuidado Pastoral de Deus","A Fidelidade de Deus nas Provações","Hebreus 12.5-7","O Senhor corrige ao que ama"),
    (17,6,"Qui",5,"O Cuidado Pastoral de Deus","A Fidelidade de Deus nas Provações","Jó 23.8-12","Quando me provar, sairei como ouro"),
    (17,7,"Sex",5,"O Cuidado Pastoral de Deus","A Fidelidade de Deus nas Provações","2 Coríntios 12.7-10","A minha graça te basta"),
    (18,1,"Sáb",5,"O Cuidado Pastoral de Deus","A Provisão Diária do Pai","Mateus 6.25-30","Não andeis ansiosos — olhai as aves do céu"),
    (18,2,"Dom",5,"O Cuidado Pastoral de Deus","A Provisão Diária do Pai","Mateus 6.31-34","Buscai em primeiro lugar o Reino de Deus"),
    (18,3,"Seg",5,"O Cuidado Pastoral de Deus","A Provisão Diária do Pai","Filipenses 4.18-20","O meu Deus suprirá toda a vossa necessidade"),
    (18,4,"Ter",5,"O Cuidado Pastoral de Deus","A Provisão Diária do Pai","Salmo 37.3-7","Confia no Senhor e faze o bem"),
    (18,5,"Qua",5,"O Cuidado Pastoral de Deus","A Provisão Diária do Pai","Deuteronômio 8.2-5","Nem só de pão viverá o homem"),
    (18,6,"Qui",5,"O Cuidado Pastoral de Deus","A Provisão Diária do Pai","Salmo 136.23-26","Eterna é a sua misericórdia"),
    (18,7,"Sex",5,"O Cuidado Pastoral de Deus","A Provisão Diária do Pai","1 Reis 17.8-16","A farinha e o azeite da viúva"),
    # ══════════════════════════════════════════════════════════════
    # MÊS 6 — A Vida no Lar e nos Relacionamentos (Sem 19-22)
    # ══════════════════════════════════════════════════════════════
    (19,1,"Sáb",6,"A Vida no Lar e nos Relacionamentos","O Lar Cristão","Salmo 127.1-5","Se o Senhor não edificar a casa, em vão trabalham"),
    (19,2,"Dom",6,"A Vida no Lar e nos Relacionamentos","O Lar Cristão","Josué 24.14-15","'Eu e a minha casa serviremos ao Senhor'"),
    (19,3,"Seg",6,"A Vida no Lar e nos Relacionamentos","O Lar Cristão","Provérbios 22.6","Instrui o menino no caminho em que deve andar"),
    (19,4,"Ter",6,"A Vida no Lar e nos Relacionamentos","O Lar Cristão","Efésios 6.1-4","Filhos, obedecei; pais, criai na disciplina do Senhor"),
    (19,5,"Qua",6,"A Vida no Lar e nos Relacionamentos","O Lar Cristão","Colossenses 3.18-21","A ordem do lar cristão"),
    (19,6,"Qui",6,"A Vida no Lar e nos Relacionamentos","O Lar Cristão","Deuteronômio 6.4-9","Estas palavras estarão no teu coração; inculcarás a teus filhos"),
    (19,7,"Sex",6,"A Vida no Lar e nos Relacionamentos","O Lar Cristão","Salmo 128.1-4","Bem-aventurado aquele que teme ao Senhor"),
    (20,1,"Sáb",6,"A Vida no Lar e nos Relacionamentos","O Amor que Suporta e Perdoa","1 Coríntios 13.4-7","O amor é paciente, é benigno"),
    (20,2,"Dom",6,"A Vida no Lar e nos Relacionamentos","O Amor que Suporta e Perdoa","Efésios 4.30-32","Sede bondosos, compassivos, perdoando-vos"),
    (20,3,"Seg",6,"A Vida no Lar e nos Relacionamentos","O Amor que Suporta e Perdoa","Mateus 18.21-22","Perdoar setenta vezes sete"),
    (20,4,"Ter",6,"A Vida no Lar e nos Relacionamentos","O Amor que Suporta e Perdoa","Colossenses 3.12-15","Revesti-vos de compaixão, bondade, humildade"),
    (20,5,"Qua",6,"A Vida no Lar e nos Relacionamentos","O Amor que Suporta e Perdoa","Mateus 5.23-26","Vai primeiro reconciliar-te com teu irmão"),
    (20,6,"Qui",6,"A Vida no Lar e nos Relacionamentos","O Amor que Suporta e Perdoa","Provérbios 17.17","Em todo tempo ama o amigo"),
    (20,7,"Sex",6,"A Vida no Lar e nos Relacionamentos","O Amor que Suporta e Perdoa","Romanos 12.9-13","O amor sem hipocrisia"),
    (21,1,"Sáb",6,"A Vida no Lar e nos Relacionamentos","A Língua: Poder de Vida e de Morte","Tiago 3.5-10","A língua é um pequeno membro, mas incendeia grande bosque"),
    (21,2,"Dom",6,"A Vida no Lar e nos Relacionamentos","A Língua: Poder de Vida e de Morte","Provérbios 18.20-21","A morte e a vida estão no poder da língua"),
    (21,3,"Seg",6,"A Vida no Lar e nos Relacionamentos","A Língua: Poder de Vida e de Morte","Efésios 4.29-31","Não saia da vossa boca nenhuma palavra torpe"),
    (21,4,"Ter",6,"A Vida no Lar e nos Relacionamentos","A Língua: Poder de Vida e de Morte","Salmo 141.3-4","Põe guarda, Senhor, à minha boca"),
    (21,5,"Qua",6,"A Vida no Lar e nos Relacionamentos","A Língua: Poder de Vida e de Morte","Provérbios 15.1-4","A resposta branda desvia o furor"),
    (21,6,"Qui",6,"A Vida no Lar e nos Relacionamentos","A Língua: Poder de Vida e de Morte","Mateus 12.34-37","De toda palavra frívola darão conta no Dia do Juízo"),
    (21,7,"Sex",6,"A Vida no Lar e nos Relacionamentos","A Língua: Poder de Vida e de Morte","Colossenses 4.5-6","A vossa palavra seja agradável, temperada com sal"),
    (22,1,"Sáb",6,"A Vida no Lar e nos Relacionamentos","A Compaixão Prática","Mateus 25.34-40","Tive fome e me destes de comer"),
    (22,2,"Dom",6,"A Vida no Lar e nos Relacionamentos","A Compaixão Prática","Lucas 10.30-37","A parábola do bom samaritano"),
    (22,3,"Seg",6,"A Vida no Lar e nos Relacionamentos","A Compaixão Prática","Isaías 58.6-9","O jejum que Deus escolheu"),
    (22,4,"Ter",6,"A Vida no Lar e nos Relacionamentos","A Compaixão Prática","Gálatas 6.1-5","Levai as cargas uns dos outros"),
    (22,5,"Qua",6,"A Vida no Lar e nos Relacionamentos","A Compaixão Prática","1 João 3.16-18","Não amemos de palavra, mas de fato e de verdade"),
    (22,6,"Qui",6,"A Vida no Lar e nos Relacionamentos","A Compaixão Prática","Miquéias 6.6-8","Que pratiques a justiça, ames a misericórdia"),
    (22,7,"Sex",6,"A Vida no Lar e nos Relacionamentos","A Compaixão Prática","Tiago 1.27","A religião pura — visitar órfãos e viúvas"),
    # ══════════════════════════════════════════════════════════════
    # MÊS 7 — Sabedoria para a Vida e Maturidade Espiritual (Sem 23-26)
    # ══════════════════════════════════════════════════════════════
    (23,1,"Sáb",7,"Sabedoria para a Vida e Maturidade Espiritual","A Sabedoria que Vem do Alto","Provérbios 1.7-9","O temor do Senhor é o princípio do saber"),
    (23,2,"Dom",7,"Sabedoria para a Vida e Maturidade Espiritual","A Sabedoria que Vem do Alto","Tiago 1.5-8","Se algum de vós tem falta de sabedoria, peça-a a Deus"),
    (23,3,"Seg",7,"Sabedoria para a Vida e Maturidade Espiritual","A Sabedoria que Vem do Alto","Provérbios 3.5-8","Confia no Senhor de todo o teu coração"),
    (23,4,"Ter",7,"Sabedoria para a Vida e Maturidade Espiritual","A Sabedoria que Vem do Alto","1 Coríntios 1.30-31","Cristo nos foi feito sabedoria da parte de Deus"),
    (23,5,"Qua",7,"Sabedoria para a Vida e Maturidade Espiritual","A Sabedoria que Vem do Alto","Provérbios 4.5-9","A sabedoria é a coisa principal"),
    (23,6,"Qui",7,"Sabedoria para a Vida e Maturidade Espiritual","A Sabedoria que Vem do Alto","Eclesiastes 12.13-14","Teme a Deus e guarda os seus mandamentos"),
    (23,7,"Sex",7,"Sabedoria para a Vida e Maturidade Espiritual","A Sabedoria que Vem do Alto","Colossenses 2.2-4","Em Cristo estão todos os tesouros da sabedoria"),
    (24,1,"Sáb",7,"Sabedoria para a Vida e Maturidade Espiritual","A Humildade e o Contentamento","Filipenses 4.10-13","Aprendi a viver contente em toda situação"),
    (24,2,"Dom",7,"Sabedoria para a Vida e Maturidade Espiritual","A Humildade e o Contentamento","1 Timóteo 6.6-10","Grande ganho é a piedade com contentamento"),
    (24,3,"Seg",7,"Sabedoria para a Vida e Maturidade Espiritual","A Humildade e o Contentamento","Filipenses 2.3-8","Tende o mesmo sentimento de Cristo"),
    (24,4,"Ter",7,"Sabedoria para a Vida e Maturidade Espiritual","A Humildade e o Contentamento","1 Pedro 5.5-7","Cingi-vos de humildade; lançai sobre Ele a ansiedade"),
    (24,5,"Qua",7,"Sabedoria para a Vida e Maturidade Espiritual","A Humildade e o Contentamento","Mateus 20.25-28","O Filho do Homem não veio para ser servido"),
    (24,6,"Qui",7,"Sabedoria para a Vida e Maturidade Espiritual","A Humildade e o Contentamento","Salmo 131.1-3","Como a criança desmamada — a alma aquietada em Deus"),
    (24,7,"Sex",7,"Sabedoria para a Vida e Maturidade Espiritual","A Humildade e o Contentamento","Hebreus 13.5-6","Estai contentes com o que tendes"),
    (25,1,"Sáb",7,"Sabedoria para a Vida e Maturidade Espiritual","Correr e Completar a Carreira","Hebreus 12.1-3","Corramos com perseverança, olhando para Jesus"),
    (25,2,"Dom",7,"Sabedoria para a Vida e Maturidade Espiritual","Correr e Completar a Carreira","2 Timóteo 4.6-8","Combati o bom combate, completei a carreira"),
    (25,3,"Seg",7,"Sabedoria para a Vida e Maturidade Espiritual","Correr e Completar a Carreira","Filipenses 3.12-16","Prossigo para o alvo — o prêmio da vocação"),
    (25,4,"Ter",7,"Sabedoria para a Vida e Maturidade Espiritual","Correr e Completar a Carreira","1 Coríntios 9.24-27","Todos correm, mas só um recebe o prêmio"),
    (25,5,"Qua",7,"Sabedoria para a Vida e Maturidade Espiritual","Correr e Completar a Carreira","Gálatas 6.7-10","Não nos cansemos de fazer o bem"),
    (25,6,"Qui",7,"Sabedoria para a Vida e Maturidade Espiritual","Correr e Completar a Carreira","Salmo 90.10-12","Ensina-nos a contar os nossos dias"),
    (25,7,"Sex",7,"Sabedoria para a Vida e Maturidade Espiritual","Correr e Completar a Carreira","Apocalipse 2.10-11","Sê fiel até à morte, e dar-te-ei a coroa da vida"),
    (26,1,"Sáb",7,"Sabedoria para a Vida e Maturidade Espiritual","A Mordomia do Tempo e dos Talentos","Mateus 25.14-21","A parábola dos talentos — 'Sobre o pouco foste fiel'"),
    (26,2,"Dom",7,"Sabedoria para a Vida e Maturidade Espiritual","A Mordomia do Tempo e dos Talentos","Efésios 5.15-17","Remindo o tempo, porque os dias são maus"),
    (26,3,"Seg",7,"Sabedoria para a Vida e Maturidade Espiritual","A Mordomia do Tempo e dos Talentos","1 Pedro 4.10-11","Cada um administre o dom que recebeu"),
    (26,4,"Ter",7,"Sabedoria para a Vida e Maturidade Espiritual","A Mordomia do Tempo e dos Talentos","Romanos 12.3-8","Dons diferentes segundo a graça"),
    (26,5,"Qua",7,"Sabedoria para a Vida e Maturidade Espiritual","A Mordomia do Tempo e dos Talentos","1 Coríntios 4.1-2","Despenseiros dos mistérios de Deus"),
    (26,6,"Qui",7,"Sabedoria para a Vida e Maturidade Espiritual","A Mordomia do Tempo e dos Talentos","Lucas 12.42-44","O mordomo fiel e prudente"),
    (26,7,"Sex",7,"Sabedoria para a Vida e Maturidade Espiritual","A Mordomia do Tempo e dos Talentos","Colossenses 3.23-24","Fazei-o de todo o coração, como ao Senhor"),
]


def get_all_entries() -> list[dict]:
    """Retorna todas as 364 entradas como dicts prontos para insert."""
    from .seed_data_part2 import PLANO_ANUAL_PART2
    full = PLANO_ANUAL + PLANO_ANUAL_PART2
    return [
        {
            "semana": s, "dia_semana": d, "dia_nome": dn,
            "mes": m, "tema_mes": tm, "tema_semana": ts,
            "texto_biblico": tb, "tema_central": tc,
            "status": "pending",
        }
        for s, d, dn, m, tm, ts, tb, tc in full
    ]

