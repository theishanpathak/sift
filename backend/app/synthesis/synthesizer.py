from openai import OpenAI
from app.models import ExtractionResult, Snapshot

client = OpenAI()
MODEL = "gpt-4o-mini"

def synthesize_snapshot(extraction : ExtractionResult) -> Snapshot:
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
        messages= [
            {
                "role": "system",
                "content": (
                    "You are an investment analyst writing a concise due diligence "
                    "snapshot for a startup, based only on the structured facts provided. "
                    "Write a clear 2-3 sentence summary of what the company does, "
                    "a one-sentence market signal assessment, a short founder "
                    "background paragraph (if no founder information is available, "
                    "explicitly say so rather than leaving this blank), and "
                    "2-3 specific risk flags an investor should be aware of. "
                    "Base every claim strictly on the provided facts — do not invent "
                    "details, funding numbers, or founder history not present in the "
                    "input. If information is missing, say so plainly rather than "
                    "guessing or leaving fields empty."
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