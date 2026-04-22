/**
 * llm.ts — Utilitário compartilhado de chamada LLM para as API routes
 * Provider ativo: openrouter (fetch nativo, sem dependências externas)
 * Fallback: gemini via openrouter compatível
 */

export async function callLLM(
  systemPrompt: string,
  userMessage: string,
  modelOverride?: string
): Promise<string> {
  const provider = process.env.LLM_PROVIDER || 'openrouter';

  /* ── OpenRouter (default — fetch nativo, sem SDK) ───────── */
  if (provider === 'openrouter') {
    const model =
      modelOverride ?? process.env.OPENROUTER_MODEL ?? 'google/gemini-2.5-flash';

    const res = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.OPENROUTER_API_KEY}`,
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://trilhagracasoberana.vercel.app',
        'X-Title': 'Trilha da Graça Soberana',
      },
      body: JSON.stringify({
        model,
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userMessage },
        ],
      }),
    });

    if (!res.ok) {
      const errText = await res.text();
      throw new Error(`OpenRouter error ${res.status}: ${errText}`);
    }

    const data = await res.json() as {
      choices?: Array<{ message?: { content?: string } }>;
    };
    return data.choices?.[0]?.message?.content ?? '';
  }

  /* ── Gemini direto via REST (sem SDK) ───────────────────── */
  if (provider === 'gemini') {
    const geminiModel =
      process.env.GEMINI_MODEL || 'gemini-2.5-flash';
    const apiKey = process.env.GEMINI_API_KEY!;
    const url = `https://generativelanguage.googleapis.com/v1beta/models/${geminiModel}:generateContent?key=${apiKey}`;

    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        systemInstruction: { parts: [{ text: systemPrompt }] },
        contents: [{ role: 'user', parts: [{ text: userMessage }] }],
      }),
    });

    if (!res.ok) {
      const errText = await res.text();
      throw new Error(`Gemini error ${res.status}: ${errText}`);
    }

    const data = await res.json() as {
      candidates?: Array<{ content?: { parts?: Array<{ text?: string }> } }>;
    };
    return data.candidates?.[0]?.content?.parts?.[0]?.text ?? '';
  }

  throw new Error(`Provider não suportado: ${provider}`);
}
