import re

from tavily import TavilyClient
from urllib.parse import urlparse

from app.models import SourceDocument

client = TavilyClient()

def is_url(query: str) -> bool:
    """True if query looks like a URL (starts with http:// or https://)."""
    return query.strip().startswith(("http://", "https://"))

def _clean_text(text: str) -> str:
    """Strip markdown images and collapse extra blank lines."""
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def _normalize_url(url: str) -> str:
    """Normalize a URL for comparison purposes (dedup only, not for display)."""
    parsed = urlparse(url)
    netloc = parsed.netloc.replace("www.", "").lower()
    path = parsed.path.rstrip("/")
    return f"{netloc}{path}"

def _dedupe_by_url(sources: list[SourceDocument]) -> list[SourceDocument]:
    """Removes duplicate SourceDocuments by normalized URL, keeping the first occurrence."""
    seen = set()
    deduped = []
    for s in sources:
        key = _normalize_url(s.url)
        if key not in seen:
            seen.add(key)
            deduped.append(s)
    return deduped

def fetch_sources(query: str, min_score: float = 0.3) -> list[SourceDocument]:
    """
    Given a company name or URL, returns raw source text about the company.
    URLs get a direct page extract plus a supplementary search (using the
    page's title) for outside signal the homepage won't have on its own.
    """
    if is_url(query):
        direct = _fetch_from_url(query)

        if not direct:
            return []
        
        title = direct[0].source_name
        supplementary = _fetch_from_search(title, min_score=min_score, max_results=7)

        return _dedupe_by_url(direct + supplementary)
    
    return _fetch_from_search(query, min_score=min_score, max_results=5)



def _fetch_from_search(query: str, min_score: float = 0.3, max_results: int = 5) -> list[SourceDocument]:
    """Runs a Tavily search biased toward business results, filtered by relevance score."""
    search_query = f"{query} startup company"
    response = client.search(search_query, max_results=max_results)

    sources = []
    for result in response["results"]:
        if result["score"] < min_score:
            continue
        sources.append(SourceDocument(
            source_name=result["title"],
            url=result["url"],
            raw_text=result["content"],
        ))

    return sources


def _fetch_from_url(url: str) -> list[SourceDocument]:
    """Fetches a single page directly via Tavily's extract endpoint."""
    response = client.extract(urls=[url])

    sources = []
    for result in response.get("results", []):
        sources.append(SourceDocument(
            source_name=result.get("title", url),
            url=result.get("url", url),
            raw_text=_clean_text(result.get("raw_content", ""))
        ))

    return sources

   