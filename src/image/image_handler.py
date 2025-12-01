"""
Image Handler

Handles image generation using DALL-E and other providers.
Supports image generation, storage, and retrieval.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import json


class ImageHandler:
    """
    Handles image generation and processing operations.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the image handler.
        
        Args:
            config: Configuration dictionary for image settings
        """
        self.config = config
        self.enabled = config.get("enabled", False)
        self.provider = config.get("provider", "dalle")
        self.api_key = config.get("api_key") or os.getenv("OPENAI_API_KEY")
        
        # Provider-specific settings
        self.model = config.get("model", "dall-e-3")
        self.size = config.get("size", "1024x1024")  # 256x256, 512x512, 1024x1024
        self.quality = config.get("quality", "standard")  # standard, hd
        self.n = config.get("n", 1)  # Number of images
        
        self.output_dir = Path(config.get("output_dir", "data/images"))
        self.metadata_file = self.output_dir / "metadata.json"
        
        if self.enabled:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self._load_metadata()
    
    def _load_metadata(self):
        """Load image metadata from file."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, "r") as f:
                    self.metadata = json.load(f)
            except:
                self.metadata = {}
        else:
            self.metadata = {}
    
    def _save_metadata(self):
        """Save image metadata to file."""
        try:
            with open(self.metadata_file, "w") as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            print(f"[WARNING] Failed to save metadata: {e}")
    
    def generate_image(
        self,
        prompt: str,
        size: Optional[str] = None,
        quality: Optional[str] = None,
        n: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Generate image(s) from text prompt.
        
        Args:
            prompt: Text description of the image
            size: Optional image size override
            quality: Optional quality override
            n: Number of images to generate
            
        Returns:
            List of dictionaries with image info: [{"url": "...", "path": "...", "revised_prompt": "..."}]
        """
        if not self.enabled:
            print("[WARNING] Image generation is not enabled in configuration")
            return []
        
        if not self.api_key:
            print("[WARNING] OpenAI API key not found for image generation")
            return []
        
        size = size or self.size
        quality = quality or self.quality
        
        try:
            from openai import OpenAI
            import requests
            
            client = OpenAI(api_key=self.api_key)
            
            # Generate image
            if self.model.startswith("dall-e-3"):
                # DALL-E 3 only supports n=1
                response = client.images.generate(
                    model=self.model,
                    prompt=prompt,
                    size=size,
                    quality=quality,
                    n=1
                )
                
                images = []
                for img in response.data:
                    image_url = img.url
                    revised_prompt = getattr(img, "revised_prompt", prompt)
                    
                    # Download and save image
                    saved_path = self._download_image(image_url, prompt)
                    
                    images.append({
                        "url": image_url,
                        "path": saved_path,
                        "revised_prompt": revised_prompt
                    })
                
                return images
                
            else:
                # DALL-E 2 supports multiple images
                response = client.images.generate(
                    model=self.model,
                    prompt=prompt,
                    size=size,
                    n=min(n, 10)  # Max 10 images
                )
                
                images = []
                for idx, img in enumerate(response.data):
                    image_url = img.url
                    saved_path = self._download_image(image_url, prompt, idx)
                    
                    images.append({
                        "url": image_url,
                        "path": saved_path,
                        "revised_prompt": prompt
                    })
                
                return images
                
        except ImportError:
            print("[WARNING] OpenAI SDK not available. Install with: pip install openai")
            return []
        except Exception as e:
            print(f"[WARNING] Image generation failed: {e}")
            return []
    
    def _download_image(self, url: str, prompt: str, index: int = 0) -> Optional[str]:
        """
        Download image from URL and save locally.
        
        Args:
            url: Image URL
            prompt: Original prompt (for filename)
            index: Image index if multiple
            
        Returns:
            Path to saved image, or None if failed
        """
        try:
            import requests
            
            # Create filename from prompt
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_prompt = "".join(c for c in prompt[:50] if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_prompt = safe_prompt.replace(' ', '_')
            filename = f"{timestamp}_{safe_prompt}_{index}.png"
            if len(filename) > 200:
                filename = f"{timestamp}_{index}.png"
            
            filepath = self.output_dir / filename
            
            # Download image
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Save to file
            with open(filepath, "wb") as f:
                f.write(response.content)
            
            # Save metadata
            image_id = str(filepath.stem)
            self.metadata[image_id] = {
                "prompt": prompt,
                "url": url,
                "path": str(filepath),
                "timestamp": datetime.now().isoformat(),
                "model": self.model,
                "size": self.size
            }
            self._save_metadata()
            
            print(f"[INFO] Saved image: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"[WARNING] Failed to download image: {e}")
            return None
    
    def list_images(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List recently generated images.
        
        Args:
            limit: Maximum number of images to return
            
        Returns:
            List of image metadata dictionaries
        """
        if not self.metadata:
            return []
        
        # Sort by timestamp (newest first)
        sorted_images = sorted(
            self.metadata.items(),
            key=lambda x: x[1].get("timestamp", ""),
            reverse=True
        )
        
        return [img_data for _, img_data in sorted_images[:limit]]
    
    def get_image(self, image_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific image.
        
        Args:
            image_id: Image ID (filename without extension)
            
        Returns:
            Image metadata dictionary, or None if not found
        """
        return self.metadata.get(image_id)

