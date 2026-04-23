# Aarogyaaid Recommender

An AI-powered health insurance recommendation platform built for AarogyaAid's engineering assessment. The system uses a RAG (Retrieval-Augmented Generation) pipeline to help Indian patients navigate health insurance decisions with empathy, transparency, and grounded policy data.

***

## What This Builds

| Surface | Purpose |
|---|---|
| **User Portal** | Captures a 6-field health and lifestyle profile; delivers AI-driven policy recommendations with a peer comparison table, coverage detail breakdown, and a personalised explanation |
| **Admin Panel** | Manages the policy knowledge base — upload, edit, delete — so the AI agent's knowledge can be updated without touching code |

***

## Tech Stack & Justifications

### Frontend — Next.js 15 + TypeScript + Tailwind CSS

Next.js was chosen because the recommendation output requires three complex
components (Peer Comparison Table, Coverage Detail Table, and the personalised
Why This Policy explanation) rendered simultaneously alongside a persistent
chat interface — all on a single page without navigation. Next.js App Router
enables clean server/client component separation: the static layout is
server-rendered for fast initial load, while the profile form, recommendation
output, and chat panel are client components sharing state through React
context. TypeScript enforces strict typing across the profile schema,
recommendation response, and chat message flow. Tailwind CSS handles
responsive layout without a custom design system overhead.

### Backend — FastAPI (Python)

RAG pipelines and LLM inference are inherently I/O-bound. FastAPI's native async support ensures the server never blocks while the AI agent queries the vector store or waits for the LLM to complete generation. Its direct Python integration with LangChain eliminates the translation layer between the AI logic and the API layer. Pydantic models enforce strict request/response validation across all endpoints.

### AI Orchestration — LangGraph (not Google ADK)

Google ADK was evaluated and explicitly considered for this use case. It offers convenient routing for standard agentic tasks and integrates well with Google's model ecosystem. However, this insurance recommendation engine has two hard requirements that ADK does not handle as cleanly out of the box:

1. **Deterministic guardrail routing** — when a user asks a medical advice question (e.g., "Should I get bariatric surgery?"), the graph must route to a refusal node with certainty. Relying solely on prompt engineering to enforce this in ADK introduces non-determinism that is unacceptable when the consequence is giving medical guidance.

2. **Persistent multi-turn state** — the user's 6-field health profile and the recommended policy must be maintained as immutable, typed state across every chat turn without re-injection or re-asking. LangGraph's state-graph architecture treats both as first-class citizens: each node receives the full state object and can read profile fields without querying the database again.

LangGraph's explicit node-and-edge architecture also makes the recommendation pipeline auditable — a reviewer can trace exactly which tool was called, what was retrieved, and how the output was formed.

### Vector Store — MongoDB Atlas Vector Search

The brief requires that admin document deletion immediately removes vectors from the store. Using MongoDB Atlas Vector Search keeps policy metadata (name, insurer, upload date, file type) and the vector embeddings in a single unified document store. This enables atomic deletion — one `deleteOne` operation removes both the document record and its associated vectors, eliminating any risk of the agent recommending from a stale or deleted policy. A separate Chroma or Qdrant instance would require synchronised dual-delete with failure modes between two systems.

### Database — MongoDB Atlas

MongoDB's flexible document model is a natural fit for insurance policy metadata, which varies in structure across insurers. Session data (user profile + recommended policy + chat history) is stored as nested documents, making retrieval fast and schema changes incremental. The same Atlas cluster serves both the document database and the vector index, reducing infrastructure complexity.

### LLM Inference — SambaNova (Llama-3.3-70B)

The interactive chat explainer must feel immediate to the user — latency in a health-related conversation breaks trust. SambaNova's high-speed inference eliminates the generation latency typical in RAG pipelines, ensuring responses arrive in under two seconds even with retrieval overhead.

### PDF Parsing — PyMuPDF + Semantic Chunking

Insurance policy PDFs are dense with tables, clause numbering, and fine print. PyMuPDF extracts both text and table structures reliably from text-native PDFs. Chunks are split semantically by clause type (Inclusions, Exclusions, Sub-limits, Co-pay, Waiting Period) rather than fixed token size. This ensures retrieval returns complete, meaningful clauses rather than truncated mid-sentence fragments, which is critical for the Coverage Detail Table that must cite specific document sections.

***

## Architecture Overview

```
User Portal (React)
    │
    ├── POST /api/profile/recommend
    │       └── LangGraph Agent
    │               ├── retrieve_policy_chunks (MongoDB Atlas Vector Search)
    │               ├── get_policy_metadata
    │               └── generate_recommendation (3 required sections)
    │
    ├── POST /api/chat
    │       └── LangGraph Agent (session-aware)
    │               ├── load_session_context (profile + recommended policy)
    │               ├── retrieve_policy_chunks
    │               └── respond with grounding + guardrail check
    │
Admin Panel (React)
    │
    ├── POST /api/admin/login        (env-var username/password → JWT)
    ├── POST /api/admin/policies     (upload → parse → chunk → embed → store)
    ├── GET  /api/admin/policies     (list with metadata)
    ├── PATCH /api/admin/policies/:id (edit policy name / insurer)
    └── DELETE /api/admin/policies/:id (remove record + vectors atomically)
```

