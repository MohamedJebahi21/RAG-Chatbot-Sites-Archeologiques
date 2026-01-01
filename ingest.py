# ingest.py - Ingestion et indexation ChromaDB
# Mini-projet IA Générative - Sites Archéologiques de Tunisie

import re
import logging
from pathlib import Path
from datetime import datetime

import chromadb
from sentence_transformers import SentenceTransformer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class DocumentIngester:
    """Gère l'ingestion, le chunking et l'indexation des documents"""

    def __init__(
        self,
        corpus_path: str,
        chroma_db_path: str,
        embedding_model: str,
        chunk_size: int = 600,
        chunk_overlap: int = 150,
        collection_name: str = "tunisian_archaeology",
    ):
        self.corpus_path = Path(corpus_path)
        self.chroma_db_path = Path(chroma_db_path)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.collection_name = collection_name

        logger.info(f"📦 Chargement du modèle d'embedding: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)

        logger.info(f"💾 Initialisation de ChromaDB: {chroma_db_path}")
        self.chroma_client = chromadb.PersistentClient(path=str(chroma_db_path))

        # Recréer la collection proprement
        try:
            self.chroma_client.delete_collection(self.collection_name)
            logger.info("🗑️  Ancienne collection supprimée")
        except Exception:
            pass

        self.collection = self.chroma_client.create_collection(
            name=self.collection_name,
            metadata={"description": "Sites archéologiques tunisiens - Mini-projet RAG"},
        )
        logger.info("✅ Ingester initialisé")

    def load_documents(self) -> list:
        """Charge tous les documents .txt du corpus"""
        documents = []
        
        if not self.corpus_path.exists():
            logger.error(f"❌ Le chemin du corpus n'existe pas: {self.corpus_path}")
            return documents

        txt_files = list(self.corpus_path.glob("*.txt"))
        logger.info(f"📄 Trouvé {len(txt_files)} fichiers .txt")

        for file_path in txt_files:
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                metadata = self._extract_metadata(content, file_path)

                documents.append(
                    {
                        "content": content,
                        "metadata": metadata,
                        "filename": file_path.name,
                    }
                )
                logger.info(f"  ✓ {file_path.name} | Site: {metadata.get('site', 'N/A')}")
            except Exception as e:
                logger.error(f"  ✗ Erreur {file_path.name}: {e}")

        return documents

    def _extract_metadata(self, content: str, file_path: Path) -> dict:
        """
        Extrait métadonnées structurées: site, période, source
        Patterns multiples + fallbacks intelligents
        """
        metadata = {
            "filename": file_path.name,
            "site": None,
            "period": None,
            "source": None,
        }

        # 1) SITE
        site_patterns = [
            r"^\s*Site\s*[:\-]\s*(.+)$",
            r"^\s*Nom\s*[:\-]\s*(.+)$",
            r"^\s*Lieu\s*[:\-]\s*(.+)$",
        ]
        for pattern in site_patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
            if match:
                metadata["site"] = match.group(1).strip()
                break
        
        if not metadata["site"]:
            metadata["site"] = self._guess_site_from_filename(file_path.name)

        # 2) PÉRIODE
        period_patterns = [
            r"^\s*P[ée]riode\s*[:\-]\s*(.+)$",
            r"^\s*[ÉéE]poque\s*[:\-]\s*(.+)$",
            r"^\s*Datation\s*[:\-]\s*(.+)$",
        ]
        for pattern in period_patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
            if match:
                metadata["period"] = match.group(1).strip()
                break
        
        if not metadata["period"]:
            metadata["period"] = self._guess_period_from_content(content)

        # 3) SOURCE
        source_patterns = [
            r"^\s*Source\s*[:\-]\s*(.+)$",
            r"^\s*R[ée]f[ée]rence\s*[:\-]\s*(.+)$",
        ]
        for pattern in source_patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
            if match:
                metadata["source"] = match.group(1).strip()
                break
        
        if not metadata["source"]:
            # Chercher URL
            url_match = re.search(r"(https?://[^\s]+)", content)
            if url_match:
                metadata["source"] = url_match.group(1)
            else:
                metadata["source"] = self._guess_source_from_filename(file_path.name)

        return metadata

    def _guess_site_from_filename(self, filename: str) -> str:
        """Devine le site depuis le nom de fichier"""
        fname = filename.lower()
        
        sites_map = {
            "carthage": "Carthage",
            "dougga": "Dougga",
            "el_jem": "El Jem",
            "eljem": "El Jem",
            "el jem": "El Jem",
            "sbeitla": "Sbeitla",
            "sbeïtla": "Sbeïtla",
            "kerkouane": "Kerkouane",
            "kerk": "Kerkouane",
            "bulla": "Bulla Regia",
            "uthina": "Uthina",
            "maktar": "Maktar",
            "thuburbo": "Thuburbo Majus",
            "chemtou": "Chemtou",
        }

        for key, site_name in sites_map.items():
            if key in fname:
                return site_name
        return None

    def _guess_period_from_content(self, content: str) -> str:
        """Devine la période historique depuis le contenu"""
        content_lower = content.lower()

        if "romain" in content_lower or "rome" in content_lower:
            return "Époque romaine"
        if "punique" in content_lower or "carthaginois" in content_lower:
            return "Époque punique"
        if "byzantin" in content_lower:
            return "Époque byzantine"
        if "numide" in content_lower:
            return "Époque numide"
        
        return None

    def _guess_source_from_filename(self, filename: str) -> str:
        """Devine la source depuis le nom de fichier"""
        fname = filename.lower()

        if "wiki" in fname:
            return "Wikipédia"
        if "unesco" in fname:
            return "UNESCO"
        if "inp" in fname:
            return "Institut National du Patrimoine (INP)"
        
        return None

    def chunk_text(self, text: str, metadata: dict) -> list:
        """
        Découpe en chunks sémantiques (300-500 tokens ≈ 400-650 caractères)
        avec overlap pour préserver le contexte
        """
        chunks = []
        start = 0
        chunk_id = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))

            # Coupe naturelle (fin de phrase)
            if end < len(text):
                for punct in [". ", "! ", "? ", "\n\n", "\n"]:
                    punct_pos = text.rfind(punct, start, end)
                    if punct_pos != -1:
                        end = punct_pos + len(punct)
                        break

            chunk = text[start:end].strip()
            
            # Ignorer chunks trop courts (< 100 caractères)
            if len(chunk) >= 100:
                chunks.append(
                    {
                        "text": chunk,
                        "metadata": {
                            **metadata,
                            "chunk_id": chunk_id,
                            "start_char": start,
                            "end_char": end,
                        },
                    }
                )
                chunk_id += 1

            start += self.chunk_size - self.chunk_overlap
            if start >= end:
                start = end

        return chunks

    def index_documents(self, documents: list) -> None:
        """Indexe tous les documents dans ChromaDB"""
        logger.info(f"🚀 Début de l'indexation de {len(documents)} documents")

        all_chunks = []
        for doc in documents:
            chunks = self.chunk_text(doc["content"], doc["metadata"])
            all_chunks.extend(chunks)
            logger.info(f"  📝 {doc['filename']}: {len(chunks)} chunks")

        logger.info(f"📊 Total: {len(all_chunks)} chunks créés")
        
        if not all_chunks:
            logger.warning("⚠️  Aucun chunk à indexer")
            return

        texts = [c["text"] for c in all_chunks]
        metadatas = [c["metadata"] for c in all_chunks]

        logger.info("🔢 Génération des embeddings...")
        embeddings = self.embedding_model.encode(
            texts, 
            show_progress_bar=True, 
            batch_size=16,
            convert_to_numpy=True
        )

        # IDs uniques
        ts = int(datetime.now().timestamp())
        ids = [f"chunk_{ts}_{i}" for i in range(len(texts))]

        # Insertion par batch (plus stable)
        batch_size = 50
        total_batches = (len(ids) + batch_size - 1) // batch_size

        for i in range(0, len(ids), batch_size):
            batch_end = min(i + batch_size, len(ids))
            batch_num = i // batch_size + 1

            self.collection.add(
                embeddings=embeddings[i:batch_end].tolist(),
                documents=texts[i:batch_end],
                metadatas=metadatas[i:batch_end],
                ids=ids[i:batch_end],
            )
            logger.info(f"  ✓ Batch {batch_num}/{total_batches} indexé")

        final_count = self.collection.count()
        logger.info(f"✅ Indexation terminée: {final_count} chunks dans ChromaDB")


