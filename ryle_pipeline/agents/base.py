"""
Ryle Pipeline — BaseAgent
Classe base com chamada LLM genérica (Gemini / OpenAI / Anthropic).
"""
import json
import re
from pathlib import Path
from .. import config


def _load_prompt(filename: str) -> str:
    """Carrega system prompt de um arquivo .md."""
    path = config.PROMPTS_DIR / filename
    return path.read_text(encoding="utf-8")


def _extract_json(text: str) -> dict:
    """Extrai JSON de uma resposta LLM (ignora markdown fences)."""
    # Tenta encontrar JSON dentro de ```json ... ```
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    # Tenta parse direto
    text = text.strip()
    if text.startswith("{"):
        return json.loads(text)
    raise ValueError(f"Não foi possível extrair JSON da resposta:\n{text[:500]}")


class BaseAgent:
    """Agente base com chamada LLM configurável."""

    def __init__(self, system_prompt_file: str):
        self.system_prompt = _load_prompt(system_prompt_file)
        self.provider = config.LLM_PROVIDER
        self.model = config.get_llm_model()
        self._client = None

    def _get_gemini_client(self):
        """Lazy init do client Gemini."""
        if self._client is None:
            from google import genai
            self._client = genai.Client(api_key=config.GEMINI_API_KEY)
        return self._client

    def call_llm(self, user_message: str) -> str:
        """Chama o LLM e retorna a resposta como string."""
        if self.provider == "gemini":
            return self._call_gemini(user_message)
        elif self.provider == "openai":
            return self._call_openai(user_message)
        elif self.provider == "anthropic":
            return self._call_anthropic(user_message)
        elif self.provider == "openrouter":
            return self._call_openrouter(user_message)
        else:
            raise ValueError(f"Provider не suportado: {self.provider}")

    def call_llm_json(self, user_message: str) -> dict:
        """Chama o LLM e retorna a resposta parseada como JSON."""
        raw = self.call_llm(user_message)
        return _extract_json(raw)

    def _call_gemini(self, user_message: str) -> str:
        import time
        from google.genai.errors import APIError
        client = self._get_gemini_client()
        
        for tentativa in range(3):
            try:
                response = client.models.generate_content(
                    model=self.model,
                    contents=user_message,
                    config={
                        "system_instruction": self.system_prompt,
                        "temperature": 0.7,
                        "max_output_tokens": 8192,
                    },
                )
                return response.text
            except APIError as e:
                # Tratar erro 429 Too Many Requests
                if "429" in str(e) or "quota" in str(e).lower() or "exhausted" in str(e).lower():
                    if tentativa < 2:
                        print(f"\n[Aviso] Rate limit atingido. Aguardando 15s antes da tentativa {tentativa + 2}...")
                        time.sleep(15)
                    else:
                        raise e
                else:
                    raise e
        return ""

    def _call_openai(self, user_message: str) -> str:
        from openai import OpenAI
        if self._client is None:
            self._client = OpenAI(api_key=config.OPENAI_API_KEY)
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.7,
            max_tokens=8192,
        )
        return response.choices[0].message.content

    def _call_anthropic(self, user_message: str) -> str:
        from anthropic import Anthropic
        if self._client is None:
            self._client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
        response = self._client.messages.create(
            model=self.model,
            max_tokens=8192,
            system=self.system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text

    def _call_openrouter(self, user_message: str) -> str:
        import time
        from openai import OpenAI
        from openai import RateLimitError
        if self._client is None or not hasattr(self._client, 'base_url') or "openrouter" not in str(self._client.base_url):
            self._client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=config.OPENROUTER_API_KEY
            )
            
        for tentativa in range(3):
            try:
                response = self._client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    temperature=0.7,
                )
                # Log token usage if available
                if hasattr(response, 'usage') and response.usage:
                    import logging
                    logging.getLogger("ryle_pipeline").info(
                        f"Tokens: input={response.usage.prompt_tokens} output={response.usage.completion_tokens} model={self.model}"
                    )
                return response.choices[0].message.content
            except RateLimitError as e:
                if tentativa < 2:
                    print(f"\n[Aviso] Rate limit do OpenRouter atingido. Aguardando 15s antes da tentativa {tentativa + 2}...")
                    time.sleep(15)
                else:
                    raise e
        return ""
