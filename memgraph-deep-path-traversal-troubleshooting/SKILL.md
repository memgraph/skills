---
name: memgraph-deep-path-traversal-troubleshooting
description: Troubleshoot Memgraph variable-length path queries and choose the right traversal algorithm. Use when user has slow path queries, uses [*] expansion, or asks about DFS, BFS, shortest path, or relationship expansion. Guides choosing *BFS over * when all paths are not needed.
metadata:
  author: memgraph
  version: "0.0.1"
---

# Memgraph Deep Path Traversal Troubleshooting

Guide path traversal choice in Memgraph to avoid unnecessarily expensive queries.

## When to Use

- User has slow queries with variable-length paths (`[*]`, `[*..5]`, etc.)
- User mentions DFS, BFS, shortest path, path finding, or relationship expansion
- User uses patterns like `(a)-[*]->(b)` or `(a)-[r *]->(b)`
- User asks how to speed up path traversal

## Critical Question: Do You Need All Paths?

**Always ask:** Does the user really need *all* paths between each (source, target) pair, or is one path per pair enough?

| Syntax | Algorithm | Returns | Cost |
|--------|-----------|---------|------|
| `(a)-[*]->(b)` | DFS | **All** paths between all (source, target) pairs | High — can timeout on larger graphs |
| `(a)-[*BFS]->(b)` | BFS | **One** path per (source, target) pair | Low — one shortest path per pair, not all |

DFS runs and returns all paths between all pairs. BFS returns one path per pair. If the user only needs one path per pair, recommend `*BFS` instead of `*`.

## Quick Reference

| Need | Use | Example |
|------|-----|---------|
| All paths between all (source,target) pairs | `[*]` (DFS) | `MATCH path=(a)-[*]->(b) RETURN path` |
| One path per (source,target) pair (unweighted) | `[*BFS]` | `MATCH path=(a)-[*BFS]->(b) RETURN path` |
| Shortest path by edge weight | `[*WSHORTEST]` | `MATCH path=(a)-[:R *WSHORTEST (r,n\|r.weight)]-(b) RETURN path` |
| All shortest paths (same weight) | `[*ALLSHORTEST]` | `MATCH path=(a)-[*ALLSHORTEST (r,n\|r.weight)]-(b) RETURN path` |
| K shortest paths | `[*KSHORTEST]` | `MATCH path=(a)-[*KSHORTEST\|5]->(b) RETURN path` |

## DFS (`*`) — Use With Caution

Variable-length `[*]` uses depth-first search and returns **every** path between all (source, target) pairs. Without length constraints it can traverse the entire graph.

**When DFS is appropriate:**
- Path existence check (any path = success)
- Enumerating all possible routes (e.g. route planning alternatives)
- Small or constrained graphs

**Mitigation if DFS is required:**
- Add length constraint: `[*..5]` or `[*3..5]`
- Filter by relationship type: `[:CloseTo *]`
- Use `USING HOPS LIMIT x` directive
- Consider whether `*BFS` or `*WSHORTEST` can satisfy the use case

## BFS (`*BFS`) — Preferred for One Path Per Pair

Use `*BFS` when the user needs one shortest path per (source, target) pair. For each pair, Memgraph returns one path and stops (does not enumerate all paths).

```cypher
MATCH path=(n {name: "A"})-[*BFS]->(m {name: "E"})
RETURN path;
```

## Constraining Expansion by Property Values

DFS, BFS, WSHORTEST, and ALLSHORTEST support a lambda filter to restrict which edges/nodes are traversed. **KSHORTEST does not support filter lambdas.**

### DFS and BFS

Filter is a lambda over `(r, n)` — relationship and node expanded to. Add `p` for current path: `(r, n, p | ...)`.

```cypher
// Filter: only expand over r.eu_border = false and n.drinks_USD < 15
MATCH path=(n {id: 0})-[* (r, n | r.eu_border = false AND n.drinks_USD < 15)]->(m {id: 8})
RETURN path;
```

```cypher
// BFS with same filter
MATCH path=(n {id: 0})-[*BFS (r, n | r.eu_border = false AND n.drinks_USD < 15)]-(m {id: 8})
RETURN path;
```

With path context (`p`): use `last(relationships(p))` to inspect how the current node was reached.

### WSHORTEST and ALLSHORTEST

Filter comes *after* the weight expression. Lambda can use `(r, n)` or `(r, n, p, w)` for path and current weight.

```cypher
// Weight from r.weight, filter: r.eu_border = false AND n.drinks_USD < 15
MATCH path=(n {id: 0})-[*WSHORTEST (r, n | r.weight) total_weight (r, n | r.eu_border = false AND n.drinks_USD < 15)]-(m {id: 46})
RETURN path, total_weight;
```

## Documentation

For full syntax (filtering, length bounds, property filters), see [Memgraph deep path traversal](https://memgraph.com/docs/advanced-algorithms/deep-path-traversal) and [constraining by property values](https://memgraph.com/docs/advanced-algorithms/deep-path-traversal#constraining-the-expansion-based-on-property-values-1).
