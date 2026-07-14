import json
import os
import time
from collections import defaultdict, deque
from pathlib import Path
from threading import Lock

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAIError

from app.groundcheck import run_groundcheck
from app.schemas import CheckRequest, CheckResponse


ROOT_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = ROOT_DIR / "app" / "static"
EXAMPLES_DIR = ROOT_DIR / "examples"
RATE_LIMIT_REQUESTS = 10
RATE_LIMIT_WINDOW_SECONDS = 10 * 60
request_history: defaultdict[str, deque[float]] = defaultdict(deque)
request_history_lock = Lock()

load_dotenv(ROOT_DIR / ".env.local")
load_dotenv(ROOT_DIR / ".env")

app = FastAPI(title="GroundCheck", version="0.1.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/demo")
def demo() -> dict[str, str]:
    examples = json.loads((EXAMPLES_DIR / "demo_cases.json").read_text(encoding="utf-8"))
    return examples[0]


@app.get("/api/examples")
def examples() -> list[dict[str, str]]:
    return json.loads((EXAMPLES_DIR / "demo_cases.json").read_text(encoding="utf-8"))


@app.get("/api/demo/{case_id}")
def demo_case(case_id: str) -> dict[str, str]:
    examples = json.loads((EXAMPLES_DIR / "demo_cases.json").read_text(encoding="utf-8"))
    for example in examples:
        if example["id"] == case_id:
            return example
    raise HTTPException(status_code=404, detail="Demo case not found")


def enforce_rate_limit(client_ip: str) -> None:
    now = time.monotonic()
    cutoff = now - RATE_LIMIT_WINDOW_SECONDS
    with request_history_lock:
        history = request_history[client_ip]
        while history and history[0] < cutoff:
            history.popleft()
        if len(history) >= RATE_LIMIT_REQUESTS:
            raise HTTPException(status_code=429, detail="Rate limit reached. Try again in a few minutes.")
        history.append(now)


@app.post("/api/check", response_model=CheckResponse)
def check_claims(payload: CheckRequest, request: Request) -> CheckResponse:
    forwarded_for = request.headers.get("x-forwarded-for", "")
    client_ip = forwarded_for.split(",", 1)[0].strip()
    if not client_ip:
        client_ip = request.client.host if request.client else "unknown"
    enforce_rate_limit(client_ip)

    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY is not configured. Add it to .env.local.",
        )

    try:
        result = run_groundcheck(payload.source_context, payload.agent_output)
    except OpenAIError as exc:
        raise HTTPException(status_code=502, detail=f"OpenAI API error: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"GroundCheck failed: {exc}") from exc

    return CheckResponse(
        model=os.getenv("OPENAI_MODEL", "gpt-5.6"),
        verdicts=result.verdicts,
        summary=result.summary,
    )
