import os
import re
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

SYSTEM_INSTRUCTION = """Você é um renomado Professor de Teologia Reformada e Aconselhamento Bíblico, profundamente influenciado pelo estilo direto, solene e pastoral de J.C. Ryle.
Sua tarefa é receber o esboço de um devocional simples e curto e reescrevê-lo inteiramente, transformando-o em uma Aula Teológico-Prática de Aconselhamento Bíblico muito mais extensa, profunda e acadêmica, com cerca de 800 a 1000 palavras.

Você DEVE seguir rigorosamente esta estrutura de markdown para a sua resposta (e NADA mais):

### I. Introdução e Contexto Exegético
[Desenvolva uma introdução histórica e teológica do texto bíblico. Analise as palavras originais no grego ou hebraico que sejam relevantes para o aconselhamento bíblico (por exemplo, termos para coração, mente, desejos, etc.), conectando a exegese à mensagem do texto.]

### II. Princípios de Aconselhamento Bíblico (Exposição)
[Desenvolva três pontos sistemáticos e aprofundados (I, II e III), cada um com vários parágrafos. Use o estilo de J.C. Ryle: interpele o leitor como "Leitor" ou "Meu amigo", use perguntas perscrutadoras do coração, e apresente forte confronto contra a teologia humanista/psicologia secular e exalte a suficiência de Cristo e da Escritura. Fale sobre adoração do coração, noologia da queda, ídolos do coração, e a dinâmica bíblica de despir-se/revestir-se (Efésios 4).]

### III. Aplicação e Caso Clínico (Estudo de Caso)
[Apresente um caso prático (estudo de caso clínico) fictício, detalhando um aconselhado realista com problemas modernos (casamento, ansiedade, medo, ira, etc.). Mostre como o conselheiro identifica o autoengano no "problema apresentado" e como o direciona para a raiz idólatra do coração e a cura pelo evangelho.]

### IV. Perguntas de Laboratório e Discussão
[Crie 3 perguntas reflexivas e profundas para autoanálise, estudo pessoal ou em grupo de aconselhamento.]"""

FEW_SHOT_EXAMPLE_USER = """Reescreva o seguinte devocional simples:

## Dia 1 — Enganoso É o Coração

*"Enganoso é o coração, mais do que tudo; e desesperadamente corrupto; quem o conhecerá?"*
— Jeremias 17.9 (ARA)

Leitor, não há diagnóstico mais honesto da condição humana do que este versículo. Não a psicologia moderna, não a filosofia antiga, não a medicina contemporânea — nenhum sistema produziu uma análise tão precisa do problema fundamental do ser humano.
O coração é enganoso. E é enganoso "mais do que tudo" — além de qualquer coisa que você possa imaginar. A profundidade do engano não é apenas ocasional — é constitutiva.
Há duas coisas que quero mostrar. Primeira: o que este versículo revela sobre o coração humano. Segunda: por que esta verdade é o ponto de partida do aconselhamento bíblico.
I. O que este versículo revela sobre o coração humano.
..."""