def main():
    """Point d'entrée pour l'ingestion"""
    print("=" * 70)
    print("🏛️  INGESTION - SITES ARCHÉOLOGIQUES DE TUNISIE")
    print("=" * 70)

    from config import Config

    has_files = Config.ensure_directories()
    if not has_files:
        print(f"\n❌ Aucun fichier .txt trouvé dans: {Config.CORPUS_PATH}")
        print("   Placez vos documents dans ce dossier et réessayez.")
        return

    print(f"\n🔧 Configuration:")
    print(f"   • Chunk size: {Config.CHUNK_SIZE} caractères")
    print(f"   • Overlap: {Config.CHUNK_OVERLAP} caractères")
    print(f"   • Modèle: {Config.EMBEDDING_MODEL}")

    ingester = DocumentIngester(
        corpus_path=str(Config.CORPUS_PATH),
        chroma_db_path=str(Config.CHROMA_DB_PATH),
        embedding_model=Config.EMBEDDING_MODEL,
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP,
    )

    documents = ingester.load_documents()
    if not documents:
        print("\n❌ Aucun document à indexer")
        return

    print(f"\n🚀 Indexation en cours...")
    ingester.index_documents(documents)
    print("\n✅ Indexation terminée avec succès!")
    print(f"   Utilisez: streamlit run app.py")


if __name__ == "__main__":
    main()
