"""
Voice Handler

Handles speech-to-text (STT) and text-to-speech (TTS) functionality.
Supports OpenAI Whisper API and OpenAI TTS, with fallbacks.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any, BinaryIO
import tempfile


class VoiceHandler:
    """
    Handles voice input/output operations.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the voice handler.
        
        Args:
            config: Configuration dictionary for voice settings
        """
        self.config = config
        self.enabled = config.get("enabled", False)
        self.provider = config.get("provider", "openai")
        self.api_key = config.get("api_key") or os.getenv("OPENAI_API_KEY")
        
        # Provider-specific settings
        self.tts_model = config.get("tts_model", "tts-1")
        self.tts_voice = config.get("tts_voice", "alloy")  # alloy, echo, fable, onyx, nova, shimmer
        self.stt_model = config.get("stt_model", "whisper-1")
        
        self.output_dir = Path(config.get("output_dir", "data/voice_output"))
        if self.enabled:
            self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def text_to_speech(self, text: str, output_path: Optional[str] = None) -> Optional[str]:
        """
        Convert text to speech and save as audio file.
        
        Args:
            text: Text to convert to speech
            output_path: Optional path to save audio file. If None, creates temp file.
            
        Returns:
            Path to saved audio file, or None if failed
        """
        if not self.enabled:
            print("[WARNING] Voice is not enabled in configuration")
            return None
        
        if not self.api_key:
            print("[WARNING] OpenAI API key not found for TTS")
            return None
        
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.api_key)
            
            # Determine output path
            if not output_path:
                output_file = tempfile.NamedTemporaryFile(
                    suffix=".mp3",
                    dir=self.output_dir,
                    delete=False
                )
                output_path = output_file.name
                output_file.close()
            
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate speech
            response = client.audio.speech.create(
                model=self.tts_model,
                voice=self.tts_voice,
                input=text
            )
            
            # Save to file
            with open(output_path, "wb") as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)
            
            print(f"[INFO] Generated speech: {output_path}")
            return str(output_path)
            
        except ImportError:
            print("[WARNING] OpenAI SDK not available. Install with: pip install openai")
            return None
        except Exception as e:
            print(f"[WARNING] Text-to-speech failed: {e}")
            return None
    
    def speech_to_text(self, audio_path: str, language: Optional[str] = None) -> Optional[str]:
        """
        Convert speech to text using Whisper API.
        
        Args:
            audio_path: Path to audio file
            language: Optional language code (e.g., "en", "es", "fr")
            
        Returns:
            Transcribed text, or None if failed
        """
        if not self.enabled:
            print("[WARNING] Voice is not enabled in configuration")
            return None
        
        if not self.api_key:
            print("[WARNING] OpenAI API key not found for STT")
            return None
        
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.api_key)
            
            audio_path = Path(audio_path)
            if not audio_path.exists():
                print(f"[ERROR] Audio file not found: {audio_path}")
                return None
            
            # Transcribe audio
            with open(audio_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model=self.stt_model,
                    file=audio_file,
                    language=language
                )
            
            text = transcript.text
            print(f"[INFO] Transcribed text: {text[:50]}...")
            return text
            
        except ImportError:
            print("[WARNING] OpenAI SDK not available. Install with: pip install openai")
            return None
        except Exception as e:
            print(f"[WARNING] Speech-to-text failed: {e}")
            return None
    
    def play_audio(self, audio_path: str) -> bool:
        """
        Play audio file using system default player.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import platform
            import subprocess
            
            audio_path = Path(audio_path)
            if not audio_path.exists():
                print(f"[ERROR] Audio file not found: {audio_path}")
                return False
            
            system = platform.system()
            
            if system == "Darwin":  # macOS
                subprocess.run(["afplay", str(audio_path)], check=True)
            elif system == "Linux":
                subprocess.run(["aplay", str(audio_path)], check=True)
            elif system == "Windows":
                subprocess.run(["start", str(audio_path)], shell=True, check=True)
            else:
                print(f"[WARNING] Unsupported platform for audio playback: {system}")
                return False
            
            return True
            
        except Exception as e:
            print(f"[WARNING] Failed to play audio: {e}")
            return False

