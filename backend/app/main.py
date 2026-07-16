from dotenv import load_dotenv
load_dotenv()


from app.models import Snapshot, SnapshotRequest
from app.synthesis.synthesizer import synthesize_snapshot
from app.extraction.extractor import extract_facts
from app.ingestion.web_search import fetch_sources
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException


app = FastAPI(title="Sift")

app.add_middleware(
    CORSMiddleware,
    # reminder to change it to my frontend url before deployment
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/snapshot", response_model=Snapshot)
def get_snapshot(request: SnapshotRequest) -> Snapshot:
    sources = fetch_sources(request.query)

    if not sources:
        raise HTTPException(
            status_code=404,
            detail=f"No information found for '{request.query}'. Try a more specific company name.",
        )

    try:
        extraction = extract_facts(request.query, sources)

        if (
            not extraction.description
            and not extraction.funding_mentions
            and not extraction.founder_mentions
            and not extraction.market_signals
        ):
            raise HTTPException(
                status_code=404,
                detail=f"No relevant information found for '{request.query}'. Try a more specific company name.",
            )

        snapshot = synthesize_snapshot(extraction)
    except HTTPException:
        raise
    except Exception as e:
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
    return snapshot
