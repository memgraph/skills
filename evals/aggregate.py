"""Aggregation + on-disk writers for the eval workspace.

Produces the artifacts the methodology describes:
  - timing.json   (per run:  total_tokens, duration_ms)
  - grading.json  (per run:  assertion_results[] + summary.pass_rate)
  - benchmark.json (per iteration: with_skill vs without_skill means + deltas)
  - feedback.json  (per iteration: human-notes template, one key per eval)
"""

from __future__ import annotations

import json
import statistics
from dataclasses import dataclass
from pathlib import Path

from .grader import GradingResult


@dataclass(frozen=True)
class RunResult:
    """Outcome of running one arm (with_skill or without_skill) of one case."""

    output: str
    total_tokens: int
    duration_ms: int
    grading: GradingResult


def _write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def write_run_artifacts(arm_dir: Path, run: RunResult) -> None:
    """Write outputs/, timing.json and grading.json for one run arm."""
    outputs_dir = arm_dir / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    (outputs_dir / "response.txt").write_text(run.output, encoding="utf-8")

    _write_json(
        arm_dir / "timing.json",
        {"total_tokens": run.total_tokens, "duration_ms": run.duration_ms},
    )
    _write_json(arm_dir / "grading.json", run.grading.to_dict())


def _mean_std(values: list[float]) -> dict:
    if not values:
        return {"mean": 0.0, "stddev": 0.0}
    mean = statistics.fmean(values)
    stddev = statistics.pstdev(values) if len(values) > 1 else 0.0
    return {"mean": round(mean, 4), "stddev": round(stddev, 4)}


def _arm_summary(runs: list[RunResult]) -> dict:
    return {
        "pass_rate": _mean_std([r.grading.summary["pass_rate"] for r in runs]),
        "time_seconds": _mean_std([r.duration_ms / 1000.0 for r in runs]),
        "tokens": _mean_std([float(r.total_tokens) for r in runs]),
    }


def build_benchmark(
    *,
    skill_name: str,
    model: str,
    iteration: int,
    with_runs: list[RunResult],
    without_runs: list[RunResult],
    per_eval: list[dict],
) -> dict:
    """Assemble the iteration-level benchmark.json payload."""
    with_summary = _arm_summary(with_runs)
    without_summary = _arm_summary(without_runs) if without_runs else None

    benchmark: dict = {
        "skill_name": skill_name,
        "model": model,
        "iteration": iteration,
        "eval_count": len(with_runs),
        "run_summary": {"with_skill": with_summary},
        "per_eval": per_eval,
    }

    if without_summary is not None:
        benchmark["run_summary"]["without_skill"] = without_summary
        benchmark["run_summary"]["delta"] = {
            "pass_rate": round(
                with_summary["pass_rate"]["mean"]
                - without_summary["pass_rate"]["mean"],
                4,
            ),
            "time_seconds": round(
                with_summary["time_seconds"]["mean"]
                - without_summary["time_seconds"]["mean"],
                4,
            ),
            "tokens": round(
                with_summary["tokens"]["mean"] - without_summary["tokens"]["mean"], 4
            ),
        }
    return benchmark


def write_iteration_artifacts(
    iteration_dir: Path, *, benchmark: dict, eval_dir_names: list[str]
) -> None:
    """Write benchmark.json and a feedback.json template at the iteration level."""
    _write_json(iteration_dir / "benchmark.json", benchmark)

    # feedback.json is a human-review template: one empty note per eval. Don't
    # clobber notes a reviewer already filled in on a rerun into the same dir.
    feedback_path = iteration_dir / "feedback.json"
    existing: dict = {}
    if feedback_path.is_file():
        try:
            existing = json.loads(feedback_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {}
    feedback = {name: existing.get(name, "") for name in eval_dir_names}
    _write_json(feedback_path, feedback)
