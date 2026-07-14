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

## Demo case

The built-in HomeWiz lease example includes three planted errors and four supported claims:

- Wrong rent amount: `$2,850` instead of `$2,450` (`high`)
- Fabricated pet policy: output says pets are allowed with a deposit, source says no pets (`high`)
- Wrong parking count: two spots instead of one (`medium`)
- Correct passes: unit number, tenant, lease term, and security deposit

## How it works

1. The browser sends source context and AI agent output to `POST /api/check`.
2. FastAPI validates and bounds the request before calling the OpenAI Responses API.
3. GPT-5.6 extracts atomic factual claims and returns a typed `CheckResult`.
4. The frontend presents contradictions first, ordered by severity, followed by supported claims.

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
