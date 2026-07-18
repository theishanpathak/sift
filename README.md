# Sift

Sift takes a startup's name, website URL, or founder pitch and generates a structured, sourced due-diligence snapshot: company summary, market signal, funding stage, key figures, founders, competitors, and severity-rated risk flags.

Unlike a single prompt to a general-purpose assistant, Sift is built as a multi-stage pipeline with typed contracts between each stage, source-level citations, and active gap-filling — if founder information is missing after the first pass, it searches again before giving up.

## Live demo

- App: https://sift-7xp1.onrender.com
- API: https://sift-backend-50q1.onrender.com

Note: the backend is hosted on Render's free tier and is kept warm via a periodic health-check ping, but the very first request after a period of inactivity may still take longer than usual.

## How it works

```
Input (name / URL) → Ingestion → Extraction → Synthesis → API → Frontend
```

- **Ingestion** — fetches raw source text via Tavily search (for company names) or direct page extraction plus a supplementary search (for URLs), deduplicated and filtered by relevance score.
- **Extraction** — a structured-output LLM call (GPT-4o mini) turns raw, noisy source text into validated, typed facts: description, funding mentions, founder mentions, key figures, competitors. If a fact isn't present in the sources, it's left empty rather than guessed. A second pass deduplicates and caps key figures, since the same fact often appears reworded across multiple sources.
- **Retry on gaps** — if founder information comes back empty, a targeted follow-up search runs once before extraction is finalized.
- **Synthesis** — a second structured-output LLM call turns the clean, factual extraction into the final narrative snapshot: summary, market signal, founder background, and severity-rated risk flags with an overall risk rating.
- **API** — a FastAPI endpoint orchestrates the pipeline, with explicit handling for irrelevant queries (404), AI failures (502), and rate limiting (5 requests/hour per IP).

## Stack

- **Backend**: FastAPI, Pydantic, OpenAI (structured outputs), Tavily
- **Frontend**: React, Tailwind CSS
- **Deploy**: Render

## Design principles

- **No silent guessing.** Every prompt explicitly forbids inventing details. Missing data is represented as `null` or an explicit "not available" statement, never a plausible-sounding placeholder.
- **Every claim is sourced.** Snapshots include the URLs they were built from.
- **Gaps trigger action, not acceptance.** The pipeline checks its own output for a known-important gap (founder info) and searches again before finalizing.

## Known limitations

- Companies whose name also refers to a fund, program, or sub-brand (e.g. a company that also runs a startup accelerator under the same name) can produce mixed-up snapshots, since ingestion doesn't yet distinguish "about this company" from "published by this company about something else."
- No cross-source conflict detection yet — if two sources disagree on a fact, extraction currently includes both without flagging the disagreement in the UI.
- Free-tier hosting means the backend may take 30-60 seconds to respond after a period of inactivity (cold start).

## Deployment

Deployed on Render as two separate services from a `prod` branch (kept intentionally separate from `main` so active work doesn't auto-deploy):

- **Backend** — Render Web Service, root directory `backend`, running `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- **Frontend** — Render Static Site, root directory `frontend`, built with `npm run build`, publishing the `dist` directory.


## Local setup

**Backend**
```bash
cd backend
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
# add OPENAI_API_KEY and TAVILY_API_KEY to a .env file
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
# add VITE_API_URL=http://localhost:8000 to a .env file
npm run dev
```

## Author

Built by Ishan Pathak — [theishanpathak.com](https://theishanpathak.com)

## License

MIT

## What's next

- Cross-source conflict detection (surface disagreements instead of silently picking one source)
- Comparison view across multiple startups
- Saved lookup history
- Pitch deck (PDF) input