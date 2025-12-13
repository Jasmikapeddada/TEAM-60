"""
LLM Client Utility - Unified interface for Groq/OpenAI
"""
import openai
from config.settings import LLM_PROVIDER, LLM_MODEL, LLM_API_KEY, LLM_API_BASE, LLM_TEMPERATURE, LLM_MAX_TOKENS


class LLMClient:
    """Unified LLM client for Groq and OpenAI"""
    
    def __init__(self, api_key=None, provider=None):
        self.provider = provider or LLM_PROVIDER
        self.api_key = api_key or LLM_API_KEY
        self.base_url = LLM_API_BASE if self.provider == "groq" else "https://api.openai.com/v1"
        self.model = LLM_MODEL
        
        if not self.api_key:
            raise ValueError(f"{self.provider.upper()}_API_KEY not found. Set it as environment variable or in UI.")
        
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def chat_completion(self, messages, model=None, temperature=None, max_tokens=None):
        """
        Generate chat completion.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (defaults to configured model)
            temperature: Temperature (defaults to configured value)
            max_tokens: Max tokens (defaults to configured value)
        
        Returns:
            Response text
        """
        try:
            response = self.client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                temperature=temperature if temperature is not None else LLM_TEMPERATURE,
                max_tokens=max_tokens or LLM_MAX_TOKENS
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"LLM API error: {str(e)}")
    
    def chat_completion_stream(self, messages, model=None, temperature=None):
        """Stream chat completion (for real-time responses in UI)."""
        try:
            stream = self.client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                temperature=temperature if temperature is not None else LLM_TEMPERATURE,
                stream=True
            )
            return stream
        except Exception as e:
            raise Exception(f"LLM API error: {str(e)}")


def get_llm_client(api_key=None, provider=None):
    """Factory function to get LLM client."""
    return LLMClient(api_key=api_key, provider=provider)

