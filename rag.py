# rag.py - Système RAG complet
# Mini-projet IA Générative - Sites Archéologiques de Tunisie

import logging
import re

import chromadb
from sentence_transformers import SentenceTransformer
import ollama

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class RAGSystem:
    """
    Système RAG complet: 
    - Garde-fou domaine (greetings + off-topic)
    - Recherche vectorielle (top-k=3-5)
    - Génération augmentée par contexte
    - Sources structurées
    """

    def __init__(
        self,
        chroma_db_path: str,
        embedding_model: str,
        llama_model: str = "llama3",
        top_k: int = 5,
        similarity_threshold: float = 0.35,
        temperature: float = 0.3,
        max_tokens: int = 512,
        collection_name: str = "tunisian_archaeology",
    ):
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        self.llama_model = llama_model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.collection_name = collection_name

        logger.info(f"📦 Chargement du modèle: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)

        logger.info(f"💾 Connexion à ChromaDB: {chroma_db_path}")
        self.chroma_client = chromadb.PersistentClient(path=chroma_db_path)

        try:
            self.collection = self.chroma_client.get_collection(name=self.collection_name)
            count = self.collection.count()
            logger.info(f"✅ Collection trouvée: {count} documents")
        except Exception as e:
            logger.error("❌ Collection non trouvée. Exécutez: python ingest.py")
            logger.error(f"   Erreur: {e}")
            self.collection = None

        self._check_ollama()

    def _check_ollama(self) -> bool:
        """Vérifie que Ollama est accessible"""
        try:
            models = ollama.list()
            
            if isinstance(models, dict) and "models" in models:
                model_names = [m.get("name", "?") for m in models["models"]]
            elif isinstance(models, list):
                model_names = [m.get("name", "?") for m in models]
            else:
                model_names = ["Format inconnu"]

            logger.info(f"✅ Ollama connecté. Modèles: {model_names}")
            return True
        except Exception as e:
            logger.warning(f"⚠️  Ollama non accessible: {e}")
            logger.warning("   Démarrez-le avec: ollama serve")
            return False

    # ========== GARDE-FOU DOMAINE ==========

    def is_in_scope(self, question: str):
        """
        Retourne:
        - "greeting" → salutation
        - True → archéologie tunisienne
        - False → hors domaine
        """
        q = question.lower().strip()

        # Salutations
        greetings = [
            "hi", "hello", "salut", "bonjour", "bonsoir", 
            "hey", "coucou", "yo", "good morning", "good evening"
        ]
        if q in greetings or any(q.startswith(g + " ") or q.startswith(g + ",") for g in greetings):
            return "greeting"

        # Domaine archéologie tunisienne
        keywords = [
            "tunisie", "tunisien", "tunisienne",
            "site archéologique", "sites archéologiques",
            "archéologie", "patrimoine", "ruines", "antique",
            "romain", "punique", "numide", "byzantin",
            "amphithéâtre", "théâtre", "forum", "thermes", "temple",
            "mosaïque", "basilique", "capitole",
            # Sites principaux
            "carthage", "dougga", "el jem", "el djem",
            "sbeitla", "sbeïtla", "kerkouane",
            "bulla regia", "uthina", "maktar", "thuburbo",
            "chemtou", "oudhna",
        ]

        # Regex pour variantes "kerk*"
        if re.search(r"\bkerk\w*", q):
            return True

        return any(k in q for k in keywords)

    # ========== RETRIEVAL ==========

    def search(self, query: str) -> list:
        """Recherche vectorielle top-k dans ChromaDB"""
        if not self.collection:
            return []

        logger.info(f"🔍 Recherche: '{query}'")
        
        query_embedding = self.embedding_model.encode(query).tolist()

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=10,  # on récupère 10 puis on filtre sur seuil
            include=["documents", "metadatas", "distances"],
        )

        documents = []
        if results.get("distances") and results["distances"][0]:
            for i, distance in enumerate(results["distances"][0]):
                # Similarité cosinus approx: 1 - (distance / 2)
                similarity = 1 - (distance / 2.0)
                
                if similarity >= self.similarity_threshold:
                    documents.append(
                        {
                            "text": results["documents"][0][i],
                            "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                            "similarity": round(float(similarity), 3),
                            "distance": round(float(distance), 3),
                        }
                    )

        # Trier par similarité décroissante
        documents.sort(key=lambda x: x["similarity"], reverse=True)
        documents = documents[: self.top_k]

        logger.info(f"📄 {len(documents)} documents pertinents (seuil={self.similarity_threshold})")
        if documents:
            sims = [d["similarity"] for d in documents]
            sites = [d["metadata"].get("site", "N/A") for d in documents]
            logger.info(f"   Similarités: {sims}")
            logger.info(f"   Sites: {sites}")

        return documents

    # ========== PROMPT / GENERATION ==========

    def build_prompt(self, query: str, context_docs: list) -> str:
        """
        Construit le prompt enrichi selon format mini-projet:
        - Question
        - Contexte récupéré (avec métadonnées)
        - Instruction de sourcing
        """
        context_parts = []
        
        for i, doc in enumerate(context_docs):
            meta = doc.get("metadata", {})
            site = meta.get("site") or "Site inconnu"
            period = meta.get("period") or "Période inconnue"
            source = meta.get("source") or "Source inconnue"
            filename = meta.get("filename", "Document")
            sim = doc.get("similarity", "?")

            context_parts.append(f"[SOURCE {i+1}]")
            context_parts.append(f"Site: {site}")
            context_parts.append(f"Période: {period}")
            context_parts.append(f"Source: {source}")
            context_parts.append(f"Document: {filename}")
            context_parts.append(f"Pertinence: {sim}")
            context_parts.append("---")
            context_parts.append(doc.get("text", ""))
            context_parts.append("=" * 50)

        context = "\n".join(context_parts)

        return f"""Tu es un expert en archéologie tunisienne. Ta mission est de fournir des réponses factuelles, précises et bien sourcées.

DOCUMENTS DE RÉFÉRENCE:
{context}

QUESTION DE L'UTILISATEUR: {query}

INSTRUCTIONS STRICTES:
1. Réponds en français, de manière claire et structurée.
2. Utilise UNIQUEMENT les informations présentes dans les documents de référence.
3. N'invente rien. Si une information n'est pas dans les documents, dis-le explicitement.
4. À la fin de ta réponse, liste les sources utilisées sous ce format exact:

Sources:
- [Titre du document] (Site: [site], Période: [période], Source: [source])

RÉPONSE:"""

    def generate_response(self, prompt: str) -> str:
        """Génère une réponse avec Llama 3 via Ollama"""
        try:
            ollama.list()  # Test connexion
        except Exception:
            return "⚠️ Erreur: Ollama n'est pas accessible. Démarrez-le avec 'ollama serve'."

        try:
            logger.info("🤖 Génération avec Llama...")
            response = ollama.generate(
                model=self.llama_model,
                prompt=prompt,
                options={
                    "temperature": float(self.temperature),
                    "num_predict": int(self.max_tokens),
                    "top_k": 40,
                    "top_p": 0.9,
                },
            )
            return response.get("response", "").strip()
        except Exception as e:
            logger.error(f"❌ Erreur génération: {e}")
            return f"⚠️ Erreur lors de la génération: {str(e)}"

    # ========== PIPELINE COMPLET ==========

    def query(self, question: str) -> dict:
        """
        Pipeline RAG complet:
        1. Garde-fou domaine
        2. Recherche vectorielle (top-k)
        3. Prompt enrichi
        4. Génération LLM
        5. Réponse structurée avec sources
        """
        logger.info(f"📝 Question: {question}")

        scope = self.is_in_scope(question)

        # CAS 1: Salutation
        if scope == "greeting":
            msg = (
                "Bonjour ! 👋 Je suis votre assistant spécialisé sur les sites "
                "archéologiques de Tunisie. \n\n"
                "Je peux répondre à vos questions sur:\n"
                "• Carthage, Dougga, El Jem, Sbeïtla, Kerkouane, Bulla Regia, etc.\n"
                "• L'histoire, l'architecture et les découvertes archéologiques\n"
                "• Les périodes punique, romaine, byzantine...\n\n"
                "Posez-moi une question !"
            )
            return {
                "answer": msg,
                "sources": [],
                "has_sources": False,
                "question": question,
            }

        # CAS 2: Hors domaine
        if not scope:
            msg = (
                "Désolé, je ne peux répondre qu'aux questions concernant "
                "les sites archéologiques de Tunisie.\n\n"
                "Exemples de questions valides:\n"
                "• Quelles sont les particularités du théâtre romain de Dougga ?\n"
                "• Parle-moi de l'amphithéâtre d'El Jem\n"
                "• Quel est l'histoire de Carthage ?"
            )
            return {
                "answer": msg,
                "sources": [],
                "has_sources": False,
                "question": question,
            }

        # CAS 3: RAG normal
        # 3.1 Recherche vectorielle
        docs = self.search(question)

        # 3.2 Pas de sources pertinentes
        if not docs:
            msg = (
                "Je ne dispose pas d'information fiable sur ce point dans ma base de connaissances.\n\n"
                "Reformulez votre question ou posez une question sur un site spécifique "
                "(Carthage, Dougga, El Jem, Sbeïtla, Kerkouane, Bulla Regia, etc.)."
            )
            return {
                "answer": msg,
                "sources": [],
                "has_sources": False,
                "question": question,
            }

        # 3.3 Génération avec contexte
        prompt = self.build_prompt(question, docs)
        answer = self.generate_response(prompt)

        return {
            "answer": answer,
            "sources": docs,
            "has_sources": True,
            "question": question,
        }

    def debug_search(self, query: str) -> None:
        """Debug: affiche les résultats bruts de recherche"""
        if not self.collection:
            print("❌ Collection non disponible")
            return

        query_embedding = self.embedding_model.encode(query).tolist()
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=10,
            include=["documents", "metadatas", "distances"],
        )

        print(f"\n🔍 DEBUG RECHERCHE: '{query}'")
        print("=" * 70)

        dists = results.get("distances", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        docs = results.get("documents", [[]])[0]

        if not dists:
            print("Aucun résultat")
            return

        for i, distance in enumerate(dists):
            similarity = 1 - (distance / 2.0)
            meta = metas[i] if i < len(metas) else {}
            site = meta.get("site", "N/A")
            
            print(f"{i+1}. Similarité: {similarity:.3f} | Distance: {distance:.3f} | Site: {site}")
            
            if i < 3 and i < len(docs):
                preview = (docs[i][:150] + "...").replace("\n", " ")
                print(f"   Extrait: {preview}")
        
        print()
