# GroundCheck

## Tagline

Unit tests for AI agent output. Catch hallucinated claims before you ship them.

## Links

- Live project: https://groundcheck-zeta.vercel.app
- Source code: https://github.com/Kausha3/groundcheck

## Project description

AI agent output often fails in the most dangerous way: it looks polished, confident, and plausible while quietly changing a number, inventing a requirement, or overstating what a source says. GroundCheck adds a review gate before a human trusts that output.

A user provides the source context and the AI-generated output that claims to be based on it. GroundCheck uses GPT-5.6 to decompose the output into factual claims, compare each claim strictly against the supplied source, and return a structured verdict. Supported claims pass. Contradicted, fabricated, unsupported, or overstated claims are flagged with severity, confidence, an explanation, and the relevant source evidence.

The demo includes realistic examples from lease review, API documentation, and product requirements. In the lease case, an agent-generated summary inflates the monthly rent, fabricates a pet policy, and doubles the number of parking spots. GroundCheck catches all three while leaving the supported unit, tenant, lease-term, and security-deposit details unflagged.

GroundCheck was built with Codex as a full-stack FastAPI application using the OpenAI Responses API and GPT-5.6 structured outputs. Codex helped translate the product idea into the backend schema, grounding prompt, API integration, frontend workflow, test fixtures, validation, and deployment configuration.

Both inputs are treated as untrusted JSON data rather than instructions. GroundCheck detects instruction-like content, displays a warning, requires verbatim source evidence for every PASS, and fails closed when that evidence is missing. We tested those boundaries with source-side, output-side, and delimiter-style prompt injections.

GroundCheck does not store submissions in a database. Review requests set `store=False`, responses are marked `no-store`, the browser is restricted to same-origin scripts and connections, and provider errors are never reflected with request or credential details. The interface clearly discloses that submitted text is sent to OpenAI for analysis.

The automated evaluation suite currently passes six of six live GPT-5.6 cases alongside deterministic unit and API tests. The suite uses human-labeled expected claims and severities and exits nonzero on a grounding regression.

## What we learned

The hard part is not asking a model whether text is true. It is defining and testing a constrained review contract: use only supplied evidence, preserve exact numbers and permissions, resist instructions embedded in untrusted text, split compound statements into actionable claims, and return results that another developer tool can consume. Structured outputs made the result predictable enough to render, grade, sort, copy, and export programmatically.

## Built with

Codex, GPT-5.6, OpenAI Responses API, Python, FastAPI, Pydantic, HTML, CSS, and JavaScript.
