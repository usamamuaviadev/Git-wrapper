"""
API Server

FastAPI-based REST API server for GPT Wrapper.
Provides endpoints for chat, memory, voice, and image generation.
"""

import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from routers.router_manager import route_prompt, load_config
from memory.memory_handler import MemoryHandler
from utils.logger import setup_logger

# Load environment variables
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

logger = setup_logger(__name__)


class APIServer:
    """
    FastAPI server for GPT Wrapper.
    """
    
    def __init__(self):
        """Initialize the API server."""
        try:
            from fastapi import FastAPI, HTTPException, UploadFile, File
            from fastapi.responses import JSONResponse, FileResponse
            from fastapi.middleware.cors import CORSMiddleware
            from fastapi.staticfiles import StaticFiles
            from pydantic import BaseModel
            
            self.app = FastAPI(
                title="GPT Wrapper API",
                description="REST API for GPT Wrapper - OpenAI and Ollama routing",
                version="1.0.0"
            )
            
            # CORS middleware
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
            
            # Load configuration
            try:
                self.config = load_config()
            except Exception as e:
                logger.error(f"Failed to load configuration: {e}")
                self.config = {}
            
            # Initialize handlers
            memory_config = self.config.get("memory", {})
            self.memory_handler = MemoryHandler(memory_config)
            
            # Store FastAPI classes for route definitions
            self.FastAPI = FastAPI
            self.HTTPException = HTTPException
            self.UploadFile = UploadFile
            self.File = File
            self.JSONResponse = JSONResponse
            self.FileResponse = FileResponse
            self.BaseModel = BaseModel
            
            self._setup_routes()
            
        except ImportError as e:
            logger.error(f"FastAPI not installed: {e}")
            logger.error("Install with: pip install fastapi uvicorn python-multipart")
            raise
    
    def _setup_routes(self):
        """Setup API routes."""
        BaseModel = self.BaseModel
        HTTPException = self.HTTPException
        
        # Request/Response models
        class ChatRequest(BaseModel):
            prompt: str
            session_id: Optional[str] = None
        
        class ChatResponse(BaseModel):
            response: str
            model: str
            session_id: Optional[str] = None
        
        class ImageRequest(BaseModel):
            prompt: str
            size: Optional[str] = "1024x1024"
            quality: Optional[str] = "standard"
            n: int = 1
        
        class ImageResponse(BaseModel):
            images: List[Dict[str, Any]]
            prompt: str
        
        # Routes
        @self.app.get("/")
        async def root():
            return {
                "message": "GPT Wrapper API",
                "version": "1.0.0",
                "endpoints": {
                    "chat": "/api/chat",
                    "health": "/api/health",
                    "sessions": "/api/sessions/{session_id}",
                    "image": "/api/image/generate",
                    "docs": "/docs"
                }
            }
        
        @self.app.get("/api/health")
        async def health():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "memory_enabled": self.memory_handler.enabled,
                "active_model": self.config.get("active_model", "unknown")
            }
        
        @self.app.post("/api/chat", response_model=ChatResponse)
        async def chat(request: ChatRequest):
            """Chat endpoint - process a prompt and return response."""
            try:
                # Load context if memory enabled
                context = None
                if self.memory_handler.enabled and request.session_id:
                    context_items = self.memory_handler.load_context(request.session_id)
                    if context_items:
                        context = self.memory_handler.format_context_for_prompt(context_items)
                
                # Route the prompt
                response, model_name = route_prompt(
                    request.prompt,
                    session_id=request.session_id,
                    context=context
                )
                
                # Save to memory if enabled
                if self.memory_handler.enabled and request.session_id:
                    self.memory_handler.save_interaction(
                        session_id=request.session_id,
                        model=model_name,
                        prompt=request.prompt,
                        response=response
                    )
                
                return ChatResponse(
                    response=response,
                    model=model_name,
                    session_id=request.session_id
                )
            except Exception as e:
                logger.error(f"Chat error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/sessions/{session_id}")
        async def get_session(session_id: str):
            """Get session history."""
            if not self.memory_handler.enabled:
                raise HTTPException(status_code=400, detail="Memory is not enabled")
            
            context_items = self.memory_handler.load_context(session_id)
            return {
                "session_id": session_id,
                "turns": context_items,
                "count": len(context_items)
            }
        
        @self.app.delete("/api/sessions/{session_id}")
        async def delete_session(session_id: str):
            """Delete a session."""
            if not self.memory_handler.enabled:
                raise HTTPException(status_code=400, detail="Memory is not enabled")
            
            self.memory_handler.clear_memory(session_id)
            return {"message": f"Session {session_id} cleared", "session_id": session_id}
        
        @self.app.post("/api/image/generate", response_model=ImageResponse)
        async def generate_image(request: ImageRequest):
            """Generate image from prompt."""
            try:
                from image.image_handler import ImageHandler
                
                image_config = self.config.get("image", {})
                image_handler = ImageHandler(image_config)
                
                if not image_handler.enabled:
                    raise HTTPException(status_code=400, detail="Image generation is not enabled")
                
                images = image_handler.generate_image(
                    prompt=request.prompt,
                    size=request.size,
                    quality=request.quality,
                    n=request.n
                )
                
                if not images:
                    raise HTTPException(status_code=500, detail="Image generation failed")
                
                return ImageResponse(images=images, prompt=request.prompt)
            except ImportError:
                raise HTTPException(status_code=500, detail="Image handler not available")
            except Exception as e:
                logger.error(f"Image generation error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Voice endpoints
        class TTSRequest(BaseModel):
            text: str
            voice: Optional[str] = None
        
        class TTSResponse(BaseModel):
            audio_path: str
            text: str
        
        class STTResponse(BaseModel):
            text: str
            language: Optional[str] = None
        
        @self.app.post("/api/voice/tts", response_model=TTSResponse)
        async def text_to_speech(request: TTSRequest):
            """Convert text to speech."""
            try:
                from voice.voice_handler import VoiceHandler
                
                voice_config = self.config.get("voice", {})
                voice_handler = VoiceHandler(voice_config)
                
                if not voice_handler.enabled:
                    raise HTTPException(status_code=400, detail="Voice is not enabled")
                
                # Override voice if provided
                if request.voice:
                    voice_handler.tts_voice = request.voice
                
                audio_path = voice_handler.text_to_speech(request.text)
                
                if not audio_path:
                    raise HTTPException(status_code=500, detail="Text-to-speech failed")
                
                return TTSResponse(audio_path=audio_path, text=request.text)
            except ImportError:
                raise HTTPException(status_code=500, detail="Voice handler not available")
            except Exception as e:
                logger.error(f"TTS error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/voice/stt", response_model=STTResponse)
        async def speech_to_text(file: UploadFile = File(...), language: Optional[str] = None):
            """Convert speech to text."""
            try:
                from voice.voice_handler import VoiceHandler
                import tempfile
                
                voice_config = self.config.get("voice", {})
                voice_handler = VoiceHandler(voice_config)
                
                if not voice_handler.enabled:
                    raise HTTPException(status_code=400, detail="Voice is not enabled")
                
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                    content = await file.read()
                    tmp_file.write(content)
                    tmp_path = tmp_file.name
                
                text = voice_handler.speech_to_text(tmp_path, language=language)
                
                # Clean up temp file
                try:
                    os.unlink(tmp_path)
                except:
                    pass
                
                if not text:
                    raise HTTPException(status_code=500, detail="Speech-to-text failed")
                
                return STTResponse(text=text, language=language)
            except ImportError:
                raise HTTPException(status_code=500, detail="Voice handler not available")
            except Exception as e:
                logger.error(f"STT error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Update root endpoint
        @self.app.get("/")
        async def root():
            return {
                "message": "GPT Wrapper API",
                "version": "1.0.0",
                "endpoints": {
                    "chat": "/api/chat",
                    "health": "/api/health",
                    "sessions": "/api/sessions/{session_id}",
                    "image": "/api/image/generate",
                    "voice_tts": "/api/voice/tts",
                    "voice_stt": "/api/voice/stt",
                    "docs": "/docs"
                }
            }
        
        logger.info("API routes configured")


def create_app():
    """Create and return FastAPI application."""
    server = APIServer()
    return server.app


def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the API server."""
    try:
        import uvicorn
        
        app = create_app()
        
        logger.info(f"Starting API server on http://{host}:{port}")
        logger.info(f"API docs available at http://{host}:{port}/docs")
        
        uvicorn.run(app, host=host, port=port)
    except ImportError:
        logger.error("uvicorn not installed. Install with: pip install uvicorn")
        raise


if __name__ == "__main__":
    run_server()

