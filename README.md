# GCP ADK Document QA Agent

This project implements a lightweight **retrieval-augmented generation (RAG)** pipeline powered by **Gemini 2.5 Flash** and **Google ADK**, enabling question answering across multiple PDF documents.

---

##  Overview
The app extracts text from PDFs, chunks it, embeds each passage using `text-embedding-004`, and retrieves the top passages most relevant to a user query. Those passages are then passed to `gemini-2.5-flash` for grounded, citation-rich answers.

---

## ⚙️ Setup Instructions

### 1. Clone & create environment
```bash
git clone <your-repo-url>
cd gcp-adk-doc-agent
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your API key
Create a `.env` file in the project root and add:
```bash
GOOGLE_API_KEY=your_gemini_api_key_here
```

To verify the key works:
```bash
python -c "import os, google.generativeai as genai; genai.configure(api_key=os.getenv('GOOGLE_API_KEY')); print(genai.GenerativeModel('gemini-2.5-flash').generate_content('Hello from Gemini!').text)"
```

---

##  Directory Structure

```
GCP-ADK-DOC-AGENT/
│
├── adk_app/
│   ├── __pycache__/
│   ├── agents/
│   │   ├── __pycache__/
│   │   ├── ingestion_agent.py
│   │   ├── reasoning_agent.py
│   ├── cache.py
│   ├── llm_clients.py
│   ├── logging_utils.py
│   ├── pipeline.py
│   ├── retrieval.py
│   ├── schemas.py
│   ├── server.py
│   ├── settings.py
│   ├── utils.py
│
├── data/
├── outputs/
├── scripts/
│   ├── __pycache__/
│   ├── run_query.py
│
├── tests/
├── .env
├── .env.example
├── .gitignore
├── Dockerfile
├── LICENSE
├── README.md
└── requirements.txt
```

##  Local Development

1. Create and activate virtual environment:
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
2. Run locally:
```powershell
uvicorn adk_app.server:app --host 127.0.0.1 --port 8080
```
3. Test endpoint:
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8080/health"
```

🐳 Docker Build

```powershell
docker build -t adk-doc-agent:demo .
docker run -p 8080:8080 --env GOOGLE_API_KEY=$env:GOOGLE_API_KEY adk-doc-agent:demo
```

☁️ Deploy on Google Cloud Run

```powershell
gcloud builds submit --tag us-central1-docker.pkg.dev/<PROJECT_ID>/adk-images/adk-doc-agent

gcloud run deploy adk-doc-agent `
  --image us-central1-docker.pkg.dev/<PROJECT_ID>/adk-images/adk-doc-agent `
  --region us-central1 `
  --allow-unauthenticated `
  --platform managed `
  --memory 1Gi `
  --cpu 1 `
  --timeout 300 `
  --min-instances 0 `
  --set-env-vars "GOOGLE_API_KEY=$env:GOOGLE_API_KEY"
```

---

##  Running the Pipeline
Run the following command to ask a question over PDFs in the `data/` folder:
```bash
python -m scripts.run_query --q "Summarize each document and highlight differences." --data data --top-k 3 --show-logs --save-json outputs/demo1.json
```

### Available Flags
| Flag | Description |
|------|--------------|
| `--q` | Your question in natural language |
| `--data` | Folder containing PDF documents |
| `--top-k` | Number of retrieved passages |
| `--show-logs` | Prints detailed step-by-step logs |
| `--save-json` | Saves the output to a JSON file |

---

## 🧾 Example Output
```json
{
  "query": "Summarize each document and highlight differences.",
  "answer": "\"Why Won’t You Listen to Me_ Measuring Receptiveness to Opposing Views\" discusses factors related to receptiveness, such as 'Derogation of opponents' and 'Taboo issues', and is attributed to Minson, Chen, and Tinsley (Management Science, 2020). Conversely, 'Conversational Receptiveness - Expressing engagement with opposing views' focuses on conversational strategies for understanding opposing views (Yeomans et al., 2020). Both discuss receptiveness but differ in focus, methodology, and journal context.",
  "citations": [
    {
      "filename": "Why Won’t You Listen to Me_ Measuring Receptiveness to Opposing Views.pdf",
      "page": 10
    },
    {
      "filename": "Conversational Receptiveness - Expressing engagement with opposing views..pdf",
      "page": 16
    }
  ],
  "meta": {
    "used_model": "gemini-2.5-flash",
    "num_docs": 3,
    "retrieval_k": 3,
    "latency_ms": 14117,
    "confidence": 1.0
  }
}
```
---
Latency was reduced from several minutes to just a few seconds by adding in-memory caching for embeddings, increasing chunk size to minimize total chunk count, and lowering retrieval top-k to reduce model load. PDF content is now parsed once at startup rather than on every query. Batch embedding calls were added where supported, cutting down request overhead. Together these optimizations reduced end-to-end response time from roughly 2–3 minutes to about 6–9 seconds.
```

---

##  Example Queries
```bash
python -m scripts.run_query --q "How do the authors define receptiveness? Provide phrasing and citations." --data data --top-k 5 --show-logs
python -m scripts.run_query --q "List any experiments involving adolescents or children." --data data --top-k 5 --show-logs
python -m scripts.run_query --q "Compare conclusions across studies." --data data --top-k 5 --show-logs
```

---

##  Key Components
| File | Description |
|------|--------------|
| `adk_app/llm_clients.py` | Connects to Gemini 2.5 and embedding APIs |
| `adk_app/agents/reasoning_agent.py` | Handles retrieval and grounded answer generation |
| `adk_app/retrieval.py` | Manages chunking, embedding, and similarity search |
| `adk_app/pipeline.py` | Orchestrates ingestion, reasoning, and response structuring |
| `scripts/run_query.py` | CLI interface for testing and demos |

---

##  Optional Enhancements
- Cache embeddings for faster repeat runs  
- Track `retrieval_time_ms` and `generation_time_ms` in metadata  
- Support multimodal (image + text) Gemini models for PDFs with figures  
- Add FastAPI or Streamlit frontend for interactive document querying  

---

##  Quick Demo Workflow
```bash
# Example 1: High-level summary
python -m scripts.run_query --q "Summarize each document and highlight differences." --data data --top-k 3 --show-logs --save-json outputs/demo1.json

# Example 2: Extract key definitions
python -m scripts.run_query --q "Define 'receptiveness' as described by each author." --data data --top-k 5 --show-logs --save-json outputs/demo2.json

# Example 3: Edge case (no result)
python -m scripts.run_query --q "List all studies involving children under 12." --data data --top-k 5 --show-logs --save-json outputs/demo_not_found.json
```

---

## 👩‍💻 Author
Built by **Oshin**, powered by **Gemini 2.5 Flash** and **Google ADK**.

