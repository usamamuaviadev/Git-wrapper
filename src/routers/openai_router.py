"""
OpenAI Router

Routes text to OpenAI API and handles responses.
"""

import os
from typing import Dict, Any
from openai import OpenAI


def query_openai(prompt: str, config: Dict[str, Any]) -> str:
    """
    Send a prompt to OpenAI API and return the response.
    
    Args:
        prompt: The user's input prompt
        config: Configuration dictionary with OpenAI settings
        
    Returns:
        The model's response as a string
        
    Raises:
        ValueError: If API key is missing
        Exception: If API call fails
    """
    api_key = config.get("api_key") or os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError(
            "OpenAI API key not found. Please set it in settings.yaml "
            "or as OPENAI_API_KEY environment variable."
        )
    
    model = config.get("model", "gpt-4-turbo")
    temperature = config.get("temperature", 0.7)
    max_tokens = config.get("max_tokens", 1000)
    
    try:
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        if not response.choices or len(response.choices) == 0:
            raise Exception("OpenAI API returned empty response")
        
        content = response.choices[0].message.content
        if not content:
            raise Exception("OpenAI API returned empty content")
        
        return content.strip()
    
    except Exception as e:
        error_msg = str(e)
        if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
            raise ValueError(
                f"OpenAI API authentication failed: {error_msg}. "
                "Please check your API key."
            )
        elif "rate limit" in error_msg.lower():
            raise Exception(
                f"OpenAI API rate limit exceeded: {error_msg}. "
                "Please wait a moment and try again."
            )
        else:
            raise Exception(f"OpenAI API error: {error_msg}")

