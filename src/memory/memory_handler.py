"""
Memory Handler

Handles session-based conversation memory storage and retrieval.
Supports both session-based (JSONL) and vector-based (embedding) memory modes.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


class MemoryHandler:
    """
    Handles session-based and vector-based memory storage and retrieval.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the memory handler.
        
        Args:
            config: Configuration dictionary for memory settings
        """
        self.config = config
        self.enabled = config.get("enabled", False)
        self.mode = config.get("mode", "session")  # session or vector
        self.storage_path = config.get("storage_path", "data/sessions")
        self.max_history = config.get("max_history", 10)
        self.vector_store = config.get("vector_store", "chroma")
        
        self.vector_db = None
        self.embeddings_model = None
        
        if self.enabled:
            self.ensure_dir_exists()
            if self.mode == "vector":
                self._initialize_vector_store()
    
    def _initialize_vector_store(self):
        """Initialize vector database and embedding model for semantic search."""
        try:
            if self.vector_store == "chroma":
                import chromadb
                from chromadb.config import Settings
                
                # Initialize ChromaDB
                chroma_path = Path(self.storage_path) / "chroma_db"
                chroma_path.mkdir(parents=True, exist_ok=True)
                
                self.vector_client = chromadb.PersistentClient(
                    path=str(chroma_path),
                    settings=Settings(anonymized_telemetry=False)
                )
                
                # Get or create collection
                self.collection = self.vector_client.get_or_create_collection(
                    name="conversations",
                    metadata={"hnsw:space": "cosine"}
                )
                
                # Initialize embeddings model
                try:
                    from sentence_transformers import SentenceTransformer
                    model_name = self.config.get("embedding_model", "all-MiniLM-L6-v2")
                    self.embeddings_model = SentenceTransformer(model_name)
                    print(f"[INFO] Loaded embedding model: {model_name}")
                except ImportError:
                    print("[WARNING] sentence-transformers not installed. Install with: pip install sentence-transformers")
                    print("[INFO] Falling back to session mode")
                    self.mode = "session"
                    
        except ImportError:
            print("[WARNING] chromadb not installed. Install with: pip install chromadb")
            print("[INFO] Falling back to session mode")
            self.mode = "session"
        except Exception as e:
            print(f"[WARNING] Failed to initialize vector store: {e}")
            print("[INFO] Falling back to session mode")
            self.mode = "session"
    
    def ensure_dir_exists(self) -> None:
        """
        Ensure the storage directory exists, create if it doesn't.
        """
        path = Path(self.storage_path)
        path.mkdir(parents=True, exist_ok=True)
    
    def save_interaction(
        self, 
        session_id: str,
        model: str,
        prompt: str,
        response: str
    ) -> None:
        """
        Save a single turn (prompt + response) to memory.
        
        Args:
            session_id: Unique identifier for the session
            model: Model used for the response
            prompt: User's input prompt
            response: Model's response
        """
        if not self.enabled:
            return
        
        if self.mode == "vector":
            self._save_to_vector_store(session_id, model, prompt, response)
        else:
            self._save_to_session_file(session_id, model, prompt, response)
    
    def _save_to_session_file(
        self,
        session_id: str,
        model: str,
        prompt: str,
        response: str
    ) -> None:
        """Save interaction to JSONL file."""
        self.ensure_dir_exists()
        session_file = Path(self.storage_path) / f"{session_id}.jsonl"
        
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "role": "user",
            "model": model,
            "prompt": prompt,
            "response": response
        }
        
        try:
            with open(session_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(interaction) + "\n")
        except Exception as e:
            print(f"[WARNING] Failed to save interaction to memory: {e}")
    
    def _save_to_vector_store(
        self,
        session_id: str,
        model: str,
        prompt: str,
        response: str
    ) -> None:
        """Save interaction to vector database with embeddings."""
        if not self.embeddings_model or not hasattr(self, 'collection'):
            # Fallback to session file
            self._save_to_session_file(session_id, model, prompt, response)
            return
        
        try:
            # Create combined text for embedding
            combined_text = f"User: {prompt}\nAssistant: {response}"
            
            # Generate embedding
            embedding = self.embeddings_model.encode(combined_text).tolist()
            
            # Create metadata
            metadata = {
                "session_id": session_id,
                "model": model,
                "prompt": prompt,
                "response": response,
                "timestamp": datetime.now().isoformat()
            }
            
            # Generate unique ID
            doc_id = f"{session_id}_{datetime.now().timestamp()}"
            
            # Add to collection
            self.collection.add(
                embeddings=[embedding],
                documents=[combined_text],
                metadatas=[metadata],
                ids=[doc_id]
            )
            
        except Exception as e:
            print(f"[WARNING] Failed to save to vector store: {e}")
            # Fallback to session file
            self._save_to_session_file(session_id, model, prompt, response)
    
    def load_context(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Load the last N turns from memory.
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            List of interaction dictionaries, most recent last
        """
        if not self.enabled:
            return []
        
        if self.mode == "vector":
            return self._load_from_vector_store(session_id)
        else:
            return self._load_from_session_file(session_id)
    
    def _load_from_session_file(self, session_id: str) -> List[Dict[str, Any]]:
        """Load context from JSONL file."""
        session_file = Path(self.storage_path) / f"{session_id}.jsonl"
        
        if not session_file.exists():
            return []
        
        interactions = []
        try:
            with open(session_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        interactions.append(json.loads(line))
            
            # Return last N interactions
            return interactions[-self.max_history:]
        except Exception as e:
            print(f"[WARNING] Failed to load context from memory: {e}")
            return []
    
    def _load_from_vector_store(self, session_id: str) -> List[Dict[str, Any]]:
        """Load context from vector store (session-based for now, semantic search later)."""
        if not hasattr(self, 'collection'):
            return []
        
        try:
            # Query for this session's interactions
            results = self.collection.get(
                where={"session_id": session_id},
                limit=self.max_history,
                include=["metadatas", "documents"]
            )
            
            # Convert to standard format
            interactions = []
            if results and results.get("metadatas"):
                for metadata in results["metadatas"]:
                    interactions.append({
                        "timestamp": metadata.get("timestamp", ""),
                        "role": "user",
                        "model": metadata.get("model", ""),
                        "prompt": metadata.get("prompt", ""),
                        "response": metadata.get("response", "")
                    })
            
            return interactions[-self.max_history:]
        except Exception as e:
            print(f"[WARNING] Failed to load from vector store: {e}")
            return []
    
    def retrieve_context(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context from memory based on semantic similarity.
        
        Args:
            query: The query to search for
            top_k: Number of results to return
            
        Returns:
            List of relevant memory items
        """
        if not self.enabled or self.mode != "vector":
            return []
        
        if not self.embeddings_model or not hasattr(self, 'collection'):
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embeddings_model.encode(query).tolist()
            
            # Search in vector store
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["metadatas", "documents", "distances"]
            )
            
            # Convert to standard format
            interactions = []
            if results and results.get("metadatas") and len(results["metadatas"]) > 0:
                metadatas = results["metadatas"][0]
                for metadata in metadatas:
                    interactions.append({
                        "timestamp": metadata.get("timestamp", ""),
                        "role": "user",
                        "model": metadata.get("model", ""),
                        "prompt": metadata.get("prompt", ""),
                        "response": metadata.get("response", ""),
                        "similarity": metadata.get("similarity", 0.0)
                    })
            
            return interactions
        except Exception as e:
            print(f"[WARNING] Semantic search failed: {e}")
            return []
    
    def format_context_for_prompt(self, context: List[Dict[str, Any]]) -> str:
        """
        Format loaded context into a string suitable for prepending to prompts.
        
        Args:
            context: List of interaction dictionaries
            
        Returns:
            Formatted context string
        """
        if not context:
            return ""
        
        formatted_parts = ["Previous conversation:"]
        for interaction in context:
            prompt = interaction.get("prompt", "")
            response = interaction.get("response", "")
            
            formatted_parts.append(f"User: {prompt}")
            formatted_parts.append(f"Assistant: {response}")
        
        formatted_parts.append("")  # Empty line before current prompt
        return "\n".join(formatted_parts)
    
    def clear_memory(self, session_id: Optional[str] = None) -> None:
        """
        Clear all stored memories for a session, or all sessions if session_id is None.
        
        Args:
            session_id: Optional session ID to clear. If None, clears all sessions.
        """
        if not self.enabled:
            return
        
        if self.mode == "vector" and hasattr(self, 'collection'):
            try:
                if session_id:
                    # Delete specific session
                    results = self.collection.get(
                        where={"session_id": session_id},
                        include=["ids"]
                    )
                    if results and results.get("ids"):
                        self.collection.delete(ids=results["ids"])
                        print(f"[INFO] Cleared vector memory for session: {session_id}")
                else:
                    # Clear all
                    self.collection.delete()
                    print("[INFO] Cleared all vector memories")
                return
            except Exception as e:
                print(f"[WARNING] Failed to clear vector memory: {e}")
        
        # Fallback to session file clearing
        if session_id:
            session_file = Path(self.storage_path) / f"{session_id}.jsonl"
            if session_file.exists():
                try:
                    session_file.unlink()
                    print(f"[INFO] Cleared memory for session: {session_id}")
                except Exception as e:
                    print(f"[WARNING] Failed to clear memory: {e}")
        else:
            # Clear all sessions
            session_dir = Path(self.storage_path)
            if session_dir.exists():
                for session_file in session_dir.glob("*.jsonl"):
                    try:
                        session_file.unlink()
                    except Exception as e:
                        print(f"[WARNING] Failed to delete {session_file}: {e}")
                print("[INFO] Cleared all session memories")
