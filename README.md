# GroundCheck

GroundCheck helps developers catch AI agent output that looks right but is not grounded in the source context. It acts like a lightweight review gate for AI-assisted development workflows, surfacing unsupported claims before they end up in docs, tickets, reviews, or shipped code.

**Track:** Developer Tools

**Tagline:** GroundCheck: unit tests for AI agent output. Catches hallucinated claims before you ship them.

**Live demo:** https://groundcheck-zeta.vercel.app

## What it does

- Accepts source context and AI agent output.
- Asks GPT-5.6 to review every meaningful factual claim.
- Returns structured claim-by-claim verdicts: `PASS` or `FLAGGED`.
- Flags hallucinated, contradicted, unsupported, or overreaching claims with severity and confidence.
- Includes realistic lease, API specification, and product requirements test cases.
- Exports results as a text report or structured JSON.
- Treats source and agent text as untrusted data and visibly warns on instruction-like content.
- Requires exact source evidence before a claim is allowed to PASS.

## Demo case

The built-in HomeWiz lease example includes three planted errors and several supported claims:

- Wrong rent amount: `$2,850` instead of `$2,450` (`high`)
- Fabricated pet policy: output says pets are allowed with a deposit, source says no pets (`high`)
- Wrong parking count: two spots instead of one (`medium`)
- Correctly supported details include the unit number, tenant, lease term, and security deposit

## How it works

1. The browser sends source context and AI agent output to `POST /api/check`.
2. FastAPI validates and bounds the request before calling the OpenAI Responses API.
3. GPT-5.6 extracts atomic factual claims and returns a typed `CheckResult`.
4. The frontend presents contradictions first, ordered by severity, followed by supported claims.

## Guardrails

- The system contract explicitly rejects instructions, role impersonation, and delimiter attacks embedded in either input.
- Inputs are JSON-encoded as untrusted data instead of interpolated into prompt headings.
- Structured Pydantic output constrains every verdict to the expected fields and values.
- A server-side evidence check fails closed when a PASS lacks a verbatim excerpt from the source.
- Instruction-like content is surfaced in the interface without deleting or rewriting the evidence.
- Requests use bounded inputs and outputs, timeouts, retries, privacy-preserving safety identifiers, and `store=False`.
- Review responses use `Cache-Control: no-store`, and restrictive browser security headers block third-party scripts, framing, and cross-origin connections.

## Data handling

- Source context and agent output are transmitted to OpenAI for analysis.
- GroundCheck has no database and does not intentionally persist submissions.
- The Responses API request sets `store=False`; this does not override any retention OpenAI may require for security or legal reasons.
- API and unexpected-error responses are generic so provider details, request contents, and credentials are not reflected to the browser.
- The OpenAI API key remains server-side in ignored local environment files and sensitive deployment environment variables.
- The public demo is not intended for confidential, regulated, or personally identifiable information.

## Evaluations

Fast guardrail tests run without an API call:

```bash
python -m unittest discover -s tests -v
```

The live evaluation suite runs six human-labeled cases, including three prompt-injection attacks:

```bash
python evals/run_evals.py
```

Use `python evals/run_evals.py --case source-prompt-injection` to run one case. GitHub Actions runs unit tests on every push and exposes the live model suite as a manually triggered workflow so API spending remains intentional. The live workflow requires an `OPENAI_API_KEY` repository secret.

See the [latest evaluation summary](outputs/evaluation_report.md) for case-by-case coverage.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

## Deploy

The repository is connected to Vercel. Production uses `app.main:app` as the FastAPI entry point and requires `OPENAI_API_KEY` and `OPENAI_MODEL` as server-side environment variables.

## Environment

Create `.env.local`:

```bash
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-5.6
```

The API key remains server-side. Never place it in frontend code or commit `.env.local`.

## API

`POST /api/check`

```json
{
  "source_context": "source text",
  "agent_output": "agent text to verify"
}
```

Returns:

```json
{
  "model": "gpt-5.6",
  "warnings": [],
  "summary": "Short review summary",
  "verdicts": [
    {
      "claim": "The monthly rent is $2,850.",
      "status": "FLAGGED",
      "severity": "high",
      "confidence": 0.98,
      "explanation": "The source lists monthly rent as $2,450.",
      "source_quote": "Monthly rent: $2,450"
    }
  ]
}
```

## How Codex helped

Codex was used to turn the hackathon brief and product framing into a working full-stack MVP: project structure, FastAPI endpoint, OpenAI Responses API integration, frontend interaction loop, demo fixture, and README setup path.

## Current scope

GroundCheck is a proof of concept for source-grounded review, not a universal truth engine. It deliberately uses only the supplied context, and its claim decomposition and severity judgments are model-generated. The public demo applies input, output, and request limits to control API usage.
