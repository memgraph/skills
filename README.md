# Memgraph Skills

A collection of Agent Skills for working with [Memgraph](https://memgraph.com) graph database, covering Cypher, data modeling, indexes, algorithms, query modules, visualization, and GraphRAG.

## Install

### With Claude Code

```
/plugin marketplace add memgraph/marketplace
/plugin install memgraph@memgraph
```

### With Codex

```bash
codex plugin marketplace add memgraph/marketplace
codex plugin add memgraph@memgraph
```

The plugin also adds the Memgraph docs MCP server and the Memgraph MCP server. [memgraph/marketplace](https://github.com/memgraph/marketplace) is the catalog of all Memgraph plugins.

### With any agent (Cursor, Codex, Claude Code, and others)

```bash
npx skills add memgraph/skills
```

Add `--skill <name>` to install a single skill, or `--list` to see them all.

## Get started

With Docker running, ask your agent:

```
Get started with Memgraph
```

It runs the `memgraph-start` skill: it starts Memgraph and Memgraph Lab in Docker, loads a sample dataset you pick, and runs a first query and a graph algorithm. To call the skill directly, use `/memgraph:memgraph-start` in Claude Code or `$memgraph-start` in Codex. In Codex, start it with `codex -a on-request` so the agent can ask to run Docker outside its sandbox. To be asked less, answer the first `docker` and `curl` prompts with **Yes, and don't ask again for commands that start with …**, or choose **Approve for me** in `/permissions`, where Codex's reviewer approves low-risk commands for you.

## Manual install

### With Cursor

Clone the repo and symlink skills into one of the locations Cursor scans.

**Personal** (available across all your projects):

```bash
git clone https://github.com/memgraph/skills.git ~/.memgraph-skills
ln -s ~/.memgraph-skills/skills/* ~/.cursor/skills-cursor/
```

**Per-project** (available only in that project):

```bash
git clone https://github.com/memgraph/skills.git ~/.memgraph-skills
cd /path/to/your/project
ln -s ~/.memgraph-skills/skills .cursor/skills
```

### With Claude Code (manual)

Clone the repo and symlink skills into one of the locations Claude Code scans.

```bash
git clone https://github.com/memgraph/skills.git ~/.memgraph-skills
cd /path/to/your/project
ln -s ~/.memgraph-skills/skills .claude/skills
```

## Skills

Skills are contextual and auto-loaded based on your conversation. When a request matches a skill's triggers, the agent loads and applies the relevant skill.

| Skill | Useful for |
|-------|-----------|
| memgraph-brand-ui | Generating UIs, dashboards, diagrams, and visual artifacts in the Memgraph brand style |
| memgraph-cpp-query-modules | Building custom query modules in C++ using the mgp.hpp API |
| memgraph-cypher-syntax | Writing, fixing, and optimizing Cypher queries for Memgraph, including BFS/DFS/WSP lambdas, text and vector search |
| memgraph-database-configuration | Configuring triggers, transactions, isolation levels, storage modes, snapshots, WAL, and memory |
| memgraph-graph-rag | Building GraphRAG systems with Memgraph: schema design, ingestion, hybrid retrieval, and agent tool contracts |
| memgraph-import-data | Loading and migrating data into Memgraph from CSV, Parquet, JSON, CYPHERL, relational databases and Neo4j; indexes, storage mode, batching and verification |
| memgraph-indexes-and-constraints | Creating and managing indexes, constraints, enums, and ANALYZE GRAPH |
| memgraph-lab-write-gss | Writing Graph Style Script (GSS) for graph visualization in Memgraph Lab |
| memgraph-mgconsole-cli | Using the mgconsole CLI to connect, run queries, and configure output |
| memgraph-model-graph-data | Designing graph data models using Labeled Property Graph principles |
| memgraph-python-query-modules | Building custom query modules in Python using the mgp API |
| memgraph-run-mage-algorithms | Running MAGE graph algorithms: PageRank, community detection, centrality, embeddings, and 70+ modules |
| memgraph-rust-query-modules | Building custom query modules in Rust using the rsmgp-sys API |
| memgraph-start | Getting started: running Memgraph and Lab in Docker, loading a sample dataset, and a first query and graph algorithm |

## Skill Structure

Each skill follows the [Agent Skills specification](https://agentskills.io/specification):

```
skill-name/
├── SKILL.md              # Main skill instructions (required)
└── references/           # Additional documentation (optional)
    └── REFERENCE.md      # Detailed API reference and examples
```

## Validation

Skills are validated against the [Agent Skills specification](https://agentskills.io/specification#validation):

```bash
uv sync
uv run skills-ref validate skills/<skill-directory>
```

## Resources

- [Agent Skills Specification](https://agentskills.io/specification)
- [Memgraph Documentation](https://memgraph.com/docs)
