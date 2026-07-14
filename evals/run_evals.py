#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.groundcheck import detect_instruction_like_content, run_groundcheck  # noqa: E402


def normalize(value: str) -> str:
    value = re.sub(r"(?<=\d),(?=\d)", "", value)
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


def load_cases() -> list[dict]:
    cases = json.loads((ROOT_DIR / "evals" / "cases.json").read_text(encoding="utf-8"))
    demos = {
        item["id"]: item
        for item in json.loads(
            (ROOT_DIR / "examples" / "demo_cases.json").read_text(encoding="utf-8")
        )
    }
    for case in cases:
        demo_id = case.get("demo_case_id")
        if demo_id:
            case["source_context"] = demos[demo_id]["source_context"]
            case["agent_output"] = demos[demo_id]["agent_output"]
    return cases


def matches_expectation(verdict: dict, expected: dict) -> bool:
    if verdict["status"] != expected["status"]:
        return False
    if expected.get("severity") and verdict["severity"] != expected["severity"]:
        return False
    if expected.get("severity_any") and verdict["severity"] not in expected["severity_any"]:
        return False
    claim = normalize(verdict["claim"])
    return all(normalize(term) in claim for term in expected.get("contains", []))


def grade_case(case: dict, result: dict, warnings: list[str]) -> list[str]:
    failures = []
    verdicts = result["verdicts"]
    unused = set(range(len(verdicts)))

    for expected in case["expected_verdicts"]:
        match = next(
            (index for index in unused if matches_expectation(verdicts[index], expected)),
            None,
        )
        if match is None:
            failures.append(f"Missing expected verdict: {expected}")
        else:
            unused.remove(match)

    for status, expected_count in case.get("expected_counts", {}).items():
        actual_count = sum(verdict["status"] == status for verdict in verdicts)
        if actual_count != expected_count:
            failures.append(f"Expected {expected_count} {status}, received {actual_count}")

    warning_text = " ".join(warnings).casefold()
    for location in case.get("warning_locations", []):
        if location.casefold() not in warning_text:
            failures.append(f"Missing injection warning for {location}")

    claim_text = " ".join(verdict["claim"] for verdict in verdicts).casefold()
    for forbidden in case.get("forbidden_claim_terms", []):
        if forbidden.casefold() in claim_text:
            failures.append(f"Instruction was incorrectly treated as a claim: {forbidden}")

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Run GroundCheck live model evaluations.")
    parser.add_argument("--case", action="append", dest="case_ids", help="Run only a case ID.")
    parser.add_argument("--output", type=Path, help="Write the JSON report to this path.")
    args = parser.parse_args()

    load_dotenv(ROOT_DIR / ".env.local")
    load_dotenv(ROOT_DIR / ".env")
    selected = [
        case for case in load_cases() if not args.case_ids or case["id"] in args.case_ids
    ]
    if not selected:
        parser.error("No matching evaluation cases.")

    report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "model": os.getenv("OPENAI_MODEL", "gpt-5.6"),
        "cases": [],
    }
    failed = 0

    for case in selected:
        warnings = detect_instruction_like_content(case["source_context"], case["agent_output"])
        result = run_groundcheck(case["source_context"], case["agent_output"])
        result_data = result.model_dump()
        failures = grade_case(case, result_data, warnings)
        failed += bool(failures)
        report["cases"].append(
            {
                "id": case["id"],
                "passed": not failures,
                "failures": failures,
                "warnings": warnings,
                "result": result_data,
            }
        )
        status = "PASS" if not failures else "FAIL"
        print(f"{status} {case['id']} ({len(result.verdicts)} verdicts)")
        for failure in failures:
            print(f"  - {failure}")

    report["summary"] = {
        "passed": len(selected) - failed,
        "failed": failed,
        "total": len(selected),
    }
    output_path = args.output or ROOT_DIR / "evals" / "latest-report.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"\n{len(selected) - failed}/{len(selected)} cases passed")
    print(f"Report: {output_path}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
