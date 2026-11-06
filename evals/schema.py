"""Schema and validator for per-skill ``evals.json`` files.

The canonical JSON Schema lives in ``evals/evals.schema.json`` (for editor
tooling). This module keeps an in-code copy of the rules and a dependency-free
validator so a malformed ``evals.json`` fails fast with a clear message before
any API calls are made.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path


class EvalValidationError(ValueError):
    """Raised when an evals.json file does not conform to the schema."""


_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _slugify(text: str) -> str:
    slug = _SLUG_RE.sub("-", text.strip().lower()).strip("-")
    return slug or "case"


@dataclass(frozen=True)
class EvalCase:
    """A single test case: a realistic prompt + a description of success + checks."""

    id: str | int
    prompt: str
    expected_output: str
    assertions: list[str]
    name: str | None = None
    files: list[str] = field(default_factory=list)

    @property
    def dir_name(self) -> str:
        """Directory name for this case's runs, e.g. ``eval-deep-path-bfs``."""
        base = self.name if self.name else f"eval-{self.id}"
        slug = _slugify(base)
        return slug if slug.startswith("eval-") else f"eval-{slug}"


@dataclass(frozen=True)
class EvalsFile:
    """A parsed, validated ``evals.json`` for one skill."""

    skill_name: str
    evals: list[EvalCase]


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise EvalValidationError(msg)


def validate_evals(data: object) -> EvalsFile:
    """Validate a parsed evals.json document and return typed objects.

    Raises EvalValidationError on any structural problem.
    """
    _require(isinstance(data, dict), "top level must be a JSON object")
    assert isinstance(data, dict)

    skill_name = data.get("skill_name")
    _require(
        isinstance(skill_name, str) and bool(skill_name.strip()),
        "'skill_name' must be a non-empty string",
    )
    assert isinstance(skill_name, str)

    raw_evals = data.get("evals")
    _require(isinstance(raw_evals, list), "'evals' must be an array")
    assert isinstance(raw_evals, list)
    _require(len(raw_evals) > 0, "'evals' must contain at least one test case")

    cases: list[EvalCase] = []
    seen_ids: set[str] = set()
    seen_dirs: set[str] = set()

    for i, raw in enumerate(raw_evals):
        where = f"evals[{i}]"
        _require(isinstance(raw, dict), f"{where} must be an object")
        assert isinstance(raw, dict)

        _require("id" in raw, f"{where}: missing 'id'")
        cid = raw["id"]
        _require(
            isinstance(cid, (str, int)) and not isinstance(cid, bool),
            f"{where}.id must be a string or integer",
        )
        _require(str(cid) not in seen_ids, f"{where}.id '{cid}' is duplicated")
        seen_ids.add(str(cid))

        prompt = raw.get("prompt")
        _require(
            isinstance(prompt, str) and bool(prompt.strip()),
            f"{where}.prompt must be a non-empty string",
        )

        expected = raw.get("expected_output")
        _require(
            isinstance(expected, str) and bool(expected.strip()),
            f"{where}.expected_output must be a non-empty string",
        )

        assertions = raw.get("assertions")
        _require(
            isinstance(assertions, list) and len(assertions) > 0,
            f"{where}.assertions must be a non-empty array",
        )
        assert isinstance(assertions, list)
        for j, a in enumerate(assertions):
            _require(
                isinstance(a, str) and bool(a.strip()),
                f"{where}.assertions[{j}] must be a non-empty string",
            )

        name = raw.get("name")
        _require(
            name is None or (isinstance(name, str) and bool(name.strip())),
            f"{where}.name, if present, must be a non-empty string",
        )

        files = raw.get("files", [])
        _require(isinstance(files, list), f"{where}.files must be an array")
        assert isinstance(files, list)
        for j, f in enumerate(files):
            _require(
                isinstance(f, str) and bool(f.strip()),
                f"{where}.files[{j}] must be a non-empty string path",
            )

        case = EvalCase(
            id=cid,
            prompt=prompt,  # type: ignore[arg-type]
            expected_output=expected,  # type: ignore[arg-type]
            assertions=list(assertions),
            name=name,
            files=list(files),
        )
        _require(
            case.dir_name not in seen_dirs,
            f"{where}: run directory '{case.dir_name}' collides with another case; "
            "give the cases distinct 'name' or 'id' values",
        )
        seen_dirs.add(case.dir_name)
        cases.append(case)

    return EvalsFile(skill_name=skill_name, evals=cases)


def load_evals(path: Path) -> EvalsFile:
    """Read and validate an evals.json file at ``path``."""
    _require(path.is_file(), f"evals file not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise EvalValidationError(f"{path}: invalid JSON — {exc}") from exc
    return validate_evals(data)
