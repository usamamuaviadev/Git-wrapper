"""
Web UI

Simple web interface for GPT Wrapper using Streamlit.
"""

import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from routers.router_manager import route_prompt, load_config
from memory.memory_handler import MemoryHandler
from voice.voice_handler import VoiceHandler
from image.image_handler import ImageHandler
from utils.logger import setup_logger

# Load environment variables
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

logger = setup_logger(__name__)


def create_web_ui():
    """Create and run Streamlit web UI."""
    try:
        import streamlit as st
    except ImportError:
        print("Streamlit not installed. Install with: pip install streamlit")
        print("Then run: streamlit run src/api/web_ui.py")
        return
    
    st.set_page_config(
        page_title="GPT Wrapper",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 GPT Wrapper")
    st.markdown("Multi-model AI chat interface with memory, voice, and image generation")
    
    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        st.error(f"Failed to load configuration: {e}")
        return
    
    # Initialize handlers
    memory_config = config.get("memory", {})
    memory_handler = MemoryHandler(memory_config)
    
    voice_config = config.get("voice", {})
    voice_handler = VoiceHandler(voice_config)
    
    image_config = config.get("image", {})
    image_handler = ImageHandler(image_config)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.write(f"**Active Model:** {config.get('active_model', 'unknown')}")
        st.write(f"**Memory:** {'Enabled' if memory_handler.enabled else 'Disabled'}")
        st.write(f"**Voice:** {'Enabled' if voice_handler.enabled else 'Disabled'}")
        st.write(f"**Image:** {'Enabled' if image_handler.enabled else 'Disabled'}")
        
        session_id = st.text_input(
            "Session ID",
            value="default",
            help="Session ID for memory tracking"
        )
        
        st.markdown("---")
        st.markdown("### 📚 Documentation")
        st.markdown("[README](../README.md)")
        st.markdown("[API Docs](/docs)")
    
    # Main chat interface
    st.header("💬 Chat")
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "model" in message:
                st.caption(f"Model: {message['model']}")
    
    # Chat input
    if prompt := st.chat_input("Enter your message..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Load context if memory enabled
                    context = None
                    if memory_handler.enabled and session_id:
                        context_items = memory_handler.load_context(session_id)
                        if context_items:
                            context = memory_handler.format_context_for_prompt(context_items)
                    
                    # Route the prompt
                    response, model_name = route_prompt(
                        prompt,
                        session_id=session_id,
                        context=context
                    )
                    
                    # Save to memory
                    if memory_handler.enabled and session_id:
                        memory_handler.save_interaction(
                            session_id=session_id,
                            model=model_name,
                            prompt=prompt,
                            response=response
                        )
                    
                    # Display response
                    st.markdown(response)
                    st.caption(f"Model: {model_name}")
                    
                    # Add to messages
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "model": model_name
                    })
                    
                    # Text-to-speech button
                    if voice_handler.enabled:
                        if st.button("🔊 Play Response", key=f"tts_{len(st.session_state.messages)}"):
                            audio_path = voice_handler.text_to_speech(response)
                            if audio_path:
                                st.audio(audio_path)
                                voice_handler.play_audio(audio_path)
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    logger.error(f"Chat error: {e}")
    
    # Image generation tab
    with st.expander("🎨 Generate Image"):
        image_prompt = st.text_input("Image prompt", placeholder="A beautiful sunset over mountains")
        image_size = st.selectbox("Size", ["256x256", "512x512", "1024x1024"], index=2)
        
        if st.button("Generate Image") and image_prompt:
            if not image_handler.enabled:
                st.warning("Image generation is not enabled in configuration")
            else:
                with st.spinner("Generating image..."):
                    try:
                        images = image_handler.generate_image(
                            prompt=image_prompt,
                            size=image_size
                        )
                        
                        if images:
                            for img in images:
                                if img.get("path"):
                                    st.image(img["path"], caption=img.get("revised_prompt", image_prompt))
                                    st.download_button(
                                        "Download",
                                        data=open(img["path"], "rb").read(),
                                        file_name=Path(img["path"]).name,
                                        mime="image/png"
                                    )
                        else:
                            st.error("Failed to generate image")
                    except Exception as e:
                        st.error(f"Image generation error: {str(e)}")
    
    # Session management
    with st.expander("📝 Session Management"):
        if memory_handler.enabled:
            context_items = memory_handler.load_context(session_id)
            st.write(f"**Session:** {session_id}")
            st.write(f"**Turns:** {len(context_items)}")
            
            if st.button("Clear Session"):
                memory_handler.clear_memory(session_id)
                st.session_state.messages = []
                st.success("Session cleared!")
                st.rerun()
        else:
            st.info("Memory is not enabled. Enable it in settings.yaml to use session management.")


if __name__ == "__main__":
    create_web_ui()

