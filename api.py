import os
import re
import logging
from contextlib import asynccontextmanager
from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import uvicorn
from dotenv import load_dotenv
from tool import get_guide_response, get_chat_response
from db import init_db, add_favorite, get_favorites, clear_favorites

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)

class CityRequest(BaseModel):
    city: str = Field(..., min_length=1, max_length=100, description="City name to get travel guide for")

class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$", description="Message role")
    content: str = Field(..., min_length=1, description="Message content")

class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., min_items=1, description="Chat history")
    city_context: Optional[str] = Field(None, description="Current city context")

class SaveFavoriteRequest(BaseModel):
    city: str = Field(..., min_length=1, max_length=100, description="City name")
    place_name: str = Field(..., min_length=1, max_length=200, description="Place to save as favorite")

class GuideResponse(BaseModel):
    guide_content: str
    timestamp: datetime = Field(default_factory=datetime.now)

class ChatResponse(BaseModel):
    response: str
    timestamp: datetime = Field(default_factory=datetime.now)

class FavoriteResponse(BaseModel):
    message: str
    success: bool
    timestamp: datetime = Field(default_factory=datetime.now)

class FavoritesListResponse(BaseModel):
    favorites: List[dict]
    count: int
    timestamp: datetime = Field(default_factory=datetime.now)

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = "1.0.0"

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Personalized AI Guide API")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    yield
    logger.info("Shutting down Personalized AI Guide API")

app = FastAPI(
    title="Personalized AI Travel Guide API",
    description="A production-ready API for AI-powered travel guidance with personalized recommendations",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    if not credentials:
        if os.getenv("REQUIRE_AUTH", "false").lower() == "true":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required"
            )
        return os.getenv("DEFAULT_GEMINI_API_KEY", "")
    
    api_key = credentials.credentials
    if not api_key or len(api_key) < 10:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key format"
        )
    
    return api_key

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy")

@app.get("/", response_model=dict)
async def root():
    return {
        "message": "Personalized AI Travel Guide API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.post("/guide", response_model=GuideResponse)
async def get_travel_guide(
    request: CityRequest,
    api_key: str = Depends(get_api_key)
):
    try:
        logger.info(f"Generating guide for city: {request.city}")
        
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gemini API key is required"
            )
        
        guide_content = get_guide_response(api_key, request.city)
        
        logger.info(f"Successfully generated guide for {request.city}")
        return GuideResponse(guide_content=guide_content)
        
    except Exception as e:
        logger.error(f"Error generating guide for {request.city}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate travel guide: {str(e)}"
        )

@app.post("/chat", response_model=ChatResponse)
async def chat_with_guide(
    request: ChatRequest,
    api_key: str = Depends(get_api_key)
):
    try:
        logger.info("Processing chat request")
        
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gemini API key is required"
            )
        
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        last_user_message = next(
            (msg["content"] for msg in reversed(messages) if msg["role"] == "user"),
            ""
        )
        
        save_match = re.search(r"save\s+(.+)", last_user_message, re.IGNORECASE)
        
        if save_match and request.city_context:
            place_to_save = save_match.group(1).strip()
            response_text = add_favorite(request.city_context, place_to_save)
        else:
            response_text = get_chat_response(api_key, messages)
        
        logger.info("Chat request processed successfully")
        return ChatResponse(response=response_text)
        
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat request: {str(e)}"
        )

@app.post("/favorites", response_model=FavoriteResponse)
async def save_favorite_place(request: SaveFavoriteRequest):
    try:
        logger.info(f"Saving favorite: {request.place_name} in {request.city}")
        
        result_message = add_favorite(request.city, request.place_name)
        success = "✅" in result_message
        
        logger.info(f"Favorite save result: {success}")
        return FavoriteResponse(
            message=result_message,
            success=success
        )
        
    except Exception as e:
        logger.error(f"Error saving favorite: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save favorite: {str(e)}"
        )

@app.get("/favorites", response_model=FavoritesListResponse)
async def get_favorite_places():
    try:
        logger.info("Retrieving favorites list")
        
        favorites_df = get_favorites()
        favorites_list = favorites_df.to_dict('records') if not favorites_df.empty else []
        
        logger.info(f"Retrieved {len(favorites_list)} favorites")
        return FavoritesListResponse(
            favorites=favorites_list,
            count=len(favorites_list)
        )
        
    except Exception as e:
        logger.error(f"Error retrieving favorites: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve favorites: {str(e)}"
        )

@app.delete("/favorites", response_model=FavoriteResponse)
async def clear_favorite_places():
    try:
        logger.info("Clearing favorites list")
        clear_favorites()
        logger.info("Favorites cleared successfully")
        return FavoriteResponse(
            message="✅ All favorites have been cleared successfully!",
            success=True
        )
        
    except Exception as e:
        logger.error(f"Error clearing favorites: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear favorites: {str(e)}"
        )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception handler caught: {str(exc)}")
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred"
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        reload=os.getenv("ENVIRONMENT") != "production"
    )