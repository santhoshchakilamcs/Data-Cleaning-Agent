"""LLM Provider abstraction for Auto-Janitor"""

from abc import ABC, abstractmethod
from typing import List, Dict
from enum import Enum

from auto_janitor.config import Config


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class BaseLLM(ABC):
    """Base class for LLM providers"""
    
    @abstractmethod
    def generate(self, messages: List[Dict[str, str]]) -> str:
        """Generate a response from the LLM"""
        pass


class OpenAILLM(BaseLLM):
    """OpenAI GPT-4o provider"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def generate(self, messages: List[Dict[str, str]]) -> str:
        """Generate a response using OpenAI API"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.1,
            max_tokens=4000
        )
        return response.choices[0].message.content


class AnthropicLLM(BaseLLM):
    """Anthropic Claude provider"""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        from anthropic import Anthropic
        self.client = Anthropic(api_key=api_key)
        self.model = model
    
    def generate(self, messages: List[Dict[str, str]]) -> str:
        """Generate a response using Anthropic API"""
        # Separate system message from conversation
        system_message = ""
        conversation_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                conversation_messages.append(msg)
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            temperature=0.1,
            system=system_message,
            messages=conversation_messages
        )
        return response.content[0].text


def get_llm(provider: str = None, model: str = None) -> BaseLLM:
    """Factory function to get the appropriate LLM provider"""
    provider = provider or Config.LLM_PROVIDER
    model = model or Config.MODEL_NAME
    
    if provider == LLMProvider.OPENAI:
        if not Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment")
        return OpenAILLM(api_key=Config.OPENAI_API_KEY, model=model)
    
    elif provider == LLMProvider.ANTHROPIC:
        if not Config.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        return AnthropicLLM(api_key=Config.ANTHROPIC_API_KEY, model=model)
    
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

