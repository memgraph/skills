---
name: memgraph-performance-troubleshooting
description: Guide using EXPLAIN and PROFILE clauses to troubleshoot slow Memgraph Cypher queries. Use when debugging query performance, identifying bottlenecks, or deciding which indexes to add. Covers query plans, operator analysis, and index recommendations.
metadata:
  author: memgraph
  version: "0.0.1"
---

# Memgraph Performance Troubleshooting

Use EXPLAIN and PROFILE to understand and improve Cypher query performance in Memgraph.

## When to Use

- User asks about slow queries, query performance, or optimization in Memgraph
- User mentions EXPLAIN, PROFILE, query plan, or bottlenecks
- User wants to reason about which operators are expensive
- User needs to decide whether to add indexes

## Workflow: EXPLAIN First, Then PROFILE

### Step 1: EXPLAIN (no execution)

**Always run EXPLAIN first** — it does not execute the query, so it is safe for expensive queries.

```cypher
EXPLAIN MATCH (n:Person {age: 42}) RETURN n;
```

EXPLAIN returns the planned operators. Read the plan from **bottom to top**; execution flows from bottom (Once) upward to Produce.

### Step 2: PROFILE (executes query, shows metrics)

Use PROFILE when you need to see **which operator runs the heaviest** and to reason about bottlenecks.

```cypher
PROFILE MATCH (n:Person {age: 42}) RETURN n;
```

PROFILE executes the query and returns:
- **OPERATOR** — same as EXPLAIN
- **ACTUAL HITS** — how many times each operator was pulled; fewer is better
- **RELATIVE TIME** — % of time spent per operator (identifies bottleneck)
- **ABSOLUTE TIME** — wall time per operator

Focus on operators with high RELATIVE TIME or high ACTUAL HITS.

## ScanAll + Filter → Add an Index

If the plan shows **ScanAll** followed by **Filter**, the query likely scans all nodes and filters afterward. That is inefficient — add an index so Memgraph can use indexed lookups.

| Pattern | Fix |
|--------|-----|
| `ScanAll` + `Filter (n :Label)` | Label index: `CREATE INDEX ON :Label;` |
| `ScanAllByLabel` + `Filter {n.property}` | Label-property index: `CREATE INDEX ON :Label(property);` |
| `ScanAll` + `Filter {n.prop}` (no label) | Add a label to the query and create `CREATE INDEX ON :Label(property);` |

### Example: Before vs After Index

**Before index:**
```
|  * Produce {n}                 |
|  * Filter (n :Person), {n.prop} |
|  * ScanAllByLabel (n :Person)   |
|  * Once                         |
```

**After label-property index:**
```
CREATE INDEX ON :Person(prop);
```

```
|  * Produce {n}                                    |
|  * ScanAllByLabelProperties (n :Person {prop})    |
|  * Once                                           |
```

`ScanAllByLabelProperties` is more efficient than `ScanAllByLabel` + `Filter`.

## Quick Index Reference

| Need | Index |
|------|-------|
| Match by label only | `CREATE INDEX ON :Label;` |
| Match by label + property | `CREATE INDEX ON :Label(property);` |
| Multiple properties together | `CREATE INDEX ON :Label(prop1, prop2);` |

For more index types (composite, edge-type, point, etc.), see [Memgraph indexes docs](https://memgraph.com/docs/fundamentals/indexes).

## Other Useful Operators

| Operator | Meaning |
|----------|---------|
| `ScanAll` | Scans all nodes — expensive on large graphs |
| `ScanAllByLabel` | Uses label index — better than ScanAll |
| `ScanAllByLabelProperties` | Uses label-property index — best when filtering by property |
| `Filter` | Filters rows; if after a ScanAll/ScanAllByLabel, consider adding an index |

## After Adding Indexes

**Always run EXPLAIN or PROFILE first** — that gives direct feedback on plan and performance. Use `ANALYZE GRAPH;` as a last resort when Memgraph picks a suboptimal index among multiple label-property indexes. Run it once after creating indexes and loading data so Memgraph can use value-distribution statistics for better index selection.
