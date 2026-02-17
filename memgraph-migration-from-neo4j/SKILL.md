---
name: memgraph-migration-from-neo4j
description: Guide migrating graph data from Neo4j to Memgraph using the migrate module and a single Cypher query. Use when user wants to migrate from Neo4j, switch to Memgraph, or transfer graph data without CSV export/import.
metadata:
  author: memgraph
  version: "0.0.1"
---

# Memgraph Migration from Neo4j

Migrate graph data from Neo4j to Memgraph using the built-in `migrate` module. Streams data directly—no CSV exports.

## When to Use

- User wants to migrate from Neo4j to Memgraph
- User asks how to transfer graph data between Neo4j and Memgraph
- User mentions Neo4j migration, data transfer, or switching databases
- User prefers direct streaming over CSV export/import

## Prerequisites

- Memgraph with MAGE (migrate module)
- Neo4j reachable via Bolt; Memgraph and Neo4j on different ports if same host

## Migration Workflow

1. **Create indices** — `:__MigrationNode__` and `:__MigrationNode__(__elementId__)`
2. **Migrate orphan nodes** (if any) — run orphan query before triplets
3. **Migrate triplets** — nodes + relationships via `CALL migrate.neo4j(...) YIELD row MERGE/CREATE`
4. **Clean up** — drop indices, remove `__MigrationNode__` label and `__elementId__` property
5. **Rebuild indices and constraints** — not migrated; add manually

## Key Notes

- Uses `elementId(n)` from Neo4j as stable ID for `MERGE`
- `__MigrationNode__` and `__elementId__` are temporary; remove after migration
- Indices and constraints must be recreated manually
- Direct streaming—no CSV; suitable for large graphs

## Additional Resources

- Full queries and partial migration examples: [references/REFERENCE.md](references/REFERENCE.md)
- [Memgraph docs](https://memgraph.com/docs/data-migration/migrate-from-neo4j/using-single-cypher-query)
