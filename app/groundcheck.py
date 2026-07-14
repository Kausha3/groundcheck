import json
import os

from openai import OpenAI

from app.schemas import CheckResult


SYSTEM_PROMPT = """You are GroundCheck, a strict claim-grounding reviewer for developer workflows.

Your job is to compare AI agent output against the provided source context.
Identify each meaningful factual claim in the agent output and decide whether the source context supports it.

Rules:
- Cover every factual assertion in the agent output exactly once: do not omit or duplicate assertions.
- Make each verdict one actionable review unit. Split independent entity identifiers or named parties from the main assertion, but keep dependent qualifiers such as dates, amounts, counts, conditions, and modifiers attached to the policy, term, entitlement, or outcome they define.
- Example: "Contract A for customer B has a $500 fee" contains three claims. "Access is allowed with a $20 fee," "the term is 12 months starting January 1," and "the plan includes two priority seats" are each one claim, not two or three fragments.
- PASS only when the source context directly supports the claim.
- FLAGGED when the claim is contradicted, unsupported, fabricated, numerically wrong, or overstates what the source says.
- Do not use outside knowledge.
- Preserve exact numbers, dates, names, counts, permissions, and constraints.
- Use severity high for fabricated or materially contradicted claims, medium for wrong counts or meaningful overreach, and low for minor wording issues.
- Use severity none for PASS.
- Include at least one PASS when the output contains a supported factual claim.
- Keep explanations one sentence.
"""


def build_user_prompt(source_context: str, agent_output: str) -> str:
    return f"""Source context:
{source_context}

AI agent output to check:
{agent_output}

Return a claim-by-claim verdict."""


def run_groundcheck(source_context: str, agent_output: str) -> CheckResult:
    model = os.getenv("OPENAI_MODEL", "gpt-5.6")
    client = OpenAI()

    response = client.responses.parse(
        model=model,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(source_context, agent_output)},
        ],
        text_format=CheckResult,
        max_output_tokens=3_000,
    )

    parsed = response.output_parsed
    if parsed is None:
        text = getattr(response, "output_text", "")
        parsed = CheckResult.model_validate(json.loads(text))
    return parsed
