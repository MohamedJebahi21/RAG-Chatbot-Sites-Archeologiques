# Tunisian Archaeological Sites — RAG Chatbot

A French-language question-answering application about Tunisia's archaeological heritage. The project combines semantic retrieval with a local language model so that answers are grounded in a curated corpus and can include relevant source context.

> **Project type:** Applied generative AI / information retrieval prototype  
> **Interface:** Streamlit  
> **Language:** French  
> **Runtime:** Python 3.8+

## What it demonstrates

- A complete retrieval-augmented generation (RAG) pipeline
- Document ingestion and semantic search with ChromaDB
- Local inference through Ollama
- A Streamlit chat interface with conversation history and source display
- A domain-focused corpus covering major Tunisian archaeological sites

## Architecture

```text
                         ┌──────────────────────┐
                         │   Streamlit (app.py)  │
                         └──────────┬───────────┘
                                    │ user question
                                    ▼
                         ┌──────────────────────┐
                         │   RAG pipeline (rag)  │
                         └──────────┬───────────┘
                                    │ retrieve context
                                    ▼
┌──────────────────┐      ┌──────────────────────┐      ┌─────────────────┐
│ Corpus (data/)   │ ───▶ │ ChromaDB vector store │ ───▶ │ Ollama + LLM    │
└──────────────────┘      └──────────────────────┘      └─────────────────┘
                                    │
                                    ▼
                         grounded answer + sources
```

## Repository structure

```text
.
├── app.py                 # Streamlit user interface
├── main.py                # Application entry point / orchestration
├── rag.py                 # Retrieval and answer-generation pipeline
├── ingest.py              # Corpus ingestion and vector-store creation
├── config.py              # Runtime configuration
├── data/                  # Archaeological knowledge corpus
├── requirements.txt       # Python dependencies
└── code for sources.py    # Source-processing utility
```

## Quick start

### 1. Clone and create a virtual environment

```bash
git clone https://github.com/MohamedJebahi21/RAG-Chatbot-Sites-Archeologiques.git
cd RAG-Chatbot-Sites-Archeologiques

python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
.venv\\Scripts\\Activate.ps1

pip install -r requirements.txt
```

### 2. Install and start Ollama

Install [Ollama](https://ollama.com), then pull a local model such as `mistral`:

```bash
ollama pull mistral
ollama serve
```

If your Ollama installation uses a different model, update the model name in `config.py`.

### 3. Build the vector store

```bash
python ingest.py
```

This processes the documents in `data/` and creates the local ChromaDB index used by the application.

### 4. Launch the interface

```bash
streamlit run app.py
```

The application is normally available at `http://localhost:8501`.

## Configuration

The main settings are defined in `config.py`, including:

- Ollama model and base URL
- ChromaDB storage path
- Chunk size and overlap
- Number of retrieved documents (`top_k`)
- Generation temperature

For local overrides, use environment variables where supported by the configuration module. Do not commit secrets or machine-specific configuration.

## Example questions

- **Quand Carthage a-t-elle été fondée ?**
- **Décris l’amphithéâtre d’El Jem.**
- **Quels sites contiennent des temples romains ?**
- **Quel est le rôle historique de Dougga ?**

## Data coverage

The corpus includes material about sites such as Carthage, Dougga, Kairouan, Sbeitla, and El Jem, along with other archaeological locations in Tunisia. Retrieval quality depends on the coverage and quality of the local corpus.

## Troubleshooting

### Ollama is not running

```bash
ollama serve
```

### The vector store is missing

Run the ingestion step again:

```bash
python ingest.py
```

### Port 8501 is already in use

```bash
streamlit run app.py --server.port 8502
```

## Limitations and next steps

This is an educational prototype intended to demonstrate a local RAG workflow. Useful next improvements include automated evaluation, stronger source attribution, versioned datasets, typed configuration, and a small regression-test suite for retrieval quality.

## Contributing

Issues and focused pull requests are welcome. Please describe the problem, include reproduction steps, and keep changes scoped to one concern.

## Author

Developed by [Mohamed Jebahi](https://github.com/MohamedJebahi21) as an applied generative AI project focused on Tunisian cultural heritage.
