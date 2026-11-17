# Trigger eval

Checks whether an agent loads the right Memgraph skill when a developer asks for something in their own words. A skill only helps if it loads, and today many requests are answered from memory without one.

Each prompt in `prompts.json` runs in Claude Code with this repo loaded as the `memgraph` plugin. The run starts in an empty folder with your own settings, plugins and MCP servers switched off. The plugin's docs MCP server is connected, but the Memgraph MCP server is left out because it needs a running Memgraph. Only the Skill tool is allowed. Other tool calls, including docs MCP searches, are refused and recorded, so nothing runs and no queries reach the docs MCP.

## Run it

Needs Python 3 (no packages) and Claude Code, signed in.

```bash
python3 evals/triggers/run.py                                    # all prompts, haiku + sonnet, 3 repeats
python3 evals/triggers/run.py --models haiku --repeats 1         # quick check
python3 evals/triggers/run.py --only slow-query,unique-email     # some prompts
```

Results go to `evals/triggers/results/<timestamp>/`: `runs.jsonl` (one line per run) and `summary.md`.

Run it before and after changing a skill's `description`. That text decides when a skill loads.

## Prompts

`expect` lists the skills that count as a correct load; any one of them is enough.

- `[]`: no Memgraph skill should load (a Python or Postgres question).
- `null`: no skill covers this yet. The run is reported, not scored, to show what agents do without one.

Write prompts the way developers ask, without the skill's name or feature names where possible: "this query is slow", not "create a label-property index".
