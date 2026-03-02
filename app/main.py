"""
Query Tagger Service - Entry Point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models import TagRequest, TagResponse, ChatRequest, ChatResponse
from app.routes import tag_query, chat_response
from typing import Optional

app = FastAPI(
    title=settings.app_name,
    description="Financial query classification service",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/tag", response_model=TagResponse)
async def tag(request: TagRequest) -> TagResponse:
    """Tag a financial query with a category."""
    return await tag_query(request)


@app.get("/tag", response_model=TagResponse)
async def tag_get(
    query: str,
    context: Optional[str] = None,
    include_reasoning: bool = False
) -> TagResponse:
    """Tag a financial query (GET convenience method)."""
    request = TagRequest(
        query=query,
        context={"note": context} if context else None,
        include_reasoning=include_reasoning
    )
    return await tag_query(request)


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Generate a chat response for a financial query."""
    return await chat_response(request)


@app.get("/chat", response_model=ChatResponse)
async def chat_get(
    query: str,
    tag: Optional[str] = None,
    context: Optional[str] = None
) -> ChatResponse:
    """Generate a chat response (GET convenience method)."""
    request = ChatRequest(
        query=query,
        tag=tag,
        context={"note": context} if context else None
    )
    return await chat_response(request)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=True)