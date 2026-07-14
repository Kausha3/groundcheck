# GroundCheck

## Tagline

Unit tests for AI agent output. Catch hallucinated claims before you ship them.

## Links

- Live project: https://groundcheck-zeta.vercel.app
- Source code: https://github.com/Kausha3/groundcheck

## Project description

AI agent output often fails in the most dangerous way: it looks polished, confident, and plausible while quietly changing a number, inventing a requirement, or overstating what a source says. GroundCheck adds a review gate before a human trusts that output.

A user provides the source context and the AI-generated output that claims to be based on it. GroundCheck uses GPT-5.6 to decompose the output into factual claims, compare each claim strictly against the supplied source, and return a structured verdict. Supported claims pass. Contradicted, fabricated, unsupported, or overstated claims are flagged with severity, confidence, an explanation, and the relevant source evidence.

The demo includes realistic examples from lease review, API documentation, and product requirements. In the lease case, an agent-generated summary inflates the monthly rent, fabricates a pet policy, and doubles the number of parking spots. GroundCheck catches all three while correctly passing the unit number, tenant, lease term, and security deposit.

GroundCheck was built with Codex as a full-stack FastAPI application using the OpenAI Responses API and GPT-5.6 structured outputs. Codex helped translate the product idea into the backend schema, grounding prompt, API integration, frontend workflow, test fixtures, validation, and deployment configuration.

## What we learned

The hard part is not asking a model whether text is true. It is defining a constrained review contract: use only the supplied evidence, preserve exact numbers and permissions, split compound statements into atomic claims, and return results that another developer tool can consume. Structured outputs made the result predictable enough to render, sort, copy, and export programmatically.

## Built with

Codex, GPT-5.6, OpenAI Responses API, Python, FastAPI, Pydantic, HTML, CSS, and JavaScript.
