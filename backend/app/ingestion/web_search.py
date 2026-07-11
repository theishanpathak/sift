from app.models import SourceDocument
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

client = TavilyClient()


def fetch_sources(query: str) -> list[SourceDocument]:
    response = client.search(f"{query} startup company", max_results = 3)

    sources = []
    for result in response["results"]:
        sources.append(SourceDocument(
            source_name=result["title"],
            url=result["url"],
            raw_text=result["content"],
        ))
    return sources
    

