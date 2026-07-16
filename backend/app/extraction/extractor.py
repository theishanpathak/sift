from openai import OpenAI
from app.models import SourceDocument, ExtractionResult

client = OpenAI()
MODEL = "gpt-4o-mini"


def extract_facts(company_name: str, sources: list[SourceDocument]) -> ExtractionResult:
    """
    Extraction layer: first AI call in the pipeline. Takes raw, possibly
    noisy source text and returns validated structured facts matching
    ExtractionResult.

    Uses OpenAI's structured outputs (.parse() with response_format=ExtractionResult)
    so the model's output is guaranteed to match our schema, no manual
    JSON parsing needed.
    """
    combined_text = "\n\n---\n\n".join(
        f"Source: {s.source_name}\n{s.raw_text}" for s in sources
    )

    completion = client.beta.chat.completions.parse(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a research analyst extracting facts about a startup "
                    "from raw web source text. Only extract facts specifically about "
                    f"the company '{company_name}'. Ignore unrelated companies, "
                    "third-party review site boilerplate, star ratings, and any "
                    "content not directly about this company. If a fact isn't "
                    "present in the sources, leave it blank or empty rather than guessing. "
                    "Determine the company's actual, correctly capitalized name from the "
                    "source text itself — do not simply repeat the query as typed."
                ),
            },
            {
                "role": "user",
                "content": f"Company: {company_name}\n\nSources:\n{combined_text}",
            },
        ],
        response_format=ExtractionResult,
    )

    return completion.choices[0].message.parsed
