"""
Shared LLM Service

Provides unified access to OpenAI and Groq language models.
Agents call this instead of managing their own LLM clients.
"""

import logging
from functools import lru_cache

from ..config import get_settings

logger = logging.getLogger("botivate.core.llm")


class LLMService:
    """Unified LLM client supporting OpenAI and Groq."""

    def __init__(self):
        self.settings = get_settings()
        self._openai_client = None
        self._groq_client = None

    @property
    def openai_client(self):
        """Lazy-loaded OpenAI client."""
        if self._openai_client is None:
            if not self.settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY not configured")
            from openai import AsyncOpenAI
            self._openai_client = AsyncOpenAI(api_key=self.settings.openai_api_key)
        return self._openai_client

    @property
    def groq_client(self):
        """Lazy-loaded Groq client."""
        if self._groq_client is None:
            if not self.settings.groq_api_key:
                raise ValueError("GROQ_API_KEY not configured")
            from groq import AsyncGroq
            self._groq_client = AsyncGroq(api_key=self.settings.groq_api_key)
        return self._groq_client

    async def chat_openai(
        self,
        messages: list[dict],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """Send a chat completion request to OpenAI."""
        model = model or self.settings.openai_model
        response = await self.openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    async def chat_groq(
        self,
        messages: list[dict],
        model: str = "llama-3.1-70b-versatile",
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """Send a chat completion request to Groq."""
        response = await self.groq_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    async def chat(
        self,
        messages: list[dict],
        provider: str = "openai",
        **kwargs,
    ) -> str:
        """
        Unified chat interface. Picks the provider automatically.

        Args:
            messages: Chat messages in [{"role": ..., "content": ...}] format
            provider: "openai" or "groq"
        """
        if provider == "groq":
            return await self.chat_groq(messages, **kwargs)
        return await self.chat_openai(messages, **kwargs)

    def get_langchain_llm(self, provider: str = "openai"):
        """Return a LangChain-compatible LLM instance."""
        if provider == "groq":
            from langchain_community.chat_models import ChatGroq
            return ChatGroq(
                groq_api_key=self.settings.groq_api_key,
                model_name="llama-3.1-70b-versatile",
                temperature=0.7,
            )
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            api_key=self.settings.openai_api_key,
            model=self.settings.openai_model,
            temperature=0.7,
        )


@lru_cache()
def get_llm_service() -> LLMService:
    """Cached LLM service instance."""
    return LLMService()
