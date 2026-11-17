# VakeelLink — Technical Interview Prep

Teach one concept at a time. Defend every file, function, API, and design decision.

**Order:** Project Overview → Folder Structure → Frontend → Backend → APIs → Database → AI/RAG → Authentication → Security → Deployment → Scalability → End-to-End Workflow → Mock Interview

---

# Concept 1 — Project Overview

*(Everything else hangs off this. Master the "elevator pitch" first.)*

---

## 1. What is it?

**VakeelLink** is an **AI-powered Indian legal research and consultation platform**. In product terms it combines:

| Product surface | What the user gets |
|-----------------|-------------------|
| **Legal RAG assistant** | Ask a legal question → get structured analysis + **citations** from case law/statutes |
| **Lawyer directory** | Browse/filter lawyers, view profiles, ratings |
| **Consultations + messaging** | Client books a lawyer; chat (HTTP + WebSocket fallbacks) |
| **Role-based portals** | Client dashboard, lawyer dashboard, admin routes |
| **Case tooling** | Case curator, search, statutes, archive (UI workflows around legal work) |

It is **not** a law firm product or a court filing system. It is a **research + matchmaking + lightweight CRM** prototype with a strong RAG core.

**One-line pitch (use this in interviews):**

> "VakeelLink is a full-stack legal tech app: React SPA talks to a FastAPI backend; authentication and relational data live in Supabase Postgres; legal answers are produced by a RAG pipeline (embeddings → vector retrieval → LLM with citation constraints), with Groq as primary LLM and Gemini as fallback."

---

## 2. Why does this project exist (problem → solution)?

### The problem (first principles)

Indian legal information is:

1. **Scattered** — judgments, acts, sections live across many sources
2. **Hard to search** — keyword search fails when the user describes a *situation* ("defective phone, seller refuses refund") instead of a *section number*
3. **High-stakes** — raw LLM answers without sources are dangerous (hallucinated sections, wrong case names)
4. **Action gap** — even a good answer doesn't connect the user to a real advocate

### The solution this architecture encodes

```
Natural-language legal problem
        │
        ▼
  Domain classification + embedding
        │
        ▼
  Vector retrieval (domain-specific collections)
        │
        ▼
  LLM constrained to retrieved context → citations
        │
        ▼
  Optional lawyer recommendations by domain
        │
        ▼
  Consultation booking / chat
```

So the product is intentionally a **pipeline**, not a single chatbot widget.

---

## 3. How does it work internally? (system mental model)

Think in **layers**, not folders:

```
┌─────────────────────────────────────────────────────────────┐
│  Browser (React 19 + Vite 8 + React Router + Tailwind CDN)  │
│  Auth token: localStorage `vakeellink_token`                │
│  API client: src/utils/api.js → Bearer + error envelopes    │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP / WS (Vite proxy /api → :8000)
┌───────────────────────────▼─────────────────────────────────┐
│  FastAPI (uvicorn) — app/main.py                            │
│  Routers: auth, users, lawyers, ai, cases, consultations…   │
│  Cross-cutting: CORS, SlowAPI rate limit, error handlers    │
└───────┬───────────────────┬───────────────────┬─────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
   Supabase            Qdrant / local       Groq → Gemini
   (Auth + Postgres)   vector store         (generation)
   profiles, lawyers,  MiniLM embeddings    JSON legal answer
   consultations…
```

### Request paths you should be able to draw on a whiteboard

| User action | Typical path |
|-------------|--------------|
| Sign up / log in | `POST /api/v1/auth/...` → Supabase Auth **or** local JSON store (`AUTH_PREFER_LOCAL`) |
| Ask legal AI | `POST /api/v1/query/ask` → `RagService` → retrieve → generate → citations |
| Browse lawyers | `GET /api/v1/lawyers` → Supabase `lawyers` table |
| Book consultation | consultations router → DB / local consultation store |
| Chat | messaging/chat routers + WebSockets with HTTP fallback |

### Dual-mode resilience (important for interviews)

This codebase is built for **hackathon + free-tier fragility**:

- **Auth:** Supabase preferred, but `AUTH_PREFER_LOCAL=true` can use `local_users.json`
- **Vectors:** Qdrant Cloud **or** local numpy corpus (`USE_LOCAL_VECTOR_STORE`)
- **LLM:** Groq primary, Gemini fallback, then **retrieval-only** answer if both LLMs fail

That "degraded but still useful" design is a strong interview talking point.

---

## 4. What alternatives exist, and why this stack?

| Concern | This project | Common alternatives | Why this was chosen (defensible story) |
|---------|--------------|---------------------|----------------------------------------|
| Frontend | React SPA + Vite | Next.js, Vue, Angular | Fast SPA for dashboards; Vite is standard for React tooling interviews |
| Backend | FastAPI | Django, Express, Nest | Async-friendly, auto OpenAPI (`/docs`), Pydantic validation, Python ML ecosystem |
| DB + Auth | Supabase (Postgres + Auth + RLS) | Firebase, custom JWT+Postgres, Auth0 | Managed auth + SQL + RLS without building full auth infrastructure |
| Vectors | Qdrant (+ local numpy) | Pinecone, Weaviate, pgvector | Strong open vector DB; free cloud; local fallback when free cluster dies |
| Embeddings | `all-MiniLM-L6-v2` | OpenAI embeddings, larger SBERT models | Small, free, local, 384-dim, good enough for domain-chunk retrieval |
| LLM | Groq Llama 3.3 70B → Gemini | OpenAI-only, Claude-only | Speed + free tier + multi-provider resilience |
| Deploy | Render free web + static frontend | AWS, Fly, Railway | Cheap prototype path; documented cold starts |

