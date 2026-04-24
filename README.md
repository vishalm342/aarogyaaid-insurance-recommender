# AarogyaAid Recommender

An AI-powered health insurance recommendation platform built for AarogyaAid's engineering assessment. The system uses a RAG (Retrieval-Augmented Generation) pipeline to help Indian patients navigate health insurance decisions with empathy, transparency, and grounded policy data.

## What This Builds

| Surface | Purpose |
|---|---|
| **User Portal** | Captures a 6-field health and lifestyle profile; delivers AI-driven policy recommendations with a peer comparison table, coverage detail breakdown, and a personalised explanation |
| **Admin Panel** | Manages the policy knowledge base — upload, edit, delete — so the AI agent's knowledge can be updated without touching code |

## Tech Stack & Justifications

### Frontend — Next.js 15 (App Router) + TypeScript + Tailwind CSS

Next.js was chosen because the recommendation output requires three complex components (Peer Comparison Table, Coverage Detail Table, and the personalised Why This Policy explanation) rendered simultaneously alongside a persistent chat interface. Next.js App Router enables clean server/client component separation: the static layout is server-rendered for fast initial load, while the profile form, recommendation output, and chat panel are client components sharing state via sessionStorage and React context.

### Backend — FastAPI (Python)

RAG pipelines and LLM inference are inherently I/O-bound. FastAPI's native async support ensures the server never blocks while the AI agent queries the vector store or waits for the LLM to complete generation. Pydantic models enforce strict request/response validation across all endpoints.

### AI Orchestration — LangGraph

Google ADK was evaluated, but this engine has two hard requirements better suited for LangGraph:

- **Deterministic guardrail routing** — when a user asks a medical advice question, the graph must route to a refusal node with certainty. Relying solely on prompt engineering introduces unacceptable non-determinism.
- **Persistent multi-turn state** — the user's 6-field health profile and the recommended policy must be maintained as immutable, typed state across every chat turn without re-asking. LangGraph's state-graph architecture treats both as first-class citizens.

### Vector Store — MongoDB Atlas Vector Search

The brief requires that admin document deletion immediately removes vectors from the store. Using MongoDB Atlas Vector Search keeps policy metadata and vector embeddings in a single unified document store. This enables atomic deletion — one delete_many operation removes both the document record and its associated vectors, eliminating any risk of the agent recommending stale data.

### LLM Inference & Embeddings

- **Inference (SambaNova Llama-3.3-70B)**: The interactive chat explainer must feel immediate. SambaNova's high-speed inference eliminates typical RAG generation latency.
- **Embeddings (Cohere embed-english-light-v3.0)**: Chosen for fast, efficient 384-dimensional semantic vectorization of policy chunks.

## Architecture Overview

```plaintext
User Portal (React)
    │
    ├── POST /api/profile/recommend
    │       └── LangGraph Agent
    │               ├── retrieve_policy_chunks (MongoDB Atlas)
    │               └── generate_recommendation (3 required sections)
    │
    ├── POST /api/chat
    │       └── LangGraph Agent (session-aware)
    │               ├── retrieve_policy_chunks
    │               └── respond with grounding + guardrail check
    │
Admin Panel (React)
    │
    ├── POST /api/admin/login        (env-var username/password → JWT)
    ├── POST /api/admin/upload       (upload → parse → chunk → embed → store)
    ├── GET  /api/admin/policies     (list with metadata)
    └── DELETE /api/admin/policies/:id (remove record + vectors atomically)
```

## Recommendation Logic

The engine processes the 6 profile fields in a deliberate, ordered sequence:

1. **Pre-existing Conditions** — First-pass filter. Policies with hard exclusions for the user's condition are flagged, not hidden.
2. **Annual Income / Financial Band** — Sets the affordability ceiling. Policies with premiums exceeding roughly 4% of stated annual income are deprioritised.
3. **Age** — Determines premium bracket sensitivity and waiting period tolerance. Age cross-references with pre-existing conditions to flag risk in the peer comparison table.
4. **City / Tier** — Adjusts network hospital availability weighting.
5. **Lifestyle** — Adjusts OPD versus hospitalisation cover weighting.
6. **Full Name** — Used throughout to personalise responses, ensuring the output reads as personal advice.

**Suitability Score** is a weighted calculation: Exclusion Match (40%) + Affordability Fit (30%) + Network Availability (20%) + Waiting Period Tolerance (10%).

## Project Structure

```plaintext
aarogyaaid-insurance-recommender/
├── PRD.md
├── README.md
│
├── backend/
│   ├── .env.example
│   ├── main.py
│   ├── config.py
│   ├── requirements.txt
│   ├── agent/       # LangGraph orchestration, prompts, tools, state
│   ├── db/          # MongoDB connection
│   ├── rag/         # PyMuPDF chunking, Cohere embedding, insertion
│   ├── routes/      # FastAPI endpoint definitions
│   ├── sample_policies/
│   │   ├── hdfc_ergo_myhealth.txt
│   │   ├── niva_bupa_reassure.txt
│   │   └── star_health_comprehensive.txt
│   └── tests/
│
└── frontend/
    ├── package.json
    ├── next.config.ts
    ├── app/
    │   ├── globals.css
    │   ├── layout.tsx
    │   ├── page.tsx            # User Profile Intake Form
    │   ├── admin/              # Admin Login & Dashboard
    │   ├── chat/               # Chat Explainer Interface
    │   └── results/            # Recommendation Output & Tables
    └── lib/
        └── api.ts
```

## Setup Instructions

### Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB Atlas account
- SambaNova and Cohere API keys

### 1. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # Fill in your actual keys in .env
uvicorn main:app --reload --port 8000
```

### 2. Frontend setup

```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:3000
```

### 3. MongoDB Atlas vector index

In your Atlas cluster, create a vector search index on the chunks_collection. Crucially, set the dimensions to 384 to match the Cohere Light model.

```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 384,
      "similarity": "cosine"
    }
  ]
}
```

### 4. Seed the knowledge base

Upload the sample policy documents located in `backend/sample_policies/` via the Admin Panel (`http://localhost:3000/admin`).

## Environment Variables

See `backend/.env.example` for all required variables.

```env
MONGODB_URI
MONGODB_DB_NAME
SAMBANOVA_API_KEY
SAMBANOVA_BASE_URL
SAMBANOVA_MODEL
COHERE_API_KEY
EMBEDDING_MODEL
ADMIN_USERNAME
ADMIN_PASSWORD
JWT_SECRET
JWT_ALGORITHM
```

## Grounding Verification

The following live tests were executed to ensure Document Intelligence and Guardrails:

- **Contextual Grounding**: User Profile (Rajesh, 45, Diabetic) submitted. The AI Explainer successfully remembered the user's age ("Rajesh, you are 45 years old.") across persistent chat turns.
- **Anti-Hallucination**: When asked to explain a "Waiting Period" as it applies specifically to the user's recommended Diabetes Care Policy, the agent defined the term accurately, but explicitly stated: "I cannot find that information in the uploaded policy documents" regarding the specific application to that exact policy. This proves the RAG pipeline will refuse to hallucinate specific policy details if the relevant chunk is not successfully retrieved from the vector store.

## Known Limitations (v1)

- Family floater policies are not supported; all recommendations are for individual cover.
- Scanned (image-based) PDFs are not supported; only text-native PDFs/TXT files are parsed correctly.
- Session context relies on sessionStorage; a hard browser refresh clears the current chat and profile context.

