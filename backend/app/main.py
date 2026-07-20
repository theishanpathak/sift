from dotenv import load_dotenv
load_dotenv()


from app.models import Snapshot, SnapshotRequest
from app.synthesis.synthesizer import synthesize_snapshot
from app.extraction.extractor import extract_facts
from app.ingestion.web_search import fetch_sources, dedupe_by_url
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Request, status, Header
from fastapi.responses import JSONResponse

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

import os

def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "detail": (
                "Whoa, slow down! I'm a solo dev running this on my own "
                "API credits. "
                "Come back in a bit, or reach out if you want to "
                "chat about the project."
            )
        },
    )
def get_real_client_ip(request: Request) -> str:
    """
    Render (and most hosting platforms) sit the app behind a reverse proxy,
    so request.client.host is the proxy's address, not the real visitor's.
    The real IP is passed in the X-Forwarded-For header instead.
    """
    forwarded = request.headers.get("x-forwarded-for")
    print(f"request.client.host = {request.client.host}, X-Forwarded-For = {forwarded}")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return get_remote_address(request)

limiter = Limiter(key_func=get_real_client_ip)

app = FastAPI(title="Sift")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)


app.add_middleware(
    CORSMiddleware,
    # reminder to change it to my frontend url before deployment
    allow_origins=["https://sift-7xp1.onrender.com"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_cache: dict[str, Snapshot] = {}

@app.post("/api/snapshot", response_model=Snapshot)
@limiter.limit("20/hour")
def get_snapshot(request: Request, body: SnapshotRequest) -> Snapshot:

    cache_key = body.query.lower()
    if cache_key in _cache:
        return _cache[cache_key]
    
    sources = fetch_sources(body.query)

    if not sources:
        raise HTTPException(
            status_code=404,
            detail=f"No information found for '{body.query}'. Try a more specific company name.",
        )

    try:
        extraction = extract_facts(body.query, sources)

        if (
            not extraction.description
            and not extraction.funding_mentions
            and not extraction.market_signals
        ):
            raise HTTPException(
                status_code=404,
                detail=f"No relevant information found for '{body.query}'. Try a more specific company name.",
            )

        if not extraction.founder_mentions:
            founder_sources = fetch_sources(f"{extraction.company_name} founders co-founder")
            sources = dedupe_by_url(sources + founder_sources)
            extraction = extract_facts(body.query, sources)

       

        snapshot = synthesize_snapshot(extraction)
    except HTTPException:
        raise
    except Exception as e:
        print(f"AI processing failed: {e}")
        raise HTTPException(
            status_code=502,
            detail="AI processing failed. Please try again.",
        ) from e

    if snapshot is None:
        raise HTTPException(
            status_code=502,
            detail="AI could not generate a snapshot from the available information.",
        )

    seen = set()
    snapshot_sources = []

    for s in sources:
        if s.url and s.url not in seen:
            snapshot_sources.append(s.url)
    snapshot.sources = snapshot_sources
    snapshot.key_figures = extraction.key_figures
    snapshot.competitors = extraction.competitors


    _cache[cache_key] = snapshot
    return snapshot

@app.get("/health")
def health():
    return {"status": "ok"}


CACHE_ADMIN_KEY = os.getenv("CACHE_ADMIN_KEY")

@app.delete("/cache", status_code=status.HTTP_204_NO_CONTENT)
def delete_cache(x_admin_key: str = Header(None)):
    if x_admin_key != CACHE_ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Not authorized.")
    _cache.clear()
    return