***

## Recommendation Logic

The engine processes the 6 profile fields in a deliberate, ordered sequence:

1. **Pre-existing Conditions** — First-pass filter. Policies with hard exclusions for the user's condition are surfaced with the exclusion flagged, not hidden. The agent never recommends a policy that will reject the user's most likely claim.

2. **Annual Income / Financial Band** — Sets the affordability ceiling. Policies with premiums exceeding approximately 4% of stated annual income are deprioritised unless no alternative exists, in which case the agent explains the trade-off explicitly.

3. **Age** — Determines premium bracket sensitivity and waiting period tolerance. A 58-year-old with a cardiac condition cannot afford a 48-month waiting period. Age cross-references with pre-existing conditions to flag this risk in the peer comparison table.

4. **City / Tier** — Adjusts network hospital availability weighting. A Tier-3 user with a cashless-only policy is only as covered as the hospitals in their city's network. The agent names network density as a scoring factor.

5. **Lifestyle** — Adjusts OPD versus hospitalisation cover weighting. Active and Athlete profiles score higher for OPD-heavy policies; Sedentary profiles are scored for depth of hospitalisation cover.

6. **Full Name** — Used throughout to personalise responses. The agent addresses the user by name in the Why This Policy explanation, ensuring the output reads as personal advice rather than a query result.

**Suitability Score** (shown in the Peer Comparison Table) is a weighted calculation:

| Factor | Weight |
|---|---|
| Exclusion match (pre-existing conditions) | 40% |
| Affordability fit (income vs premium) | 30% |
| Network availability (city/tier) | 20% |
| Waiting period tolerance (age cross-reference) | 10% |

***

## Project Structure

```
aarogyaaid-recommender/
├── PRD.md
├── README.md
├── .env.example
├── .gitignore
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── routes/
│   │   ├── recommend.py
│   │   ├── chat.py
│   │   └── admin.py
│   ├── agent/
│   │   ├── graph.py
│   │   ├── tools.py
│   │   ├── prompts.py
│   │   └── session.py
│   ├── rag/
│   │   ├── ingest.py
│   │   ├── retriever.py
│   │   └── chunker.py
│   ├── db/
│   │   └── mongo.py
│   └── tests/
│       └── test_recommendation.py
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── UserPortal.tsx
│   │   │   └── AdminPanel.tsx
│   │   └── components/
│   │       ├── ProfileForm.tsx
│   │       ├── PeerComparisonTable.tsx
│   │       ├── CoverageDetailTable.tsx
│   │       ├── WhyThisPolicy.tsx
│   │       └── ChatExplainer.tsx
│   └── ...
│
└── sample_policies/
    ├── policy_basic_health.txt
    ├── policy_senior_care.txt
    └── policy_diabetes_cover.txt
```

***

## Setup Instructions

### Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB Atlas account (free tier is sufficient)
- SambaNova API key (or Gemini API key as alternative)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/aarogyaaid-recommender.git
cd aarogyaaid-recommender
```

### 2. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env
# Fill in your actual keys in .env
uvicorn main:app --reload --port 8000
```

### 3. Frontend setup

```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:5173
```

### 4. MongoDB Atlas vector index

In your Atlas cluster, create a vector search index on the `policy_chunks` collection:

```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 768,
      "similarity": "cosine"
    }
  ]
}
```

### 5. Seed the knowledge base

Upload the three sample policy documents in `sample_policies/` via the Admin Panel after logging in with the credentials set in your `.env`.

***

## Environment Variables

See `.env.example` for all required variables. Never commit `.env` to the repository.

```
MONGODB_URI              MongoDB Atlas connection string
MONGODB_DB_NAME          Database name (e.g. aarogyaaid)
SAMBANOVA_API_KEY        SambaNova inference API key
GEMINI_API_KEY           Google Gemini API key (embeddings)
ADMIN_USERNAME           Admin panel username
ADMIN_PASSWORD           Admin panel password
JWT_SECRET               Secret for signing admin session tokens
EMBEDDING_MODEL          Embedding model name
```

***

## Running Tests

```bash
cd backend
pytest tests/test_recommendation.py -v
```

The unit test covers the core suitability scoring logic — given a known profile and a set of policy stubs, it asserts the correct policy is ranked first and the exclusion flag is raised for matching pre-existing conditions.

***

## Grounding Verification

Before submitting, the following grounding test was run:

1. Uploaded a policy document containing coverage for **Type 2 Diabetes management**.
2. Asked the agent about diabetes cover using a matching user profile → agent cited a specific clause from the uploaded document with the document name.
3. Asked the agent about **kidney transplant cover**, which does not appear in any uploaded document → agent responded: *"I cannot find information about kidney transplant coverage in the uploaded policy documents. Please consult the insurer directly for this specific query."*

No hallucinated policy data was produced.

***

## Known Limitations (v1)

- Family floater policies are not supported; all recommendations are for individual cover.
- Network hospital data is extracted from policy PDF text, not from a live insurer API.
- If a user refreshes the page, the session context is cleared and the profile must be re-entered.
- Scanned (image-based) PDFs are not supported; only text-native PDFs are parsed correctly.