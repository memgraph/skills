"""LLM judge: grade each assertion PASS/FAIL with concrete evidence.

One structured Anthropic call per assertion (per the methodology). The judge is
told to give NO benefit of the doubt: an assertion FAILS unless the output
clearly and fully satisfies it.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass

from .client import with_retry

# Structured-output schema for a single grading decision.
_GRADE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["status", "evidence"],
    "properties": {
        "status": {"type": "string", "enum": ["PASS", "FAIL"]},
        "evidence": {
            "type": "string",
            "description": "One or two sentences quoting or citing the specific part of the output that justifies the verdict.",
        },
    },
}

_JUDGE_SYSTEM = (
    "You are a strict evaluation judge. You are given a user prompt, a description "
    "of what a successful response looks like, the actual model output, and ONE "
    "assertion about that output. Decide whether the output clearly and fully "
    "satisfies the assertion.\n\n"
    "Rules:\n"
    "- Do NOT give the benefit of the doubt. If the output only partially, "
    "vaguely, or ambiguously satisfies the assertion, return FAIL.\n"
    "- Judge only the assertion in front of you, not overall quality.\n"
    "- Base your verdict solely on the actual output — not on what the model "
    "could have meant or might do next.\n"
    "- Cite concrete evidence from the output (quote the relevant fragment)."
)

_JSON_OBJ_RE = re.compile(r"\{.*\}", re.DOTALL)


@dataclass(frozen=True)
class AssertionResult:
    text: str
    passed: bool
    evidence: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class GradingResult:
    assertion_results: list[AssertionResult]

    @property
    def summary(self) -> dict:
        passed = sum(1 for a in self.assertion_results if a.passed)
        total = len(self.assertion_results)
        return {
            "passed": passed,
            "failed": total - passed,
            "total": total,
            "pass_rate": (passed / total) if total else 0.0,
        }

    def to_dict(self) -> dict:
        return {
            "assertion_results": [a.to_dict() for a in self.assertion_results],
            "summary": self.summary,
        }


def _extract_json(text: str) -> dict:
    """Parse a JSON object from the judge's response, tolerating stray prose."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = _JSON_OBJ_RE.search(text)
        if match:
            return json.loads(match.group(0))
        raise


def grade_assertion(
    client: object,
    model: str,
    *,
    prompt: str,
    expected_output: str,
    output: str,
    assertion: str,
) -> AssertionResult:
    """Grade a single assertion against one run's output."""
    user = (
        f"USER PROMPT:\n{prompt}\n\n"
        f"DESCRIPTION OF A SUCCESSFUL RESPONSE:\n{expected_output}\n\n"
        f"ACTUAL MODEL OUTPUT:\n{output if output.strip() else '(empty output)'}\n\n"
        f"ASSERTION TO CHECK:\n{assertion}\n\n"
        "Return your verdict as JSON."
    )

    def _call():
        return client.messages.create(  # type: ignore[attr-defined]
            model=model,
            max_tokens=512,
            system=_JUDGE_SYSTEM,
            messages=[{"role": "user", "content": user}],
            output_config={"format": {"type": "json_schema", "schema": _GRADE_SCHEMA}},
        )

    resp = with_retry(_call)
    text = next((b.text for b in resp.content if b.type == "text"), "")
    try:
        data = _extract_json(text)
        status = str(data.get("status", "")).upper()
        evidence = str(data.get("evidence", "")).strip()
        passed = status == "PASS"
        if status not in ("PASS", "FAIL"):
            # Malformed verdict — treat as FAIL (no benefit of the doubt).
            passed = False
            evidence = f"Unparseable judge verdict: {text[:200]!r}"
    except (json.JSONDecodeError, ValueError):
        passed = False
        evidence = f"Judge did not return valid JSON: {text[:200]!r}"

    return AssertionResult(text=assertion, passed=passed, evidence=evidence)


def grade_run(
    client: object,
    model: str,
    *,
    prompt: str,
    expected_output: str,
    output: str,
    assertions: list[str],
) -> GradingResult:
    """Grade every assertion for one run (one arm of one eval case)."""
    results = [
        grade_assertion(
            client,
            model,
            prompt=prompt,
            expected_output=expected_output,
            output=output,
            assertion=assertion,
        )
        for assertion in assertions
    ]
    return GradingResult(assertion_results=results)
