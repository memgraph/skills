# Memgraph Agent Skills

A collection of [Agent Skills](https://agentskills.io) for working with [Memgraph](https://memgraph.com) graph database.

## What are Agent Skills?

Agent Skills are portable instruction sets that enhance AI coding agents with specialized knowledge. They follow the [Agent Skills specification](https://agentskills.io/specification) and can be used with compatible AI tools like Claude Code, Cursor, and others.

## Available Skills

| Skill | Description |
|-------|-------------|
| [memgraph-python-query-modules](memgraph-python-query-modules/) | Develop custom query modules in Python for Memgraph using the mgp API |
| [memgraph-cpp-query-modules](memgraph-cpp-query-modules/) | Develop custom query modules in C++ for Memgraph using the mgp.hpp API |
| [memgraph-rust-query-modules](memgraph-rust-query-modules/) | Develop custom query modules in Rust for Memgraph using rsmgp-sys |
| [memgraph-graph-rag](memgraph-graph-rag/) | Language-agnostic blueprint for GraphRAG with Memgraph and agent tooling |

## Usage

### With Claude Code

Add skills to your project by cloning this repository or copying individual skill directories:

```bash
# Clone the entire skills repository
git clone https://github.com/memgraph/skills.git .skills

# Or copy a specific skill
cp -r skills/memgraph-python-query-modules .skills/
```

### Skill Structure

Each skill follows the Agent Skills specification:

```
skill-name/
├── SKILL.md              # Main skill instructions (required)
└── references/           # Additional documentation (optional)
    └── REFERENCE.md      # Detailed API reference and examples
```

## Resources

- [Agent Skills Specification](https://agentskills.io/specification)
- [Memgraph Documentation](https://memgraph.com/docs)
- [Memgraph Python API](https://memgraph.com/docs/custom-query-modules/python/python-api)