FEW_SHOT_EXAMPLE_ASSISTANT = """### I. Introdução e Contexto Exegético

Para compreendermos o aconselhamento bíblico em sua raiz, precisamos primeiro nos submeter ao diagnóstico que o próprio Criador faz da alma humana. No capítulo 17 de seu livro, o profeta Jeremias escreve sob a tensão da iminente invasão babilônica. O povo de Judá havia colocado sua confiança em alianças geopolíticas, em homens e na sua própria força militar (v. 5). O profeta contrasta o homem que confia no homem (que é como um arbusto solitário no deserto) com o homem que confia no Senhor (que é como uma árvore plantada junto às águas).

No verso 9, Jeremias desce à causa primária da apostasia de Judá e de todo o gênero humano: o estado anatômico de sua vida interior.

No hebraico, o termo traduzido por "coração" é *leb* (ou *lebab*). Na antropologia bíblica, o coração não representa meramente a sede das emoções ou dos sentimentos românticos, como a cultura ocidental contemporânea sugere. O coração é o centro integrador da personalidade humana: engloba a mente (intelecto), as afeições (emoções) e a vontade (volição). É o dínamo existencial do homem. 

Duas palavras hebraicas qualificam este coração em Jeremias 17.9:
1. **Enganoso (*'aqob*):** A raiz de *'aqob* aponta para algo tortuoso, cheio de dobras, acidentado e fraudulento. É a mesma raiz do nome *Ya'aqob* (Jacó), aquele que suplanta ou que engana pegando pelo calcanhar. O coração humano não é uma linha rota; ele é um labirinto fraudulento.
2. **Desesperadamente Corrupto (*anash*):** O termo *anash* descreve uma enfermidade física que é mortal e incurável por meios humanos. Fala de um estado de fragilidade incurável. O coração está terminalmente doente no que tange às suas próprias capacidades de autocura.

### II. Princípios de Aconselhamento Bíblico (Exposição)

#### 1. O Coração como Dínamo Volitivo e a Ilusão da Neutralidade Moral
Diferente das teorias psicológicas seculares que concebem o homem como uma tabula rasa passiva, governada estritamente por forças ambientais ou químicas, a antropologia bíblica estabelece que o homem é um ser ativa e inevitavelmente adorador. O coração (*leb*) funciona como o centro de gravidade volitiva da alma humana. Não existe neutralidade moral no aconselhamento. Conforme Romanos 1.25, a dinâmica profunda do coração opera sempre em termos de adoração: ou se adora o Criador, ou a criatura. 

Neste sentido, a conduta externa (o fruto) é uma extensão imediata e lógica daquilo que governa o coração (a raiz). Desejos que inicialmente parecem legítimos e inofensivos — como o anseio por aprovação, conforto ou segurança — ao se instalarem no coração, rapidamente passam de "desejos" (*epithumia*) para "exigências soberanas". O comportamento pecaminoso surge quando o homem está disposto a pecar para obter o que deseja, ou pecar porque foi privado do que desejava. O aconselhamento bíblico sistemático rejeita diagnósticos meramente sintomáticos (como os contidos no DSM-5) que reduzem conflitos espirituais a transtornos puramente clínicos, e redireciona o foco para o nível de idolatria no trono do coração.

#### 2. Os Efeitos Noéticos da Queda e os Mecanismos Epistêmicos de Autoengano
A natureza *'aqob* do coração caída descreve o que a teologia reformada chama de *efeitos noéticos da queda* — a corrupção da própria capacidade humana de raciocinar e discernir a verdade moral (Efésios 4.17-18). O autoengano não é um processo passivo de ignorância intelectual; é uma resistência ativa, uma supressão epistêmica da verdade em prol da injustiça (Romanos 1.18). O coração caído funciona como um editor literário desonesto: ele reescreve a história das nossas falhas morais para construir uma narrativa de autodefesa e autojustificação.

No gabinete de aconselhamento, essa noética caída se traduz em mecanismos sofisticados de transferência de culpa, racionalização teológica e minimização do pecado. O aconselhado raramente apresenta o problema real no primeiro contato. Ele apresenta o "problema formatado por seu autoengano" — onde ele se posiciona como vítima inevitável e injustiçada de terceiros ou de suas próprias circunstâncias biológicas. O conselheiro bíblico não pode adotar uma postura de escuta puramente passiva que valide a narrativa defensiva do aconselhado. Ele deve usar a Palavra como um bisturi exegético, aplicando perguntas de diagnóstico que perfurem a racionalização e exponham a real motivação idólatra.

#### 3. A Dinâmica de Despir-se/Revestir-se (Efésios 4.22-24) vs. Terapias de Manejo Comportamental
Se o diagnóstico divino é de que o coração é *anash* (incurável e terminalmente enfermo por meios humanos), qualquer metodologia de aconselhamento que se baseie em autoajuda, reforço positivo ou estratégias cognitivo-comportamentais puramente humanas é equivalente a aplicar maquiagem sobre um cadáver. O homem caído não precisa de reabilitação ou de um novo "coping mechanism" (mecanismo de enfrentamento); ele precisa de ressurreição espiritual e regeneração soberana.

O verdadeiro aconselhamento bíblico opera na dinâmica descrita por Paulo em Efésios 4.22-24: o despir-se do velho homem (arrependimento e crucificação do eu), a renovação na mente pela verdade de Deus, e o revestir-se do novo homem (santificação progressiva). A mudança bíblica exige a morte do ídolo e o nascimento de uma nova afeição por Cristo (a "força expulsiva de uma nova afeição", como afirmava Thomas Chalmers). O conselheiro bíblico não busca fazer com que o aconselhado simplesmente controle sua ira ou gerencie sua ansiedade; ele trabalha para que o aconselhado ame a Cristo acima de sua própria reputação ou conforto, gerando uma transformação ontológica e duradoura sustentada pelo Espírito Santo.

### III. Aplicação e Caso Clínico (Estudo de Caso)

**O Caso de Roberto:**
Roberto, 42 anos, procurou aconselhamento pastoral alegando que seu casamento estava destruído por causa da "agressividade verbal e falta de respeito" de sua esposa, Sandra. Em sua narrativa inicial, Roberto descrevia-se como um marido paciente, trabalhador e calmo, que simplesmente "explodia" ocasionalmente quando Sandra o pressionava com cobranças financeiras e críticas ao seu desempenho.

**A Análise do Coração:**
Ao aplicar Jeremias 17.9 ao caso, o conselheiro percebeu o mecanismo de autoengano (*'aqob*) de Roberto. Ele justificava suas explosões de raiva como "reações legítimas de um homem cansado de ser atacado". Durante as sessões, por meio de perguntas direcionadas às suas motivações íntimas, Roberto foi confrontado com o fato de que seu maior desejo (seu ídolo funcional) era o conforto pessoal e o controle absoluto sobre seu tempo livre. 

Quando Sandra trazia demandas legítimas da casa, Roberto via a esposa não como uma companheira que precisava de ajuda, mas como um obstáculo que bloqueava seu ídolo do conforto. A raiva de Roberto não nascia nas palavras de Sandra, mas em seu próprio coração que idolatrava o descanso egoísta. 

Somente quando Roberto reconheceu a deformidade de seu coração (*anash*) e parou de culpar as circunstâncias, pôde experimentar o perdão em Cristo e começar a amar sua esposa sacrificialmente.

### IV. Perguntas de Laboratório e Discussão

1. **Rastreando a Raiz:** Quando você reage com ira, ansiedade ou frustração diante de uma contrariedade, qual é a narrativa de autojustificativa que seu coração constrói imediatamente? Como essa narrativa mascara seu pecado?
2. **Identificando Ídolos do Coração:** Pense em um conflito relacional recente. O que você queria tanto naquele momento que estava disposto a pecar (ou fazer o outro sofrer) para conseguir? (Lembre-se: desejos bons podem se tornar ídolos governantes).
3. **Dependência da Graça:** De que maneiras práticas você tem tentado corrigir suas fraquezas espirituais confiando em suas próprias resoluções de força de vontade, em vez de recorrer diariamente à confissão sincera e ao poder transformador do Evangelho."""


