# config.py - Configuration centralisée

import os
from pathlib import Path


class Config:
    """Configuration du projet RAG - Mini-projet IA Générative"""

    # Chemins
    BASE_DIR = Path(__file__).parent.absolute()
    CORPUS_PATH = BASE_DIR / "data" / "corpus_txt"
    CHROMA_DB_PATH = BASE_DIR / "chroma_db"
    LOGS_PATH = BASE_DIR / "logs"

    # Chunking (300-500 tokens ≈ 400-650 caractères en français)
    CHUNK_SIZE = 600          # caractères (≈ 400 tokens)
    CHUNK_OVERLAP = 150       # caractères (≈ 100 tokens)

    # Embeddings
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

    # RAG (top-k: 3-5 selon consigne)
    TOP_K = 5
    SIMILARITY_THRESHOLD = 0.35  # seuil cosine similarity

    # LLM (Ollama)
    LLAMA_MODEL = "llama3"
    LLAMA_TEMPERATURE = 0.3
    LLAMA_MAX_TOKENS = 512

    # UI
    PAGE_TITLE = "🏛️ Chatbot - Sites Archéologiques de Tunisie"
    PAGE_ICON = "🏛️"

    @classmethod
    def ensure_directories(cls) -> bool:
        """Crée les dossiers et vérifie la présence de fichiers"""
        os.makedirs(cls.CORPUS_PATH, exist_ok=True)
        os.makedirs(cls.CHROMA_DB_PATH, exist_ok=True)
        os.makedirs(cls.LOGS_PATH, exist_ok=True)
        
        txt_files = list(cls.CORPUS_PATH.glob("*.txt"))
        print(f"📁 Dossiers créés")
        print(f"   • Corpus: {cls.CORPUS_PATH}")
        print(f"   • ChromaDB: {cls.CHROMA_DB_PATH}")
        print(f"   • Fichiers .txt trouvés: {len(txt_files)}")
        
        return len(txt_files) > 0
