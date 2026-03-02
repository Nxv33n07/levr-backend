"""
Tagger Service - handles LLM API calls for query tagging.
"""

import json
import re
import time
from typing import Optional

import httpx

from app.config import settings
from app.tagger.prompts import build_messages, is_valid_tag


class TaggerService:
    """Service for tagging financial queries using LLM."""
    
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
                "base_url": None,  # Gemini uses different API
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
    
    async def tag(self, query: str, context: Optional[dict] = None, include_reasoning: bool = False) -> dict:
        """
        Tag a financial query.
        
        Returns:
            dict with: tag, confidence, reasoning, processing_time_ms
        """
        if not self.is_configured:
            raise ValueError(f"{self.provider} API key not configured")
        
        start_time = time.perf_counter()
        
        messages = build_messages(query, context)
        
        if self.provider == "gemini":
            result = await self._call_gemini(messages)
        else:
            result = await self._call_openai_compatible(messages)
        
        processing_time = int((time.perf_counter() - start_time) * 1000)
        
        # Parse result
        parsed = self._parse_response(result)
        parsed["processing_time_ms"] = processing_time
        
        if not include_reasoning:
            parsed["reasoning"] = None
        
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
            "max_tokens": settings.llm_max_tokens,
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
        
        # Convert messages to Gemini format
        prompt = "\n\n".join([f"{m['role']}: {m['content']}" for m in messages])
        
        response = await model.generate_content_async(prompt)
        return response.text
    
    def _parse_response(self, response_text: str) -> dict:
        """Parse LLM response to extract tag, confidence, reasoning."""
        result = {"tag": None, "confidence": 0.0, "reasoning": None}
        
        if not response_text:
            return result
        
        # Try direct JSON parse
        try:
            parsed = json.loads(response_text.strip())
            if isinstance(parsed, dict):
                return self._validate_result(parsed)
        except json.JSONDecodeError:
            pass
        
        # Try extracting JSON from response
        json_match = re.search(r'\{[^{}]*"tag"[^{}]*\}', response_text, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group())
                return self._validate_result(parsed)
            except json.JSONDecodeError:
                pass
        
        return result
    
    def _validate_result(self, data: dict) -> dict:
        """Validate and sanitize parsed result."""
        tag = data.get("tag")
        
        # Validate tag
        if tag and isinstance(tag, str):
            tag = tag.lower().strip()
            if not is_valid_tag(tag):
                tag = None
        else:
            tag = None
        
        # Validate confidence
        confidence = data.get("confidence", 0.0)
        try:
            confidence = max(0.0, min(1.0, float(confidence)))
        except (TypeError, ValueError):
            confidence = 0.0
        
        return {
            "tag": tag,
            "confidence": confidence,
            "reasoning": data.get("reasoning"),
        }
    
    async def health_check(self) -> bool:
        """Check if LLM service is accessible."""
        if not self.is_configured:
            return False
        
        try:
            result = await self.tag("test query")
            return result["tag"] is not None or result["confidence"] >= 0
        except Exception:
            return False


# Singleton instance
_tagger_service: Optional[TaggerService] = None


def get_tagger() -> TaggerService:
    """Get or create TaggerService instance."""
    global _tagger_service
    if _tagger_service is None:
        _tagger_service = TaggerService()
    return _tagger_service