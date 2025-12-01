#!/usr/bin/env python3
"""
GPT Wrapper - Main Entry Point

This is the entry point for the GPT wrapper system that routes prompts
to either OpenAI API or local Ollama models based on configuration.
Supports both single-shot and interactive chat modes with session memory.
"""

import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
from routers.router_manager import route_prompt, load_config
from memory.memory_handler import MemoryHandler
from utils.logger import setup_logger

# Load environment variables from .env file if it exists
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

logger = setup_logger(__name__)
if env_path.exists():
    logger.info(f"Loaded environment variables from {env_path}")


def process_prompt(prompt: str, session_id: str = None, memory_handler: MemoryHandler = None):
    """
    Process a single prompt and return the response.
    
    Args:
        prompt: The user's input prompt
        session_id: Optional session ID for memory tracking
        memory_handler: Optional memory handler instance
        
    Returns:
        Tuple of (response, model_name)
    """
    context = None
    
    # Load context from memory if enabled and session_id provided
    if memory_handler and memory_handler.enabled and session_id:
        context_items = memory_handler.load_context(session_id)
        if context_items:
            context = memory_handler.format_context_for_prompt(context_items)
            logger.info(f"Loaded {len(context_items)} previous turns from session {session_id}")
    
    # Route the prompt
    response, model_name = route_prompt(prompt, session_id=session_id, context=context)
    
    # Save to memory if enabled
    if memory_handler and memory_handler.enabled and session_id:
        memory_handler.save_interaction(
            session_id=session_id,
            model=model_name,
            prompt=prompt,
            response=response
        )
        logger.info(f"Saved interaction to session {session_id}")
    
    return response, model_name


def interactive_mode(session_id: str = None, memory_handler: MemoryHandler = None):
    """
    Run interactive chat mode with continuous user input.
    
    Args:
        session_id: Optional session ID for memory tracking
        memory_handler: Optional memory handler instance
    """
    print("\n" + "="*80)
    print("🔄 Interactive Chat Mode")
    if session_id:
        print(f"📝 Session ID: {session_id}")
    if memory_handler and memory_handler.enabled:
        print("💾 Memory: ENABLED")
    print("="*80)
    print("Type your messages (or /exit or /quit to end)\n")
    
    turn_count = 0
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Check for exit commands
            if user_input.lower() in ['/exit', '/quit']:
                print("\n👋 Goodbye!\n")
                break
            
            turn_count += 1
            logger.info(f"Turn {turn_count}: Processing user input")
            
            # Process the prompt
            try:
                response, model_name = process_prompt(
                    user_input, 
                    session_id=session_id,
                    memory_handler=memory_handler
                )
                
                # Print response
                print(f"\n{model_name}: {response}\n")
                
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted by user. Type /exit to quit.\n")
            except Exception as e:
                logger.error(f"Error processing prompt: {str(e)}")
                print(f"\n❌ Error: {str(e)}\n")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except EOFError:
            print("\n\n👋 Goodbye!\n")
            break


def single_shot_mode(prompt: str, session_id: str = None, memory_handler: MemoryHandler = None):
    """
    Process a single prompt and exit.
    
    Args:
        prompt: The user's input prompt
        session_id: Optional session ID for memory tracking
        memory_handler: Optional memory handler instance
    """
    if not prompt.strip():
        logger.warning("Empty prompt provided. Exiting.")
        return
    
    try:
        logger.info(f"Processing prompt: {prompt[:50]}...")
        response, model_name = process_prompt(
            prompt,
            session_id=session_id,
            memory_handler=memory_handler
        )
        
        print("\n" + "="*80)
        print("RESPONSE:")
        print("="*80)
        print(response)
        print("="*80 + "\n")
        
        logger.info("Prompt processed successfully")
        
    except Exception as e:
        logger.error(f"Error processing prompt: {str(e)}")
        print(f"\n❌ Error: {str(e)}\n")
        sys.exit(1)


