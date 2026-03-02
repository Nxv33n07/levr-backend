"""
API routes for the Query Tagger service.
"""

from fastapi import HTTPException

from app.models import TagRequest, TagResponse, TagResult, ChatRequest, ChatResponse, ChatResult
from app.tagger.service import get_tagger
from app.chat.service import get_chat_service


async def tag_query(request: TagRequest) -> TagResponse:
    """Tag a financial query with a category."""
    tagger = get_tagger()
    
    if not tagger.is_configured:
        raise HTTPException(503, f"{tagger.provider} API key not configured")
    
    try:
        result = await tagger.tag(
            query=request.query,
            context=request.context,
            include_reasoning=request.include_reasoning
        )
        
        return TagResponse(
            success=True,
            data=TagResult(
                tag=result["tag"],
                confidence=result["confidence"],
                reasoning=result["reasoning"]
            ),
            metadata={
                "provider": tagger.provider,
                "model": tagger.get_model_name(),
                "processing_time_ms": result["processing_time_ms"]
            }
        )
    
    except Exception as e:
        return TagResponse(
            success=False,
            error=str(e),
            metadata={"provider": tagger.provider}
        )


async def chat_response(request: ChatRequest) -> ChatResponse:
    """Generate a chat response for a financial query."""
    chat_service = get_chat_service()
    
    if not chat_service.is_configured:
        raise HTTPException(503, f"{chat_service.provider} API key not configured")
    
    try:
        result = await chat_service.generate(query=request.query)
        
        return ChatResponse(
            success=True,
            data=ChatResult(
                primary_tag=result["primary_tag"],
                primary_confidence=result["primary_confidence"],
                secondary_tag=result["secondary_tag"],
                secondary_confidence=result["secondary_confidence"],
                interpreted_query=result["interpreted_query"],
                response=result["response"],
                suggestions=result["suggestions"],
                related_topics=result["related_topics"]
            ),
            metadata={
                "provider": chat_service.provider,
                "model": chat_service.get_model_name(),
                "processing_time_ms": result["processing_time_ms"]
            }
        )
    
    except Exception as e:
        return ChatResponse(
            success=False,
            error=str(e),
            metadata={"provider": chat_service.provider}
        )
