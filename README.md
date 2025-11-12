# GCP ADK Document QA Agent

This project implements a lightweight **retrieval-augmented generation (RAG)** pipeline powered by **Gemini 2.5 Flash** and **Google ADK**, enabling question answering across multiple PDF documents.

---

## 🧠 Overview
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

## 📂 Directory Structure

```
adk_app/
├── agents/
│   ├── ingestion_agent.py
│   ├── reasoning_agent.py
│   └── __pycache__/
├── cache.py
├── llm_clients.py
├── logging_utils.py
├── pipeline.py
├── retrieval.py
├── schemas.py
├── settings.py
├── utils.py
├── __pycache__/

scripts/
├── run_query.py
├── __pycache__/

tests/
├── (test files)

data/
├── *.pdf

outputs/
├── demo1.json

.venv/
.env
.env.example
.gitignore
LICENSE
README.md
requirements.txt
```

---

## 🚀 Running the Pipeline
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

## 🧪 Example Queries
```bash
python -m scripts.run_query --q "How do the authors define receptiveness? Provide phrasing and citations." --data data --top-k 5 --show-logs
python -m scripts.run_query --q "List any experiments involving adolescents or children." --data data --top-k 5 --show-logs
python -m scripts.run_query --q "Compare conclusions across studies." --data data --top-k 5 --show-logs
```

---

## 🧰 Key Components
| File | Description |
|------|--------------|
| `adk_app/llm_clients.py` | Connects to Gemini 2.5 and embedding APIs |
| `adk_app/agents/reasoning_agent.py` | Handles retrieval and grounded answer generation |
| `adk_app/retrieval.py` | Manages chunking, embedding, and similarity search |
| `adk_app/pipeline.py` | Orchestrates ingestion, reasoning, and response structuring |
| `scripts/run_query.py` | CLI interface for testing and demos |

---

## 🧩 Optional Enhancements
- Cache embeddings for faster repeat runs  
- Track `retrieval_time_ms` and `generation_time_ms` in metadata  
- Support multimodal (image + text) Gemini models for PDFs with figures  
- Add FastAPI or Streamlit frontend for interactive document querying  

---

## 🧭 Quick Demo Workflow
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