def main():
    """Main function to run the GPT wrapper."""
    parser = argparse.ArgumentParser(
        description="GPT Wrapper - Route prompts to OpenAI or local Ollama models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single prompt
  python src/main.py "What is AI?"
  
  # Interactive mode
  python src/main.py --interactive
  
  # With session memory
  python src/main.py --session-id test --interactive
  python src/main.py --session-id test "What is machine learning?"
  
  # Generate image
  python src/main.py --image "A beautiful sunset over mountains"
  
  # Text to speech
  python src/main.py --tts "Hello, world!"
  
  # Speech to text (requires audio file)
  python src/main.py --stt audio.wav
        """
    )
    
    parser.add_argument(
        'prompt',
        nargs='*',
        help='The prompt to process (optional if using --interactive, --image, --tts, or --stt)'
    )
    
    parser.add_argument(
        '--session-id',
        type=str,
        help='Session ID for memory tracking (required when memory.enabled=true)'
    )
    
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Run in interactive chat mode'
    )
    
    parser.add_argument(
        '--image',
        type=str,
        metavar='PROMPT',
        help='Generate image from prompt'
    )
    
    parser.add_argument(
        '--tts',
        type=str,
        metavar='TEXT',
        help='Convert text to speech'
    )
    
    parser.add_argument(
        '--stt',
        type=str,
        metavar='AUDIO_FILE',
        help='Convert speech to text from audio file'
    )
    
    args = parser.parse_args()
    
    logger.info("Starting GPT Wrapper...")
    
    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        logger.error(f"Failed to load configuration: {str(e)}")
        print(f"\n❌ Configuration Error: {str(e)}\n")
        sys.exit(1)
    
    # Initialize memory handler
    memory_config = config.get("memory", {})
    memory_handler = MemoryHandler(memory_config)
    
    # Check if memory is enabled but no session_id provided
    if memory_handler.enabled and not args.session_id:
        logger.warning("Memory is enabled but no --session-id provided. Memory features disabled for this session.")
        print("⚠️  Warning: Memory is enabled in config but no --session-id provided.")
        print("   Memory features will be disabled for this session.\n")
    
    # Determine session_id (use provided or generate default)
    session_id = args.session_id if args.session_id else None
    
    # If memory is enabled, require session_id
    if memory_handler.enabled and not session_id:
        session_id = "default"
        logger.info(f"Using default session_id: {session_id}")
    
    # Handle special modes first
    if args.image:
        # Image generation mode
        try:
            from image.image_handler import ImageHandler
            
            image_config = config.get("image", {})
            image_handler = ImageHandler(image_config)
            
            if not image_handler.enabled:
                print("❌ Error: Image generation is not enabled in configuration")
                sys.exit(1)
            
            print(f"🎨 Generating image: {args.image}")
            images = image_handler.generate_image(prompt=args.image)
            
            if images:
                print("\n" + "="*80)
                print("GENERATED IMAGE(S):")
                print("="*80)
                for img in images:
                    print(f"📸 Saved: {img.get('path', 'N/A')}")
                    if img.get('revised_prompt'):
                        print(f"📝 Revised prompt: {img.get('revised_prompt')}")
                    print()
                print("="*80)
            else:
                print("❌ Image generation failed")
                sys.exit(1)
                
        except Exception as e:
            logger.error(f"Image generation error: {e}")
            print(f"❌ Error: {str(e)}")
            sys.exit(1)
    
    elif args.tts:
        # Text-to-speech mode
        try:
            from voice.voice_handler import VoiceHandler
            
            voice_config = config.get("voice", {})
            voice_handler = VoiceHandler(voice_config)
            
            if not voice_handler.enabled:
                print("❌ Error: Voice is not enabled in configuration")
                sys.exit(1)
            
            print(f"🔊 Converting text to speech...")
            audio_path = voice_handler.text_to_speech(args.tts)
            
            if audio_path:
                print(f"\n✅ Audio saved: {audio_path}")
                print("Playing audio...")
                voice_handler.play_audio(audio_path)
            else:
                print("❌ Text-to-speech failed")
                sys.exit(1)
                
        except Exception as e:
            logger.error(f"TTS error: {e}")
            print(f"❌ Error: {str(e)}")
            sys.exit(1)
    
    elif args.stt:
        # Speech-to-text mode
        try:
            from voice.voice_handler import VoiceHandler
            from pathlib import Path
            
            voice_config = config.get("voice", {})
            voice_handler = VoiceHandler(voice_config)
            
            if not voice_handler.enabled:
                print("❌ Error: Voice is not enabled in configuration")
                sys.exit(1)
            
            audio_path = Path(args.stt)
            if not audio_path.exists():
                print(f"❌ Error: Audio file not found: {audio_path}")
                sys.exit(1)
            
            print(f"🎤 Converting speech to text from {audio_path}...")
            text = voice_handler.speech_to_text(str(audio_path))
            
            if text:
                print("\n" + "="*80)
                print("TRANSCRIBED TEXT:")
                print("="*80)
                print(text)
                print("="*80 + "\n")
            else:
                print("❌ Speech-to-text failed")
                sys.exit(1)
                
        except Exception as e:
            logger.error(f"STT error: {e}")
            print(f"❌ Error: {str(e)}")
            sys.exit(1)
    
    elif args.interactive:
        # Interactive mode
        interactive_mode(session_id=session_id, memory_handler=memory_handler)
    
    else:
        # Regular chat mode
        # Get prompt from args or input
        if args.prompt:
            prompt = " ".join(args.prompt)
        else:
            prompt = input("Enter your prompt: ")
        
        single_shot_mode(
            prompt=prompt,
            session_id=session_id,
            memory_handler=memory_handler
        )


if __name__ == "__main__":
    main()
