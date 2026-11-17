"""Check which Memgraph skill an agent loads for realistic prompts.

Each prompt runs in Claude Code (`claude -p`) with this repo loaded as the
`memgraph` plugin, in an empty folder, with the user's own settings, plugins and
MCP servers switched off. Only the Skill tool is allowed, so the agent can't run
commands or change anything; other tool calls are refused and recorded.

    python3 evals/triggers/run.py                      # all prompts, haiku + sonnet, 3 repeats
    python3 evals/triggers/run.py --models haiku --repeats 1 --only slow-query

Results go to evals/triggers/results/<timestamp>/ (runs.jsonl, summary.md).
"""

import argparse
import concurrent.futures
import datetime
import json
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
PREFIX = "memgraph:"
# The plugin's docs MCP server. The Memgraph MCP server is left out: it needs a running Memgraph.
MCP = {"mcpServers": {"memgraph-docs": {"type": "http", "url": "https://mcp-docs.memgraph.com"}}}


def run_one(case, model, repeat, timeout):
    workdir = Path(tempfile.mkdtemp(prefix="trigger-eval-"))
    mcp_file = workdir.parent / f"{workdir.name}-mcp.json"
    mcp_file.write_text(json.dumps(MCP))
    cmd = [
        "claude", "-p", case["prompt"],
        "--model", model,
        "--plugin-dir", str(REPO),
        "--setting-sources", "project",
        "--strict-mcp-config", "--mcp-config", str(mcp_file),
        "--allowedTools", "Skill",
        "--output-format", "stream-json", "--verbose",
    ]
    record = {"id": case["id"], "model": model, "repeat": repeat, "skills": [], "tools": [], "error": None}
    try:
        out = subprocess.run(cmd, cwd=workdir, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=timeout).stdout
    except subprocess.TimeoutExpired as e:
        out = e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
        record["error"] = "timeout"
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
        mcp_file.unlink(missing_ok=True)

    for line in out.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "system" and event.get("subtype") == "init":
            loaded = [s for s in event.get("skills", []) if s.startswith(PREFIX)]
            if not loaded:
                record["error"] = "plugin skills not loaded"
        elif event.get("type") == "assistant":
            for block in event["message"].get("content", []):
                if block.get("type") != "tool_use":
                    continue
                if block["name"] == "Skill":
                    record["skills"].append(block["input"].get("skill", "").removeprefix(PREFIX))
                else:
                    record["tools"].append(block["name"])
        elif event.get("type") == "result":
            record["turns"] = event.get("num_turns")
            record["cost_usd"] = event.get("total_cost_usd")
    return record


def verdict(case, record):
    loaded = [s for s in record["skills"] if s.startswith("memgraph-")]
    if case["expect"] is None:
        return "gap"
    if case["expect"] == []:
        return "fail" if loaded else "pass"
    return "pass" if any(s in case["expect"] for s in loaded) else "fail"


def summarize(cases, records, models):
    by_case = {c["id"]: c for c in cases}
    lines = ["# Trigger eval", ""]

    def rate(rows):
        scored = [r for r in rows if r["verdict"] in ("pass", "fail")]
        return f"{sum(r['verdict'] == 'pass' for r in scored)}/{len(scored)}" if scored else "-"

    lines += ["## Overall", "", "| Model | Should load a skill | Should load none |", "| --- | --- | --- |"]
    for m in models:
        rows = [r for r in records if r["model"] == m]
        pos = [r for r in rows if by_case[r["id"]]["expect"]]
        neg = [r for r in rows if by_case[r["id"]]["expect"] == []]
        lines.append(f"| {m} | {rate(pos)} | {rate(neg)} |")

    lines += ["", "## By expected skill", "", "| Skill | " + " | ".join(models) + " |", "| --- |" + " --- |" * len(models)]
    skills = sorted({c["expect"][0] for c in cases if c["expect"]})
    for s in skills:
        cells = [rate([r for r in records if r["model"] == m and by_case[r["id"]]["expect"] and by_case[r["id"]]["expect"][0] == s]) for m in models]
        lines.append(f"| {s} | " + " | ".join(cells) + " |")

    lines += ["", "## By prompt", "", "| Prompt | Expected | Model | Pass | Loaded instead / other tools |", "| --- | --- | --- | --- | --- |"]
    grouped = defaultdict(list)
    for r in records:
        grouped[(r["id"], r["model"])].append(r)
    for c in cases:
        for m in models:
            rows = grouped.get((c["id"], m), [])
            if not rows:
                continue
            loaded = sorted({s for r in rows for s in r["skills"]})
            tools = sorted({t for r in rows for t in r["tools"]})
            errors = sorted({r["error"] for r in rows if r["error"]})
            expected = "none" if c["expect"] == [] else ("(no skill yet)" if c["expect"] is None else ", ".join(c["expect"]))
            other = ", ".join(loaded) or "no skill"
            if tools:
                other += f"; tools: {', '.join(tools)}"
            if errors:
                other += f"; errors: {', '.join(errors)}"
            lines.append(f"| {c['id']} | {expected} | {m} | {rate(rows) if c['expect'] is not None else '-'} | {other} |")

    cost = sum(r.get("cost_usd") or 0 for r in records)
    lines += ["", f"{len(records)} runs, ${cost:.2f} reported by Claude Code."]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--models", default="haiku,sonnet", help="comma-separated Claude Code model aliases")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--jobs", type=int, default=6, help="runs in parallel")
    parser.add_argument("--only", help="comma-separated prompt ids")
    parser.add_argument("--timeout", type=int, default=180, help="seconds per run")
    args = parser.parse_args()

    if not shutil.which("claude"):
        sys.exit("Claude Code (`claude`) is not on PATH.")
    cases = json.loads((HERE / "prompts.json").read_text())["prompts"]
    if args.only:
        wanted = set(args.only.split(","))
        cases = [c for c in cases if c["id"] in wanted]
    models = args.models.split(",")
    jobs = [(c, m, i) for c in cases for m in models for i in range(args.repeats)]

    out_dir = HERE / "results" / datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir.mkdir(parents=True)
    by_case = {c["id"]: c for c in cases}
    records = []
    with open(out_dir / "runs.jsonl", "w") as log, concurrent.futures.ThreadPoolExecutor(args.jobs) as pool:
        futures = [pool.submit(run_one, c, m, i, args.timeout) for c, m, i in jobs]
        for n, future in enumerate(concurrent.futures.as_completed(futures), 1):
            record = future.result()
            record["verdict"] = verdict(by_case[record["id"]], record)
            records.append(record)
            log.write(json.dumps(record) + "\n")
            log.flush()
            print(f"[{n}/{len(jobs)}] {record['id']} {record['model']}: {record['verdict']} {record['skills'] or ''}", file=sys.stderr)

    summary = summarize(cases, records, models)
    (out_dir / "summary.md").write_text(summary)
    print(summary)
    print(f"Results: {out_dir}", file=sys.stderr)


if __name__ == "__main__":
    main()