def parse_original_series(file_path):
    content = file_path.read_text(encoding="utf-8")
    
    # Extract week changes
    lines = content.splitlines()
    week_map = {}
    current_week = ""
    
    for line in lines:
        if line.startswith("## SEMANA") or line.startswith("## EIXO"):
            current_week = line.strip()
        elif line.startswith("## Dia "):
            match = re.match(r"## Dia (\d+)", line)
            if match:
                day_num = int(match.group(1))
                week_map[day_num] = current_week
                
    parts = re.split(r'\n(## Dia \d+ —[^\n]*)', content)
    header = parts[0].strip()
    
    days = {}
    for i in range(1, len(parts), 2):
        day_header = parts[i].strip()
        day_body = parts[i+1].strip()
        
        match = re.match(r"## Dia (\d+) — (.+)", day_header)
        if match:
            day_num = int(match.group(1))
            title = match.group(2).strip()
            days[day_num] = {
                "day_header": day_header,
                "title": title,
                "body": day_body,
                "week_header": week_map.get(day_num, "")
            }
            
    return header, days


def generate_counseling_lesson(client, provider, model, day_num, day_data):
    prompt_user = f"""Reescreva o seguinte devocional simples no formato de uma Aula Teológico-Prática de Aconselhamento Bíblico, conforme as regras:

{day_data['day_header']}

{day_data['body']}"""

    for attempt in range(5):
        try:
            if provider == "openrouter":
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": SYSTEM_INSTRUCTION},
                        {"role": "user", "content": FEW_SHOT_EXAMPLE_USER},
                        {"role": "assistant", "content": FEW_SHOT_EXAMPLE_ASSISTANT},
                        {"role": "user", "content": prompt_user}
                    ],
                    temperature=0.7,
                )
                return response.choices[0].message.content
            else:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt_user,
                    config={
                        "system_instruction": SYSTEM_INSTRUCTION,
                        "temperature": 0.7,
                        "max_output_tokens": 8192,
                    }
                )
                return response.text
        except Exception as e:
            wait_time = 30 * (attempt + 1)
            print(f"API Error ({e}) for Day {day_num}. Waiting {wait_time}s before retry {attempt + 1}...")
            time.sleep(wait_time)
            
    raise RuntimeError(f"Failed to generate Day {day_num} after 5 attempts.")


