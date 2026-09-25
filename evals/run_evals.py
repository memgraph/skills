"""CLI entrypoint for the skill-evaluation harness.

Usage (from the repo root):
    uv run python -m evals.run_evals --skill memgraph-cypher-syntax
    uv run python -m evals.run_evals --all --no-baseline
    uv run python -m evals.run_evals --all --fail-under 0.6   # CI gate (opt-in)

For each eval case the harness runs the model twice — WITH the skill injected into
the system prompt and WITHOUT it (the baseline) — captures output + tokens +
duration, LLM-grades every assertion, and aggregates a with-vs-without benchmark.
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from .aggregate import (
    RunResult,
    build_benchmark,
    write_iteration_artifacts,
    write_run_artifacts,
)
from .client import MissingAPIKeyError, build_client
from .grader import GradingResult, grade_run
from .schema import EvalCase, EvalsFile, EvalValidationError, load_evals

DEFAULT_MODEL = "claude-sonnet-5"

_BASELINE_SYSTEM = "You are a helpful assistant. Answer the user's request directly."

_ITER_RE = re.compile(r"^iteration-(\d+)$")


# --------------------------------------------------------------------------- #
# Repo layout helpers
# --------------------------------------------------------------------------- #
def repo_root() -> Path:
    """Repo root = parent of the evals/ package."""
    return Path(__file__).resolve().parent.parent


def skill_dir(root: Path, skill: str) -> Path:
    return root / "skills" / skill


def discover_skills(root: Path) -> list[str]:
    """Skills that have an evals/evals.json, sorted by name."""
    base = root / "skills"
    if not base.is_dir():
        return []
    found = [
        p.parent.parent.name
        for p in sorted(base.glob("*/evals/evals.json"))
        if p.is_file()
    ]
    return found


def next_iteration(workspace: Path) -> int:
    """Lowest unused iteration-N under a workspace (1-based)."""
    if not workspace.is_dir():
        return 1
    used = [
        int(m.group(1))
        for p in workspace.iterdir()
        if p.is_dir() and (m := _ITER_RE.match(p.name))
    ]
    return (max(used) + 1) if used else 1


# --------------------------------------------------------------------------- #
# Skill context
# --------------------------------------------------------------------------- #
def load_skill_context(sdir: Path) -> str:
    """Build the WITH-skill system prompt: SKILL.md + any references injected."""
    parts: list[str] = [
        "You are a helpful assistant. You have access to the following skill "
        "document. Use it to answer the user's request.",
        "",
        "<skill>",
    ]
    skill_md = sdir / "SKILL.md"
    if skill_md.is_file():
        parts.append(skill_md.read_text(encoding="utf-8"))

    # Inject optional references (missing references are simply skipped).
    ref_dir = sdir / "references"
    if ref_dir.is_dir():
        for ref in sorted(ref_dir.glob("*.md")):
            parts.append(f"\n<reference path=\"references/{ref.name}\">")
            parts.append(ref.read_text(encoding="utf-8"))
            parts.append("</reference>")
    parts.append("</skill>")
    return "\n".join(parts)


def build_user_prompt(case: EvalCase, evals_dir: Path) -> str:
    """Case prompt plus the contents of any referenced input files."""
    prompt = case.prompt
    file_blocks: list[str] = []
    for rel in case.files:
        fpath = (evals_dir / rel).resolve()
        if fpath.is_file():
            file_blocks.append(
                f"\n\n--- FILE: {rel} ---\n{fpath.read_text(encoding='utf-8')}"
            )
        else:
            file_blocks.append(f"\n\n--- FILE: {rel} (NOT FOUND) ---")
    return prompt + "".join(file_blocks)


# --------------------------------------------------------------------------- #
# Running one arm
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class _ArmOutput:
    text: str
    total_tokens: int
    duration_ms: int


def run_arm(client: object, model: str, *, system: str, user_prompt: str) -> _ArmOutput:
    """Run one model call and capture output text, token usage, and duration."""
    from .client import with_retry

    def _call():
        return client.messages.create(  # type: ignore[attr-defined]
            model=model,
            max_tokens=4096,
            system=system,
            messages=[{"role": "user", "content": user_prompt}],
        )

    start = time.monotonic()
    resp = with_retry(_call)
    duration_ms = int((time.monotonic() - start) * 1000)

    text = "".join(b.text for b in resp.content if b.type == "text")
    usage = resp.usage
    total_tokens = (
        (usage.input_tokens or 0)
        + (usage.output_tokens or 0)
        + (getattr(usage, "cache_creation_input_tokens", 0) or 0)
        + (getattr(usage, "cache_read_input_tokens", 0) or 0)
    )
    return _ArmOutput(text=text, total_tokens=total_tokens, duration_ms=duration_ms)


# --------------------------------------------------------------------------- #
# Running one skill
# --------------------------------------------------------------------------- #
@dataclass
class SkillSummary:
    skill_name: str
    iteration: int
    with_pass_rate: float
    without_pass_rate: float | None
    workspace: Path


def run_skill(
    client: object,
    *,
    root: Path,
    skill: str,
    model: str,
    baseline: bool,
    iteration: int | None,
    out: Path | None,
) -> SkillSummary:
    sdir = skill_dir(root, skill)
    evals_dir = sdir / "evals"
    evals_file: EvalsFile = load_evals(evals_dir / "evals.json")

    skill_system = load_skill_context(sdir)

    workspace = out if out is not None else sdir.parent / f"{skill}-workspace"
    iteration_n = iteration if iteration is not None else next_iteration(workspace)
    iteration_dir = workspace / f"iteration-{iteration_n}"

    print(f"\n=== {skill}  (iteration {iteration_n}, model {model}) ===")
    print(f"    workspace: {iteration_dir}")

    with_runs: list[RunResult] = []
    without_runs: list[RunResult] = []
    per_eval: list[dict] = []
    eval_dir_names: list[str] = []

    for case in evals_file.evals:
        eval_dir = iteration_dir / case.dir_name
        eval_dir_names.append(case.dir_name)
        user_prompt = build_user_prompt(case, evals_dir)
        print(f"  - {case.dir_name}: {len(case.assertions)} assertion(s)")

        # WITH skill
        w = run_arm(client, model, system=skill_system, user_prompt=user_prompt)
        w_grade: GradingResult = grade_run(
            client,
            model,
            prompt=case.prompt,
            expected_output=case.expected_output,
            output=w.text,
            assertions=case.assertions,
        )
        w_run = RunResult(w.text, w.total_tokens, w.duration_ms, w_grade)
        write_run_artifacts(eval_dir / "with_skill", w_run)
        with_runs.append(w_run)

        eval_entry: dict = {
            "name": case.dir_name,
            "with_skill": {
                "pass_rate": w_grade.summary["pass_rate"],
                "total_tokens": w.total_tokens,
                "duration_ms": w.duration_ms,
            },
        }

        # WITHOUT skill (baseline)
        if baseline:
            wo = run_arm(
                client, model, system=_BASELINE_SYSTEM, user_prompt=user_prompt
            )
            wo_grade = grade_run(
                client,
                model,
                prompt=case.prompt,
                expected_output=case.expected_output,
                output=wo.text,
                assertions=case.assertions,
            )
            wo_run = RunResult(wo.text, wo.total_tokens, wo.duration_ms, wo_grade)
            write_run_artifacts(eval_dir / "without_skill", wo_run)
            without_runs.append(wo_run)
            eval_entry["without_skill"] = {
                "pass_rate": wo_grade.summary["pass_rate"],
                "total_tokens": wo.total_tokens,
                "duration_ms": wo.duration_ms,
            }
            eval_entry["delta_pass_rate"] = round(
                w_grade.summary["pass_rate"] - wo_grade.summary["pass_rate"], 4
            )

        per_eval.append(eval_entry)

    benchmark = build_benchmark(
        skill_name=evals_file.skill_name,
        model=model,
        iteration=iteration_n,
        with_runs=with_runs,
        without_runs=without_runs,
        per_eval=per_eval,
    )
    write_iteration_artifacts(
        iteration_dir, benchmark=benchmark, eval_dir_names=eval_dir_names
    )

    rs = benchmark["run_summary"]
    return SkillSummary(
        skill_name=skill,
        iteration=iteration_n,
        with_pass_rate=rs["with_skill"]["pass_rate"]["mean"],
        without_pass_rate=(
            rs["without_skill"]["pass_rate"]["mean"] if baseline else None
        ),
        workspace=iteration_dir,
    )


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #
def print_summary_table(summaries: list[SkillSummary]) -> None:
    print("\n" + "=" * 72)
    print("SUMMARY  (pass rate: with skill vs without skill)")
    print("=" * 72)
    header = f"{'skill':<40}{'with':>8}{'without':>10}{'delta':>8}"
    print(header)
    print("-" * len(header))
    for s in summaries:
        without = "n/a" if s.without_pass_rate is None else f"{s.without_pass_rate:.2f}"
        delta = (
            "n/a"
            if s.without_pass_rate is None
            else f"{s.with_pass_rate - s.without_pass_rate:+.2f}"
        )
        print(f"{s.skill_name:<40}{s.with_pass_rate:>8.2f}{without:>10}{delta:>8}")
    print("=" * 72)


def write_step_summary(summaries: list[SkillSummary], path: Path) -> None:
    """Append a GitHub Actions job-summary markdown table (for $GITHUB_STEP_SUMMARY)."""
    lines = [
        "## Skill eval results",
        "",
        "| Skill | With skill | Without skill | Delta |",
        "| --- | ---: | ---: | ---: |",
    ]
    for s in summaries:
        without = "n/a" if s.without_pass_rate is None else f"{s.without_pass_rate:.2f}"
        delta = (
            "n/a"
            if s.without_pass_rate is None
            else f"{s.with_pass_rate - s.without_pass_rate:+.2f}"
        )
        lines.append(f"| {s.skill_name} | {s.with_pass_rate:.2f} | {without} | {delta} |")
    lines.append("")
    with path.open("a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="evals",
        description="Run the with/without-skill eval harness and grade assertions.",
    )
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--skill", help="Skill directory name, e.g. memgraph-cypher-syntax")
    group.add_argument(
        "--all", action="store_true", help="Run every skill that has an evals.json"
    )
    p.add_argument(
        "--iteration",
        type=int,
        default=None,
        help="Iteration number (default: auto-increment per skill workspace)",
    )
    p.add_argument("--model", default=DEFAULT_MODEL, help=f"Model id (default {DEFAULT_MODEL})")
    p.add_argument(
        "--baseline",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Run the WITHOUT-skill baseline arm (default: on). Use --no-baseline to skip.",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Workspace base dir (default: skills/<skill>-workspace next to each skill)",
    )
    p.add_argument(
        "--fail-under",
        type=float,
        default=None,
        metavar="RATE",
        help="CI gate: exit non-zero if any skill's with-skill mean pass_rate is below "
        "RATE (0..1). Default: report-only (always exit 0).",
    )
    p.add_argument(
        "--github-step-summary",
        type=Path,
        default=None,
        help="Path to append a markdown summary table (typically $GITHUB_STEP_SUMMARY).",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = repo_root()

    if args.all:
        skills = discover_skills(root)
        if not skills:
            print("No skills with evals/evals.json found under skills/.", file=sys.stderr)
            return 0
    else:
        skills = [args.skill]

    try:
        client = build_client()
    except MissingAPIKeyError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    summaries: list[SkillSummary] = []
    for skill in skills:
        try:
            summaries.append(
                run_skill(
                    client,
                    root=root,
                    skill=skill,
                    model=args.model,
                    baseline=args.baseline,
                    iteration=args.iteration,
                    out=args.out,
                )
            )
        except (EvalValidationError, FileNotFoundError) as exc:
            print(f"ERROR [{skill}]: {exc}", file=sys.stderr)
            return 2

    print_summary_table(summaries)
    if args.github_step_summary is not None:
        write_step_summary(summaries, args.github_step_summary)

    # Exit code / gating.
    if args.fail_under is not None:
        failing = [s for s in summaries if s.with_pass_rate < args.fail_under]
        if failing:
            names = ", ".join(f"{s.skill_name}={s.with_pass_rate:.2f}" for s in failing)
            print(
                f"\nFAIL: with-skill pass_rate below {args.fail_under:.2f} for: {names}",
                file=sys.stderr,
            )
            return 1
        print(f"\nPASS: all skills >= {args.fail_under:.2f} with-skill pass_rate.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
