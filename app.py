# app.py - Optimized & Fast UI
# Mini-projet IA Générative - Sites Archéologiques de Tunisie

import sys
import json
from pathlib import Path
from datetime import datetime

import streamlit as st

sys.path.append(str(Path(__file__).parent))
from config import Config
from rag import RAGSystem


# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title=Config.PAGE_TITLE,
    page_icon=Config.PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)


# -----------------------------
# OPTIMIZED CSS - FAST & SMOOTH
# -----------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=Inter:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/icon?family=Material+Icons');

:root{
  --bg-dark: #0d1117;
  --bg-main: #161b22;
  --bg-elevated: #1c2128;
  
  --sidebar-bg: #1e1410;
  --sidebar-border: rgba(201,168,106,.2);
  
  --gold: #C9A86A;
  --gold-light: #d4b77e;
  --gold-dark: #9d8152;
  
  --chat-user: #2d3748;
  --chat-assistant: #3d2e1a;
  --chat-text: #e8e6e3;
  
  --text-primary: #f0f0f0;
  --text-secondary: rgba(240,240,240,.7);
  
  --border: rgba(255,255,255,.1);
  --shadow: 0 4px 12px rgba(0,0,0,.3);
}

/* Simple clean background */
.main{
  background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
}

.block-container{
  padding: 2rem 1.5rem;
  max-width: 1300px;
}

/* Clean sidebar */
[data-testid="stSidebar"]{
  background: linear-gradient(165deg, var(--sidebar-bg) 0%, #2d2115 100%);
  padding: 1.5rem 1.2rem;
  border-right: 1px solid var(--sidebar-border);
}

[data-testid="stSidebar"] *:not(.material-icons){
  font-family: 'Inter', sans-serif !important;
  color: var(--text-primary) !important;
}

.material-icons{
  font-family: 'Material Icons' !important;
}

/* Sidebar headings */
[data-testid="stSidebar"] h3{
  color: var(--gold-light) !important;
  font-family: 'Playfair Display', serif !important;
  font-weight: 700 !important;
  font-size: 1.1rem !important;
  margin-bottom: 1rem !important;
  letter-spacing: .5px;
}

/* Metrics */
[data-testid="stMetricLabel"]{
  color: var(--text-secondary) !important;
  font-weight: 600 !important;
  font-size: .85rem !important;
}

[data-testid="stMetricValue"]{
  color: var(--gold-light) !important;
  font-weight: 800 !important;
  font-size: 2rem !important;
}

/* Simple sidebar buttons */
[data-testid="stSidebar"] .stButton button{
  width: 100% !important;
  border: 1px solid rgba(201,168,106,.25) !important;
  border-radius: 12px !important;
  padding: .75rem 1.2rem !important;
  font-weight: 700 !important;
  background: linear-gradient(135deg, var(--gold) 0%, var(--gold-dark) 100%) !important;
  color: #fff !important;
  box-shadow: 0 2px 8px rgba(0,0,0,.3) !important;
  transition: transform .2s, box-shadow .2s;
}

[data-testid="stSidebar"] .stButton button:hover{
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(201,168,106,.4) !important;
}

[data-testid="stSidebar"] hr{
  border: none;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--sidebar-border), transparent);
  margin: 1.2rem 0 !important;
}

