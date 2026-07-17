from openai import OpenAI
from app.models import ExtractionResult, Snapshot

client = OpenAI()
MODEL = "gpt-4o-mini"


def synthesize_snapshot(extraction: ExtractionResult) -> Snapshot:
    """
    Synthesis layer: second AI call in the pipeline. Takes the clean,
    structured ExtractionResult (never the raw source text) and produces
    the final polished Snapshot: a written summary, a market signal
    judgment, founder background, and reasoned risk flags.

    This is the layer where actual analytical judgment happens — risk
    flags should reflect reasoning over the facts, not just restate them.
    """
    completions = client.beta.chat.completions.parse(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an investment analyst writing a concise due diligence "
                    "snapshot for a startup, based only on the structured facts provided. "
                    "Write a clear 2-3 sentence summary of what the company does, "
                    "a one-sentence market signal assessment, drawing on market_signals, "
                    "key_figures, and funding_mentions together — strong quantitative "
                    "figures (e.g. large transaction volumes, user counts, growth rates) "
                    "are themselves a valid market signal even if market_signals is empty "
                    "(if none of these fields provide a real signal, say so plainly rather "
                    "than interpreting the absence as meaningful), a short founder "
                    "background paragraph (if no founder information is available, "
                    "explicitly say so rather than leaving this blank), and "
                    "2-3 specific risk flags an investor should be aware of, each rated "
                    "low, medium, or high severity. Then provide an overall_risk_rating "
                    "(low, medium, medium-high, or high) that synthesizes those risk "
                    "flags into one verdict. "
                    "Base every claim strictly on the provided facts — do not invent "
                    "details, funding numbers, or founder history not present in the "
                    "input. If information is missing, say so plainly rather than "
                    "guessing or leaving fields empty — except for funding_stage, which "
                    "should be left as null/None if no specific stage is disclosed, rather "
                    "than writing a placeholder like 'unknown' or 'undisclosed'."
                ),
            },
            {
                "role": "user",
                "content": extraction.model_dump_json(indent=2),
            },
        ],
        response_format=Snapshot,
    )

    return completions.choices[0].message.parsed
