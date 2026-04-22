# Guia de Manutenção UI / Next.js

A aplicação cliente em React faz parte da stack robusta para a Trilha Graça Soberana, arquitetada como interface de consumo e leitura dos devocionais. O repositório está dentro do diretório `/web`.

## Estrutura Base
A aplicação usa o `App Router` do Next.js (versão recente), portanto o scaffolding principal ocorre em:
- `/web/app/`: Central de todas as rotas (página de cada devocional mapeado por semanas/dias, e layouts).
- `/web/components/`: Componentes UI reaproveitáveis.
- Estilos aplicados através de `.module.css` e de declarações globais (`globals.css`), prezando pelo "Vanilla CSS" modular em boa parte, podendo incorporar tokens caso um Design System seja mais robusto posteriormente.

## Rodando o Frontend

Para o modo de desenvolvimento:
```powershell
cd web
npm run dev
```

Estará exposto tipicamente em `http://localhost:3000`.

### Integração com o Banco de Dados (Supabase)
O projeto faz chamadas baseadas na library de cliente `@supabase/supabase-js`. 
-  Certifique-se de que o `.env.local` contenha as credenciais `NEXT_PUBLIC_SUPABASE_URL` e `NEXT_PUBLIC_SUPABASE_ANON_KEY`. 
- Sem essas variáveis, nenhum devocional/exegese vai renderizar ou as requisições API Server Components quebrarão.

### UI e Design Empregado
O design da plataforma foi alinhado a altos padrões estéticos e interativos:
- **Glassmorphism:** Efeitos de vidro (desfoque/backdrop-filter e uso moderado de opacidades nas variações de cores de fundo)
- **Animações / UX:** Efeitos de hover e transições suaves incentivam o acoplamento do devocional com o usuário, conferindo sensação vívida ao sistema.
- Ao atualizar essa frente, evite usar marcações HTML genéricas. Utilize classes robustas, fontes Google tipográficas e estruturação semântica de `headings`.

### Teste de Build
Para assegurar a não existência de Erros TypeScript graves e consistência das rotas dinâmicas, antes de Deploy em nuvem prefigurado na Vercel ou Railway, sempre valide o build do ecossistema Next.js via:
```powershell
npm run build
```
Não realize PR em produção na branch master sem ter certeza desse retorno de Sucesso. O Build deve gerar todas as Rotas do roteamento dinâmico App Router limpas.
