# Memgraph Skills

A collection of Agent Skills for working with [Memgraph](https://memgraph.com) graph database, covering Cypher, data modeling, indexes, algorithms, query modules, visualization, and GraphRAG.

## Usage

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

### With Claude Code

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
| memgraph-indexes-and-constraints | Creating and managing indexes, constraints, enums, and ANALYZE GRAPH |
| memgraph-lab-write-gss | Writing Graph Style Script (GSS) for graph visualization in Memgraph Lab |
| memgraph-mgconsole-cli | Using the mgconsole CLI to connect, run queries, and configure output |
| memgraph-model-graph-data | Designing graph data models using Labeled Property Graph principles |
| memgraph-python-query-modules | Building custom query modules in Python using the mgp API |
| memgraph-run-mage-algorithms | Running MAGE graph algorithms: PageRank, community detection, centrality, embeddings, and 70+ modules |
| memgraph-rust-query-modules | Building custom query modules in Rust using the rsmgp-sys API |

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
