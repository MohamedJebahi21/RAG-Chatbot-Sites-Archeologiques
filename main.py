# main.py - VERSION SIMPLIFIÉE
import sys
import os
from pathlib import Path

def main_menu():
    """Menu principal"""
    print("=" * 70)
    print("🏛️  CHATBOT RAG - ARCHÉOLOGIE TUNISIENNE")
    print("=" * 70)
    print("\nQue souhaitez-vous faire?")
    print("1. 🔧 Indexer les documents (créer la base de données)")
    print("2. 🚀 Lancer le chatbot (interface Streamlit)")
    print("3. 🧪 Tester le système RAG")
    print("4. ❌ Quitter")
    
    choice = input("\nVotre choix (1-4): ").strip()
    
    if choice == "1":
        print("\n🔧 Lancement de l'indexation...")
        os.system("python ingest.py")
        
    elif choice == "2":
        print("\n🚀 Lancement de l'interface...")
        print("➡️  Ouvrez http://localhost:8501 dans votre navigateur")
        print("➡️  Appuyez sur Ctrl+C pour arrêter")
        os.system("streamlit run app.py")
        
    elif choice == "3":
        print("\n🧪 Test du système...")
        test_rag()
        
    elif choice == "4":
        print("\n👋 Au revoir!")
        sys.exit(0)
        
    else:
        print("❌ Choix invalide!")

def test_rag():
    """Test simple du système RAG"""
    try:
        from rag import RAGSystem
        from config import Config
        
        print("Chargement du système RAG...")
        rag = RAGSystem(
            chroma_db_path=str(Config.CHROMA_DB_PATH),
            embedding_model=Config.EMBEDDING_MODEL
        )
        
        questions = [
            "Qu'est-ce que Carthage?",
            "Parle-moi de Dougga",
            "Quels sont les sites romains en Tunisie?"
        ]
        
        for q in questions:
            print(f"\n{'='*50}")
            print(f"Question: {q}")
            result = rag.query(q)
            print(f"Réponse: {result['answer'][:200]}...")
            print(f"Sources trouvées: {len(result['sources'])}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    main_menu()