from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.ingestion.web_search import fetch_sources
from app.extraction.extractor import extract_facts
from app.synthesis.synthesizer import synthesize_snapshot

from app.models import Snapshot, SnapshotRequest


app = FastAPI(title="Sift")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # reminder to change it to my frontend url before deployment
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
        snapshot = synthesize_snapshot(extraction)
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
    
    return snapshot