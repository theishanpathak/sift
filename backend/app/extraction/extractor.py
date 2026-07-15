from openai import OpenAI
from app.models import SourceDocument, ExtractionResult

client = OpenAI()


def extract_facts(company_name: str, sources: list[SourceDocument]) -> ExtractionResult:
    combined_text = "\n\n---\n\n".join(
        f"Source: {s.source_name}\n{s.raw_text}" for s in sources
    )

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a research analyst extracting facts about a startup "
                    "from raw web source text. Only extract facts specifically about "
                    f"the company '{company_name}'. Ignore unrelated companies, "
                    "third-party review site boilerplate, star ratings, and any "
                    "content not directly about this company. If a fact isn't "
                    "present in the sources, leave it blank or empty rather than guessing."
                ),
            },
            {
                "role": "user",
                "content": f"Company: {company_name}\n\nSources:\n{combined_text}",
            },
        ],
        response_format=ExtractionResult
    )

    return completion.choices[0].message.parsed