def main():
    root_dir = Path(__file__).parent.parent
    load_dotenv(root_dir / ".env", override=True)
    
    provider = os.getenv("LLM_PROVIDER", "openrouter")
    print(f"Using provider: {provider}")
    
    if provider == "openrouter":
        api_key = os.getenv("OPENROUTER_API_KEY", "")
        if not api_key:
            print("Error: OPENROUTER_API_KEY is not set.")
            return
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        model = os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash")
    else:
        from google import genai
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            print("Error: GEMINI_API_KEY is not set.")
            return
        client = genai.Client(api_key=api_key)
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
    print(f"Using model: {model}")
    
    src_file = root_dir / "novos" / "serie3-aconselhamento-biblico-21-devocionais.md"
    dest_file = root_dir / "scratch" / "serie3-aconselhamento-biblico-21-devocionais-enriched.md"
    checkpoints_dir = root_dir / "scratch" / "counseling_checkpoints"
    
    checkpoints_dir.mkdir(parents=True, exist_ok=True)
    
    print("Parsing original series...")
    header, days = parse_original_series(src_file)
    print(f"Parsed {len(days)} days successfully.")
    
    # Initialize Day 1 in checkpoints if not exists
    day1_file = checkpoints_dir / "day_1.txt"
    if not day1_file.exists():
        day1_file.write_text(FEW_SHOT_EXAMPLE_ASSISTANT.strip(), encoding="utf-8")
        print("Initialized Day 1 checkpoint.")
        
    # Generate Days 2 to 21
    for day_num in sorted(days.keys()):
        day_data = days[day_num]
        ckpt_file = checkpoints_dir / f"day_{day_num}.txt"
        
        print(f"\n--- Checking Day {day_num}/21: {day_data['title']} ---")
        
        if ckpt_file.exists():
            print(f"Day {day_num} already exists in checkpoints. Skipping API call.")
            continue
            
        print("Calling API to enrich...")
        lesson_body = generate_counseling_lesson(client, provider, model, day_num, day_data)
        
        lesson_body = lesson_body.strip()
        if lesson_body.startswith("#") or lesson_body.startswith("##"):
            idx = lesson_body.find("### I.")
            if idx != -1:
                lesson_body = lesson_body[idx:]
                
        ckpt_file.write_text(lesson_body, encoding="utf-8")
        print(f"Saved checkpoint: {ckpt_file}")
        
        # Brief pause to avoid rate limits
        time.sleep(2)
        
    # Assemble all days
    print("\nReassembling entire file from checkpoints...")
    enriched_content = []
    enriched_content.append(header)
    enriched_content.append("\n")
    
    current_week = ""
    for day_num in sorted(days.keys()):
        day_data = days[day_num]
        ckpt_file = checkpoints_dir / f"day_{day_num}.txt"
        
        if day_data["week_header"] and day_data["week_header"] != current_week:
            current_week = day_data["week_header"]
            enriched_content.append("\n---\n\n" + current_week + "\n\n---\n")
            
        enriched_content.append("\n" + day_data["day_header"] + "\n\n")
        
        lines = day_data["body"].splitlines()
        verse_lines = []
        is_verse = True
        
        for line in lines:
            if is_verse:
                if line.strip() == "" or (len(verse_lines) > 0 and not (line.strip().startswith("*") or line.strip().startswith("—") or line.strip().startswith(">"))):
                    is_verse = False
                else:
                    if line.strip() != "":
                        verse_lines.append(line)
            else:
                break
                
        enriched_content.append("\n".join(verse_lines) + "\n\n")
        
        body_text = ckpt_file.read_text(encoding="utf-8")
        enriched_content.append(body_text + "\n\n---\n")
        
    final_text = "".join(enriched_content)
    if final_text.endswith("\n---\n"):
        final_text = final_text[:-5]
    elif final_text.endswith("---\n"):
        final_text = final_text[:-4]
        
    dest_file.write_text(final_text, encoding="utf-8")
    print(f"\nDone! Enriched file saved to: {dest_file}")
    
    original_dest = src_file
    original_dest.write_text(final_text, encoding="utf-8")
    print(f"Original file successfully overwritten at: {original_dest}")

if __name__ == "__main__":
    main()
