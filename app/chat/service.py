"""
Chat Service - handles LLM API calls for chat response generation.
"""

import json
import time
from typing import Optional

import httpx

from app.config import settings
from app.chat.prompts import build_chat_messages


class ChatService:
    """Service for generating chat responses using LLM."""
    
    def __init__(self):
        self.provider = settings.llm_provider
        self.timeout = settings.timeout
        self._setup_provider()
    
    def _setup_provider(self):
        """Setup provider-specific configuration."""
        configs = {
            "groq": {
                "api_key": settings.groq_api_key,
                "model": settings.groq_model,
                "base_url": settings.groq_api_base_url,
            },
            "openai": {
                "api_key": settings.openai_api_key,
                "model": settings.openai_model,
                "base_url": settings.openai_api_base_url,
            },
            "grok": {
                "api_key": settings.grok_api_key,
                "model": settings.grok_model,
                "base_url": settings.grok_api_base_url,
            },
            "gemini": {
                "api_key": settings.gemini_api_key,
                "model": settings.gemini_model,
                "base_url": None,
            },
        }
        
        config = configs.get(self.provider, configs["groq"])
        self.api_key = config["api_key"]
        self.model = config["model"]
        self.base_url = config["base_url"]
    
    @property
    def is_configured(self) -> bool:
        """Check if service is configured."""
        return bool(self.api_key)
    
    def get_model_name(self) -> str:
        """Get current model name."""
        return self.model
    
    async def generate(self, query: str) -> dict:
        """
        Generate a chat response.
        
        Returns:
            dict with: primary_tag, primary_confidence, secondary_tag, secondary_confidence, 
            interpreted_query, response, suggestions, related_topics, processing_time_ms
        """
        if not self.is_configured:
            raise ValueError(f"{self.provider} API key not configured")
        
        start_time = time.perf_counter()
        
        messages = build_chat_messages(query)
        
        if self.provider == "gemini":
            result = await self._call_gemini(messages)
        else:
            result = await self._call_openai_compatible(messages)
        
        processing_time = int((time.perf_counter() - start_time) * 1000)
        
        # Parse result
        parsed = self._parse_response(result)
        parsed["processing_time_ms"] = processing_time
        
        return parsed
    
    async def _call_openai_compatible(self, messages: list[dict]) -> str:
        """Call OpenAI-compatible API (Groq, OpenAI, Grok)."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": settings.llm_temperature,
            "max_tokens": settings.chat_max_tokens,
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            
            if response.status_code != 200:
                raise Exception(f"API error: {response.status_code} - {response.text}")
            
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    async def _call_gemini(self, messages: list[dict]) -> str:
        """Call Google Gemini API."""
        import google.generativeai as genai
        
        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(self.model)
        
        prompt = "\n\n".join([f"{m['role']}: {m['content']}" for m in messages])
        
        response = await model.generate_content_async(prompt)
        return response.text
    
    def _parse_response(self, response_text: str) -> dict:
        """Parse LLM response with high robustness."""
        result = {
            "primary_tag": None,
            "primary_confidence": 0.0,
            "secondary_tag": None,
            "secondary_confidence": None,
            "interpreted_query": "",
            "response": "",
            "suggestions": [],
            "related_topics": [],
        }
        
        if not response_text:
            return result
        
        text = response_text.strip()
        
        # 1. Try to find JSON block using regex
        import re
        json_match = re.search(r'(\{.*\})', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            
            # 2. Pre-parse cleanup
            # Handle potential raw newlines inside JSON strings which break standard json.loads
            # This replaces actual newlines (0x0A) with the escaped \n sequence if they are inside double quotes
            # But the most common issue is just literal unescaped newlines.
            
            # Try parsing the extracted block
            try:
                parsed = json.loads(json_str)
                return self._validate_result(parsed)
            except json.JSONDecodeError:
                # 3. Last ditch attempt: sanitization for common LLM JSON errors
                try:
                    # Fix unescaped newlines in strings
                    sanitized = re.sub(r'":\s*"([^"]*)"', lambda m: '": "' + m.group(1).replace('\n', '\\n') + '"', json_str)
                    # Fix trailing commas
                    sanitized = re.sub(r',\s*([\]}])', r'\1', sanitized)
                    
                    parsed = json.loads(sanitized)
                    return self._validate_result(parsed)
                except:
                    pass
        
        # Fallback: If all parsing fails, put the raw text in the response field
        result["response"] = response_text
        return result
    
    def _validate_result(self, data: dict) -> dict:
        """Validate and sanitize parsed result with support for new fields."""
        
        # Primary tag and confidence
        primary_tag = data.get("primary_tag") or data.get("tag")
        if primary_tag and not isinstance(primary_tag, str):
            primary_tag = str(primary_tag)
            
        primary_confidence = data.get("primary_confidence", 0.0)
        # Handle cases where confidence might be 0-1 vs 0-100
        if isinstance(primary_confidence, (int, float)):
            if primary_confidence > 1.0:
                primary_confidence = primary_confidence / 100.0
        else:
            primary_confidence = 0.0
            
        # Secondary tag and confidence
        secondary_tag = data.get("secondary_tag")
        if secondary_tag and not isinstance(secondary_tag, str):
            secondary_tag = str(secondary_tag)
            
        secondary_confidence = data.get("secondary_confidence")
        if isinstance(secondary_confidence, (int, float)):
            if secondary_confidence > 1.0:
                secondary_confidence = secondary_confidence / 100.0
        else:
            secondary_confidence = None
        
        # Interpreted query
        interpreted_query = data.get("interpreted_query", "")
        if not isinstance(interpreted_query, str):
            interpreted_query = str(interpreted_query)
            
        # Response
        response = data.get("response", "")
        if not isinstance(response, str):
            response = str(response)
            
        # Suggestions and Topics
        suggestions = data.get("suggestions", [])
        if not isinstance(suggestions, list):
            suggestions = [str(suggestions)] if suggestions else []
        else:
            suggestions = [str(s) for s in suggestions if s]
            
        related_topics = data.get("related_topics", [])
        if not isinstance(related_topics, list):
            related_topics = [str(related_topics)] if related_topics else []
        else:
            related_topics = [str(t) for t in related_topics if t]
        
        return {
            "primary_tag": primary_tag,
            "primary_confidence": primary_confidence,
            "secondary_tag": secondary_tag,
            "secondary_confidence": secondary_confidence,
            "interpreted_query": interpreted_query,
            "response": response,
            "suggestions": suggestions,
            "related_topics": related_topics,
        }


# Singleton instance
_chat_service: Optional[ChatService] = None


def get_chat_service() -> ChatService:
    """Get or create ChatService instance."""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service