**Why not "just ChatGPT with a system prompt"?**  
Because **retrieval + citations** are the product differentiator. Without a corpus, you cannot defend answers in court-adjacent domains, and you cannot show `citations[]`, `cited_sections`, confidence, domain, etc.

---

## 5. Trade-offs and limitations (say these before the interviewer does)

Be honest — top companies reward this.

| Trade-off | Reality in this repo |
|-----------|----------------------|
| **Prototype vs production** | Local JSON stores, CDN Tailwind, free-tier services — great for demos, not multi-tenant SaaS |
| **Accuracy vs latency** | Loading MiniLM + vector search + 70B call is heavy; free Render may OOM on embeddings |
| **Legal risk** | Explicit disclaimer; outputs are **not legal advice** — still a compliance/ethics topic |
| **Role naming drift** | Schema uses `client`; frontend `ProtectedRoute` uses `user` for client dashboard — classic interview bug |
| **Ephemeral disk** | Local `backend/data/*.json` resets on redeploy |
| **Cold starts** | Free Render spins down; first request 30–60s |
| **CDN Tailwind** | Fast to ship; weaker for production purge/CSP/version pinning |
| **Single-worker uvicorn** | Simpler deploy; WebSockets/chat state is process-local |

---

## 6. How it fits the overall workflow

End-to-end product loop:

1. **Landing** → user signs up as client or lawyer
2. **AI assistant** → research with citations; domain inferred
3. **Recommended lawyers** (when DB available) by domain
4. **Directory / profile** → book consultation
5. **Consultations + chat** → human expert takes over
6. **History** (when logged in) → `query_history` / citations tables

Offline pipeline (data science side, scripts at repo root):

```
scrape / process corpus → generate_embeddings.py → upload_to_qdrant.py
                         → evaluate_retrieval.py / smoke_rag.py
```

The **app** serves answers; the **scripts** build the knowledge base. Interviewers love hearing that separation.

---

## 7. Production improvements (high-signal list)

If asked "what would you do next?":

1. **Unify roles** (`client` vs `user`) across FE and BE
2. **Managed Postgres only** — drop local JSON stores in production
3. **pgvector or always-on Qdrant** + embedding microservice (don't load torch in the API process)
4. **Proper Tailwind build** (PostCSS), not CDN
5. **Streaming answers** (SSE/WebSocket) for UX
6. **Citation grounding checks** (post-verify every cited section appears in retrieved chunks)
7. **Auth:** short-lived access tokens + refresh; HttpOnly cookies instead of raw localStorage JWT
8. **Observability:** structured logs, tracing per query, RAG eval metrics in CI
9. **Multi-worker / Redis** for rate limits and chat fan-out
10. **Human-in-the-loop** for high-stakes domains (criminal, family)

---

## 8. Interview questions (basic → advanced)

### Basic
1. In one minute, what does VakeelLink do and who is the user?
2. Name the main layers of the stack and one responsibility of each.
3. What is the difference between the **relational DB** and the **vector DB** here?
4. Why do legal answers need **citations**?

### Intermediate
5. Walk through what happens when a logged-in client submits a question on `/assistant`.
6. Why FastAPI instead of Django or Express for this product?
7. What does "degraded mode" mean in this architecture, and why design for it?
8. Why is MiniLM a reasonable embedding model choice for a student/hackathon system?

### Advanced (Microsoft / Google / Amazon style)
9. How would you prevent the LLM from inventing a section of the IPC that was never retrieved?
10. Free Render has 512 MB RAM and loads `sentence-transformers` in-process. What breaks, and how would you re-architect?
11. Compare storing chat in Postgres vs process memory vs Redis for horizontal scale.
12. How would you evaluate whether the RAG system is "good enough" before launch (metrics, datasets, online signals)?
13. Security: JWT in `localStorage` — risks and safer alternatives?
14. Design a multi-tenant version where firm A must never retrieve firm B's private documents.

---

## 9. Practice questions (answer in your own words)

**Q1 (elevator pitch)**  
Explain VakeelLink in ~60 seconds: problem, solution, stack, and one non-obvious design choice.

**Q2 (architecture)**  
Draw (in text) the path of:  
`User types "defective product refund" → citations appear on screen.`  
Name every major component that touches that request.

**Q3 (trade-offs)**  
Pick **two** limitations of this project and say how you'd fix them for a real product company.

**Q4 (why not simpler)**  
Why not put everything in one Next.js app with OpenAI only and no vector DB?

---

### After answering

- Score each answer (what interviewers liked / what was weak)
- Correct misconceptions
- Ask tight follow-ups
- Then move to **Concept 2: Folder Structure**