/* Clean header */
.header-card{
  background: linear-gradient(135deg, #3d2e1a 0%, #4d3820 100%);
  border: 1px solid rgba(201,168,106,.2);
  border-radius: 20px;
  padding: 2.5rem 2rem;
  box-shadow: var(--shadow);
  text-align: center;
  margin-bottom: 1.5rem;
}

.header-title{
  font-family: 'Playfair Display', serif;
  font-size: 2.8rem;
  font-weight: 800;
  color: var(--gold-light);
  letter-spacing: 2px;
  margin: 0;
  display: inline-flex;
  align-items: center;
  gap: 1rem;
}

.header-title .material-icons{
  font-size: 3rem;
  color: var(--gold-light);
}

.header-sub{
  margin: .8rem 0 0 0;
  color: rgba(255,255,255,.85);
  font-size: 1.1rem;
  font-weight: 500;
}

/* IMPROVED CHAT BUBBLES - DARK THEME */
div[data-testid="stChatMessage"]{
  border-radius: 16px !important;
  padding: 1.5rem 1.8rem !important;
  margin: 1rem 0 !important;
  border: 1px solid var(--border) !important;
  transition: transform .2s;
}

/* User message - Cool gray-blue */
div[data-testid="stChatMessage"][data-testid*="user-message"],
div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]){
  background: linear-gradient(135deg, #2d3748 0%, #374151 100%) !important;
  border-left: 4px solid #3b82f6 !important;
}

/* Assistant message - Warm brown-gold */
div[data-testid="stChatMessage"][data-testid*="assistant-message"],
div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]){
  background: linear-gradient(135deg, #3d2e1a 0%, #4a3620 100%) !important;
  border-left: 4px solid var(--gold) !important;
}

div[data-testid="stChatMessage"]:hover{
  transform: translateX(3px);
}

/* Chat text - Light on dark */
div[data-testid="stChatMessage"] p,
div[data-testid="stChatMessage"] div,
div[data-testid="stChatMessage"] span:not(.material-icons){
  color: var(--chat-text) !important;
  line-height: 1.7 !important;
  font-size: 1.05rem !important;
  font-weight: 500 !important;
}

div[data-testid="stChatMessage"] strong{
  color: #ffffff !important;
  font-weight: 700 !important;
}

/* Chat avatars */
div[data-testid="stChatMessage"] [data-testid="chatAvatarIcon-user"]{
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
}

div[data-testid="stChatMessage"] [data-testid="chatAvatarIcon-assistant"]{
  background: linear-gradient(135deg, var(--gold) 0%, var(--gold-dark) 100%) !important;
}

/* Chat input */
div[data-testid="stChatInput"]{
  border-radius: 16px !important;
}

div[data-testid="stChatInput"] textarea{
  background: var(--bg-elevated) !important;
  color: var(--text-primary) !important;
  caret-color: var(--gold) !important;
  border: 2px solid var(--border) !important;
  border-radius: 16px !important;
  padding: 1.2rem 1.5rem !important;
  font-size: 1.05rem !important;
  font-weight: 500 !important;
  transition: border-color .2s;
}

div[data-testid="stChatInput"] textarea:focus{
  border-color: var(--gold) !important;
  outline: none !important;
}

div[data-testid="stChatInput"] textarea::placeholder{
  color: var(--text-secondary) !important;
}

/* Source cards */
.source-card{
  background: linear-gradient(135deg, #2d2115 0%, #3d2e1a 100%);
  border-left: 4px solid var(--gold);
  padding: 1.3rem 1.5rem;
  border-radius: 14px;
  margin: 1rem 0;
  border: 1px solid rgba(201,168,106,.2);
  transition: transform .2s;
}

.source-card:hover{
  transform: translateX(5px);
  border-left-width: 6px;
}

.source-title{
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--gold-light);
  margin-bottom: .6rem;
  display: flex;
  align-items: center;
  gap: .5rem;
}

.source-title::before{
  content: '📚';
}

.source-meta{
  color: rgba(232,230,227,.8);
  font-size: .95rem;
  line-height: 1.6;
  margin: .3rem 0;
}

.source-meta strong{
  color: var(--gold);
  font-weight: 600;
}

.badge{
  display: inline-block;
  margin-top: .7rem;
  padding: .35rem .9rem;
  border-radius: 999px;
  font-weight: 700;
  font-size: .85rem;
  color: #fff;
  letter-spacing: .3px;
}

/* Info box */
div[data-testid="stInfo"]{
  background: linear-gradient(135deg, #1e3a5f 0%, #2d4a6f 100%) !important;
  border-left: 4px solid #3b82f6 !important;
  border-radius: 12px !important;
  padding: 1.2rem 1.5rem !important;
  color: #bfdbfe !important;
  font-weight: 600 !important;
  border: 1px solid rgba(59,130,246,.2);
}

/* Scrollbar */
::-webkit-scrollbar{
  width: 10px;
}

::-webkit-scrollbar-track{
  background: rgba(0,0,0,.2);
}

::-webkit-scrollbar-thumb{
  background: linear-gradient(180deg, var(--gold) 0%, var(--gold-dark) 100%);
  border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover{
  background: var(--gold-light);
}

/* Hide collapse */
[data-testid="collapsedControl"],
section[data-testid="stSidebar"] button[kind="header"]{
  display: none !important;
}
</style>
""",
    unsafe_allow_html=True,
)


# -----------------------------
# Backend
# -----------------------------
@st.cache_resource
def load_rag_system():
    return RAGSystem(
        chroma_db_path=str(Config.CHROMA_DB_PATH),
        embedding_model=Config.EMBEDDING_MODEL,
        llama_model=Config.LLAMA_MODEL,
        top_k=Config.TOP_K,
        similarity_threshold=Config.SIMILARITY_THRESHOLD,
    )


def init_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "query_count" not in st.session_state:
        st.session_state.query_count = 0
    if "show_sources" not in st.session_state:
        st.session_state.show_sources = True
    if "show_metrics" not in st.session_state:
        st.session_state.show_metrics = False


def save_conversation_json():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fn = f"conversation_{ts}.json"
    with open(fn, "w", encoding="utf-8") as f:
        json.dump(
            {
                "timestamp": ts,
                "query_count": st.session_state.query_count,
                "messages": st.session_state.messages,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    return fn


def source_badge(sim: float):
    if sim >= 0.70:
        return ("Très pertinent", "#10b981")
    if sim >= 0.50:
        return ("Pertinent", "#f59e0b")
    return ("Peu pertinent", "#ef4444")


def render_source_card(src: dict):
    meta = src.get("metadata", {}) or {}
    filename = meta.get("filename", "Document")
    site = meta.get("site", "N/A")
    period = meta.get("period", "N/A")
    ref = meta.get("source", "N/A")
    sim = float(src.get("similarity", 0.0))

    label, color = source_badge(sim)

    st.markdown(
        f"""
<div class="source-card">
  <div class="source-title">{filename}</div>
  <div class="source-meta"><strong>🏛️ Site:</strong> {site}</div>
  <div class="source-meta"><strong>📅 Période:</strong> {period}</div>
  <div class="source-meta"><strong>📖 Référence:</strong> {ref}</div>
  <span class="badge" style="background:{color};">{label} • {sim:.0%}</span>
</div>
""",
        unsafe_allow_html=True,
    )


# -----------------------------
# Main app
# -----------------------------
def main():
    init_state()

    st.markdown(
        """
<div class="header-card">
  <div class="header-title">
    <span class="material-icons">account_balance</span>
    CHATBOT RAG
  </div>
  <div class="header-sub">Sites archéologiques de Tunisie • RAG + Llama 3</div>
</div>
""",
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown("### 📊 Statistiques")
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Questions", st.session_state.query_count)
        with c2:
            st.metric("Échanges", len(st.session_state.messages) // 2)

        st.markdown("---")

        st.markdown("### ⚙️ Paramètres")
        st.session_state.show_sources = st.toggle("📚 Afficher sources", value=st.session_state.show_sources)
        st.session_state.show_metrics = st.toggle("📈 Afficher métriques", value=st.session_state.show_metrics)

        st.markdown("---")

        st.markdown("### 🎯 Actions")
        a1, a2 = st.columns(2)
        with a1:
            if st.button("🗑️ Effacer", use_container_width=True):
                st.session_state.messages = []
                st.session_state.query_count = 0
                st.rerun()
        with a2:
            if st.button("💾 Sauvegarder", use_container_width=True):
                if st.session_state.messages:
                    fn = save_conversation_json()
                    st.success(f"✅ Sauvegardé: {fn}")
                else:
                    st.warning("Rien à sauvegarder")

        st.markdown("---")

        st.markdown("### 💡 Exemples")
        examples = [
            "Parle-moi de Carthage",
            "Le théâtre de Dougga ?",
            "L'amphithéâtre d'El Jem",
            "Sites puniques",
            "Compare Carthage et Dougga",
        ]
        for ex in examples:
            if st.button(ex, use_container_width=True, key=f"ex_{ex}"):
                st.session_state.example_question = ex
                st.rerun()

        st.markdown("---")
        st.caption("🎓 Mini-projet 2025")

    try:
        rag = load_rag_system()
    except Exception as e:
        st.error(f"❌ Système RAG indisponible: {e}")
        st.info("💡 Exécutez: `python ingest.py`")
        return

    if not st.session_state.messages:
        st.info("👋 Bienvenue ! Posez une question sur les sites archéologiques tunisiens.")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if "example_question" in st.session_state:
        question = st.session_state.example_question
        del st.session_state.example_question
    else:
        question = st.chat_input("💬 Tapez votre question...")

    if not question:
        return

    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.query_count += 1

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("🔍 Recherche en cours..."):
            result = rag.query(question)

        answer = result.get("answer", "")
        sources = result.get("sources", []) or []

        st.markdown(answer)

        if st.session_state.show_sources:
            st.markdown("---")
            st.markdown("### 📚 Sources")
            if sources:
                for s in sources:
                    render_source_card(s)
            else:
                st.info("ℹ️ Aucune source trouvée pour cette question.")

        if st.session_state.show_metrics and sources:
            sims = [float(s.get("similarity", 0.0)) for s in sources]
            avg = sum(sims) / len(sims)
            st.markdown("---")
            st.markdown("### 📊 Métriques")
            m1, m2, m3 = st.columns(3)
            m1.metric("📄 Sources", len(sources))
            m2.metric("📊 Moyenne", f"{avg:.0%}")
            m3.metric("⭐ Maximum", f"{max(sims):.0%}")

    st.session_state.messages.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()
