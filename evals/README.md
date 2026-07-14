# Skill evals

A harness for evaluating the quality of the Memgraph Agent Skills in this repo,
implementing the agentskills.io ["Evaluating skills"][method] methodology.

For each test case the harness runs a Claude model **twice** — once **with** the
skill injected as context and once **without** it (the baseline) — then uses an
LLM judge to grade every assertion PASS/FAIL. The skill's value is the *delta*
between the two arms.

`validate.yml` checks that a skill is *structurally* valid (frontmatter, naming).
These evals check whether the skill actually *helps the model* — a different
question, hence a separate workflow (`evals.yml`).

[method]: https://agentskills.io/skill-creation/evaluating-skills

## How it works

1. Each skill has its test cases in `skills/<skill>/evals/evals.json`.
2. The runner builds the WITH-skill system prompt from the skill's `SKILL.md`
   plus any `references/*.md`, and a neutral baseline prompt for the WITHOUT arm.
3. It calls the model once per arm per case, capturing the output, total tokens,
   and wall-clock duration.
4. The **judge** (`grader.py`) makes one structured call per assertion and
   returns `PASS`/`FAIL` with evidence. It is told to give **no benefit of the
   doubt** — an assertion fails unless the output clearly and fully satisfies it.
5. Results are aggregated into per-run and per-iteration JSON, plus a printed
   with-vs-without summary table.

Runs are written to a sibling `skills/<skill>-workspace/` (git-ignored):

```
skills/memgraph-cypher-syntax/
├── SKILL.md
└── evals/
    └── evals.json
skills/memgraph-cypher-syntax-workspace/
└── iteration-1/
    ├── eval-bfs-shortest-path/
    │   ├── with_skill/    { outputs/response.txt, timing.json, grading.json }
    │   └── without_skill/ { outputs/response.txt, timing.json, grading.json }
    ├── eval-weighted-shortest-path-lambda/  { with_skill/, without_skill/ }
    ├── eval-vector-index-and-search/        { with_skill/, without_skill/ }
    ├── benchmark.json
    └── feedback.json      (human-review notes — one empty entry per eval)
```

- `timing.json` — `{ "total_tokens": ..., "duration_ms": ... }`
- `grading.json` — `{ "assertion_results": [{text, passed, evidence}], "summary": {passed, failed, total, pass_rate} }`
- `benchmark.json` — with/without mean `pass_rate`, `time_seconds`, `tokens` (+ stddev) and the deltas
- `feedback.json` — a template for the human-review step (fill in per eval)

## Running locally

Requires `uv` (already used by this repo) and an Anthropic API key:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
uv sync

# one skill (auto-increments to the next iteration-N)
uv run python -m evals.run_evals --skill memgraph-cypher-syntax

# every skill that has an evals.json
uv run python -m evals.run_evals --all

# skip the baseline arm (faster / cheaper; loses the delta)
uv run python -m evals.run_evals --skill memgraph-cypher-syntax --no-baseline

# pin an iteration number, choose a model, or a custom output dir
uv run python -m evals.run_evals --skill memgraph-cypher-syntax \
    --iteration 2 --model claude-sonnet-5 --out ./eval-runs
```

Without `ANTHROPIC_API_KEY` the CLI exits with a clear error before making any
call. `--help` and `evals.json` validation work without a key.

### Options

| Flag | Meaning |
| --- | --- |
| `--skill <name>` / `--all` | One skill, or every skill with an `evals.json` (required, mutually exclusive) |
| `--iteration N` | Iteration number (default: auto-increment per skill workspace) |
| `--model <id>` | Model id (default `claude-sonnet-5`) |
| `--baseline` / `--no-baseline` | Run the WITHOUT-skill arm (default: on) |
| `--out <dir>` | Workspace base dir (default: `skills/<skill>-workspace`) |
| `--fail-under <rate>` | CI gate: exit non-zero if any skill's WITH-skill mean `pass_rate` < rate. Default: report-only (exit 0). |
| `--github-step-summary <path>` | Append a markdown delta table (used with `$GITHUB_STEP_SUMMARY`) |

## Writing `evals.json`

Start from [`evals/evals.template.json`](evals.template.json); the schema is in
[`evals/evals.schema.json`](evals.schema.json). A malformed file fails fast with
a specific error before any API calls.

Each case is: **(1)** a realistic prompt, **(2)** a plain-language description of
success (`expected_output`, shown only to the judge), optionally **(3)** input
`files`, and **(4)** concrete `assertions`.

```json
{
  "skill_name": "memgraph-cypher-syntax",
  "evals": [
    {
      "id": 1,
      "name": "bfs-shortest-path",
      "prompt": "In Memgraph, how do I find the shortest path between the node named \"A\" and the node named \"E\"?",
      "expected_output": "A Cypher query using Memgraph's -[*BFS]-> deep-path syntax, not Neo4j's shortestPath().",
      "files": [],
      "assertions": [
        "The query uses Memgraph's *BFS relationship-expansion syntax (e.g. -[*BFS]->).",
        "The query does NOT use Neo4j's shortestPath() function.",
        "The query binds and returns a path variable p."
      ]
    }
  ]
}
```

Field notes:

- **`id`** — unique within the file (string or integer).
- **`name`** — optional; becomes the run directory (`eval-<slug>`). Defaults to `eval-<id>`.
- **`prompt`** — exactly what a user would type; sent to the model verbatim.
- **`expected_output`** — guides the judge; **not** shown to the model under test.
- **`files`** — optional paths relative to the skill's `evals/` dir; their contents are appended to the prompt as context. Missing files are noted, not fatal.
- **`assertions`** — many small, independently checkable statements beat one broad one. Graded with no benefit of the doubt.

Ground assertions strictly in the skill's `SKILL.md` — don't assert behavior the
skill doesn't document.

## CI

`.github/workflows/evals.yml` runs on `workflow_dispatch` (pick a skill or
`all`, optional iteration) and on `pull_request`s touching `skills/**` or
`evals/**`. On a PR it evaluates only the changed skills that have an
`evals.json` (falling back to all skills when the harness itself changed). It
uploads the workspace as an artifact and appends the delta table to the job
summary. It needs the `ANTHROPIC_API_KEY` repository secret.

It is **report-only by default** — evals never fail the build. To turn it into a
quality gate, uncomment the `GATE="--fail-under 0.6"` line in the workflow's
"Run evals" step.

## The iterate loop

1. Run the evals; read failed assertions, `feedback.json`, and the run outputs.
2. Improve the `SKILL.md` (address root causes broadly — fewer, better
   instructions usually beat exhaustive rules).
3. Rerun into a new `iteration-N`.
4. Grade & aggregate (automatic).
5. Human-review `feedback.json`. Repeat until the delta plateaus or you're satisfied.
