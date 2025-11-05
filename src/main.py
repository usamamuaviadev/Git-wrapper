#!/usr/bin/env python3
"""
GPT Wrapper - Main Entry Point

This is the entry point for the GPT wrapper system that routes prompts
to either OpenAI API or local Ollama models based on configuration.
"""

import sys
from routers.router_manager import route_prompt
from utils.logger import setup_logger

logger = setup_logger(__name__)


def main():
    """Main function to run the GPT wrapper."""
    logger.info("Starting GPT Wrapper...")
    
    # Example prompt - can be replaced with CLI input, API endpoint, etc.
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = input("Enter your prompt: ")
    
    if not prompt.strip():
        logger.warning("Empty prompt provided. Exiting.")
        return
    
    try:
        logger.info(f"Processing prompt: {prompt[:50]}...")
        response = route_prompt(prompt)
        
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


if __name__ == "__main__":
    main()

