from openai import OpenAI
from app.models import SourceDocument, ExtractionResult, KeyFiguresList

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
                    "source text itself — do not simply repeat the query as typed. "
                    "Pay special attention to specific numbers — fees, percentages, dollar "
                    "amounts, raise limits, growth rates, valuations — and capture them "
                    "precisely in key_figures, even if they don't fit neatly into the "
                    "other fields. Only include figures that describe the company's own "
                    "actual business metrics (revenue, users, funding, pricing tiers, "
                    "growth rates, etc.) — do not include example prices, sample "
                    "transactions, demo UI content, or illustrative figures that a "
                    "company's marketing page might show for demonstration purposes. "
                    "If multiple sources mention the same fact (e.g. the same dollar figure "
                    "or statistic), include it only once in key_figures — do not repeat the "
                    "same fact reworded from different sources."
                    "Also note any competitors or direct alternatives "
                    "explicitly named in the source text."
                ),
            },
            {
                "role": "user",
                "content": f"Company: {company_name}\n\nSources:\n{combined_text}",
            },
        ],
        response_format=ExtractionResult,
    )

    extraction = completion.choices[0].message.parsed
    return _dedupe_key_figures(extraction)


def _dedupe_key_figures(extraction: ExtractionResult) -> ExtractionResult:
    """
    Merges duplicate or reworded-repeat facts within key_figures (common
    when multiple sources mention the same figure with different wording),
    and caps the result to the 5 most meaningful figures.
    """
    if len(extraction.key_figures) <= 1:
        return extraction

    completion = client.beta.chat.completions.parse(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You will be given a list of extracted facts about a company. "
                    "Some entries may be the same underlying fact stated with "
                    "different wording — merge those into a single entry using "
                    "the clearest phrasing. Do not remove genuinely distinct "
                    "facts, and do not add new ones. Return at most 5 entries "
                    "total — if there are more than 5 distinct facts after "
                    "merging, keep the 5 most significant or specific ones."
                ),
            },
            {
                "role": "user",
                "content": "\n".join(extraction.key_figures),
            },
        ],
        response_format=KeyFiguresList,
    )

    result = completion.choices[0].message.parsed
    if result:
        extraction.key_figures = result.key_figures

    return extraction
