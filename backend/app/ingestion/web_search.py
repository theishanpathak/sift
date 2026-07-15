from app.models import SourceDocument
from tavily import TavilyClient

client = TavilyClient()


def fetch_sources(query: str) -> list[SourceDocument]:
    """
    Ingestion layer: given a startup name (or URL), search the web and
    return a list of SourceDocuments containing raw text about it.

    No AI is involved here — this is pure retrieval. The "startup company"
    suffix biases Tavily's results toward business-relevant pages instead
    of unrelated namesakes or generic review sites.

    Returns an empty list if nothing is found; it's up to a later stage
    (extraction or the API layer) to decide whether that counts as an error.
    """
    response = client.search(f"{query} startup company", max_results = 3)

    sources = []
    for result in response["results"]:
        sources.append(SourceDocument(
            source_name=result["title"],
            url=result["url"],
            raw_text=result["content"],
        ))
    return sources
    

