---
name: memgraph-run-mage-algorithms
description: >-
  Run MAGE (Memgraph Advanced Graph Extensions) graph algorithms from Cypher,
  including built-in deep path traversals (BFS, DFS, WSP, ASP, KSP), PageRank,
  community detection, centrality, node embeddings, LLM integration, and 70+
  algorithm modules. Use when the user asks to run a graph algorithm, find
  shortest paths, detect communities, compute centrality, generate embeddings,
  or call any MAGE procedure.
compatibility: Any language with a Bolt-compatible driver. Memgraph instance required.
integrations:
  - memgraph-lab>=3.11
metadata:
  version: "0.0.1"
  author: memgraph
---

# Running MAGE Graph Algorithms

MAGE is Memgraph's graph algorithm library. Algorithms are exposed as **query
modules** — each module has one or more **procedures** (via `CALL`) or
**functions** (via `RETURN`).

## Installation

MAGE is pre-installed in Docker images `memgraph/memgraph-mage` and
`memgraph/memgraph-platform`.

```shell
docker run -p 7687:7687 --name memgraph memgraph/memgraph-mage:3.2
```

For GPU algorithms, add `--gpus all` and use a `-cuda` image tag.

## CALL syntax

```cypher
CALL module.procedure(arg1, arg2, ...) YIELD col1, col2;
CALL module.procedure() YIELD *;
```

Rules:
- First parameter can optionally be a `Graph` from `project()` to run on a subgraph
- `YIELD` selects output columns; use `YIELD *` for all
- Can embed in larger queries: `MATCH ... CALL ... YIELD ... RETURN ...`
- Write procedures: `CALL` can only be followed by `YIELD` and/or `RETURN`
- Alias with `AS` if column names conflict with outer variables

## Functions vs procedures

```cypher
CALL pagerank.get() YIELD node, rank;              -- procedure
RETURN llm.complete("Summarize this.");             -- function
RETURN collections.sort([3, 1, 2]);                 -- function in expression
```

## Subgraph projection

Run algorithms on a subset of the graph using `project()`:

```cypher
MATCH p=(n:Person)-[r:KNOWS]->(m:Person)
WITH project(p) AS subgraph
CALL pagerank.get(subgraph) YIELD node, rank
RETURN node.name, rank ORDER BY rank DESC;
```

Alternative with explicit lists:

```cypher
MATCH (a)-[e]-(b)
WITH collect(a) AS nodes, collect(e) AS rels
CALL community_detection.get_subgraph(nodes, rels) YIELD node, community_id
RETURN node, community_id;
```

Projection cannot be used with built-in deep path traversal (BFS/DFS/WSP/ASP/KSP).

## Memory limits

Default: 100 MB per procedure.

```cypher
CALL module.procedure() PROCEDURE MEMORY LIMIT 500 MB YIELD *;
CALL module.procedure() PROCEDURE MEMORY UNLIMITED YIELD *;
```

## Discovering modules

```cypher
CALL mg.procedures() YIELD name, signature;
CALL mg.load_all();
CALL node2vec.help() YIELD name, value;
```

---

## Built-in deep path traversal (no MAGE required)

These use relationship expansion syntax directly in MATCH.

### BFS (unweighted shortest path)

```cypher
MATCH p=(a {name: "A"})-[*BFS]->(b {name: "E"}) RETURN p;
MATCH p=(a)-[r:ROAD *BFS]->(b) RETURN p;
```

### DFS (all paths)

```cypher
MATCH p=(a)-[*]->(b) RETURN p;
```

### Weighted shortest path (WSP)

```cypher
MATCH p=(a)-[*WSHORTEST (r, n | r.weight) total_weight]->(b)
RETURN p, total_weight;
```

Combined node + edge weight:

```cypher
MATCH p=(a)-[*WSHORTEST (r, n | n.cost + coalesce(r.weight, 0)) total]->(b)
RETURN p, total;
```

### All shortest paths (ASP)

```cypher
MATCH p=(a)-[*ALLSHORTEST (r, n | r.weight)]->(b) RETURN p;
```

### K shortest paths (KSP)

Must match source/target first, pass via `WITH`:

```cypher
MATCH (a:Node {name: "A"}), (b:Node {name: "E"})
WITH a, b
MATCH p=(a)-[*KSHORTEST|3]->(b) RETURN p;
```

### Filter lambdas

2-arg `(r, n | predicate)`:
```cypher
MATCH p=(a)-[*BFS (r, n | n.active = true AND r.weight < 10)]->(b) RETURN p;
```

3-arg `(r, n, p | predicate)` — p is the path so far:
```cypher
MATCH p=(a)-[* (r, n, p | type(last(relationships(p))) != "BLOCKED")]->(b) RETURN p;
```

4-arg WSP/ASP filter `(r, n, p, w | predicate)` — w is accumulated weight:
```cypher
MATCH p=(a)-[*WSHORTEST (r, n | r.w) total (r, n, p, w | w < 1000)]->(b) RETURN p, total;
```

### Hop limits

```cypher
MATCH p=(a)-[*BFS ..5]->(b) RETURN p;
USING HOPS LIMIT 3 MATCH p=(a)-[*BFS]->(b) RETURN p;
```

---

## Algorithm categories

For the complete module list with signatures, see [reference.md](reference.md).

### Centrality

| Module | Description |
|--------|-------------|
| `pagerank` | PageRank influence ranking |
| `betweenness_centrality` | Brandes betweenness |
| `degree_centrality` | In/out/undirected degree |
| `katz_centrality` | Katz influence |

### Community detection

| Module | Description |
|--------|-------------|
| `community_detection` | Louvain modularity maximization |
| `leiden_community_detection` | Leiden (improved Louvain) |
| `weakly_connected_components` | WCC |

### Path & traversal

| Module | Description |
|--------|-------------|
| Built-in BFS/DFS/WSP/ASP/KSP | Expansion syntax |
| `algo` | General traversal utilities |
| `path` | Path navigation/analysis |
| `cycles` | Cycle detection |
| `bridges` | Bridge edge detection |
| `biconnected_components` | Maximal biconnected subgraphs |

### Graph ML

| Module | Description |
|--------|-------------|
| `node2vec` | Node embeddings via biased random walks |
| `gnn_link_prediction` | GNN link prediction |
| `gnn_node_classification` | GNN node classification |
| `tgn` | Temporal Graph Networks |
| `embeddings` | Sentence embeddings (local or remote) |
| `knn` | K-nearest neighbors |

### Utilities

| Module | Description |
|--------|-------------|
| `collections` | List operations (sort, union, partition) |
| `map` | Map operations |
| `text` | String manipulation |
| `llm` | LLM completions via LiteLLM |
| `json_util` | JSON load from file/URL |
| `export_util` | Graph export (JSON) |
| `import_util` | Data import (JSON) |
| `periodic` | Periodic query execution |
| `uuid_generator` | UUID generation |
| `migrate` | MySQL/SQL Server/Oracle access |

### Dynamic/online (Enterprise)

| Module | Description |
|--------|-------------|
| `pagerank_online` | Streaming PageRank |
| `community_detection_online` | Streaming LabelRankT |
| `betweenness_centrality_online` | Streaming betweenness |
| `katz_centrality_online` | Streaming Katz |
| `node2vec_online` | Incremental node2vec |

### Integrations

| Module | Description |
|--------|-------------|
| `nxalg` | 70+ NetworkX algorithm wrappers |
| `igraphalg` | igraph wrappers |
| `cugraph` | NVIDIA GPU algorithms |

---

## Key algorithm examples

### PageRank

```cypher
CALL pagerank.get() YIELD node, rank;
CALL pagerank.get({max_iterations: 100, damping_factor: 0.85, stop_epsilon: 1e-5})
YIELD node, rank SET node.rank = rank;
```

Parameters: `max_iterations` (100), `damping_factor` (0.85), `stop_epsilon` (1e-5),
`num_of_threads` (1).

### Community detection (Louvain)

```cypher
CALL community_detection.get() YIELD node, community_id;
```

Parameters: `weight` ("weight"), `coloring` (false), `min_graph_shrink` (100000),
`community_alg_threshold` (0.000001), `num_of_threads` (half HW threads).

Weighted graphs require `--storage-properties-on-edges=true`.

### Leiden community detection

```cypher
CALL leiden_community_detection.get() YIELD node, community_id;
```

Parameters: `weight_property` ("weight"), `gamma` (1.0), `theta` (0.01),
`resolution_parameter` (0.01), `max_iterations` (inf).

### Betweenness centrality

```cypher
CALL betweenness_centrality.get() YIELD node, betweenness_centrality;
CALL betweenness_centrality.get(true, true) YIELD node, betweenness_centrality;
```

Parameters: `directed` (true), `normalized` (true), `threads` (half HW threads).

### Degree centrality

```cypher
CALL degree_centrality.get() YIELD node, degree;
CALL degree_centrality.get("in") YIELD node, degree;
```

Parameters: `type` ("undirected" | "in" | "out").

### Node2Vec embeddings

```cypher
CALL node2vec.set_embeddings(false, 2.0, 0.5, 4, 5, 128) YIELD nodes, embeddings;
MATCH (n) RETURN n.id, n.embedding;
```

Key parameters: `is_directed`, `p` (return param), `q` (in-out param),
`num_walks`, `walk_length`, `vector_size`.

Low `p` → structural equivalence (BFS-like). Low `q` → homophily (DFS-like).

### LLM completions

```cypher
RETURN llm.complete("Summarize: Memgraph is a graph database.");
RETURN llm.complete("Hello", {model: "ollama/llama2", api_base: "http://localhost:11434"});
```

Config: `model`, `api_base`, `system_prompt`. Uses LiteLLM (requires
`pip install litellm` + provider API keys).

With graph data:

```cypher
MATCH (n:Article)
WITH collect(n.title + ": " + n.abstract) AS texts
WITH reduce(s = "", t IN texts | s + t + "\n") AS combined
RETURN llm.complete(combined, {system_prompt: "Summarize in 2 sentences."});
```

---

## Online algorithm pattern (Enterprise)

1. Initialize with `set()`:
   ```cypher
   CALL pagerank_online.set(100, 0.2) YIELD node, rank;
   ```

2. Create a trigger with `update()`:
   ```cypher
   CREATE TRIGGER pagerankTrigger BEFORE COMMIT EXECUTE
   CALL pagerank_online.update(createdVertices, createdEdges, deletedVertices, deletedEdges)
   YIELD node, rank SET node.rank = rank;
   ```

3. Read cached results with `get()`:
   ```cypher
   CALL pagerank_online.get() YIELD node, rank;
   ```

4. Reset with `reset()`:
   ```cypher
   CALL pagerank_online.reset();
   ```

---

## Common patterns

### Run algorithm → write results to nodes

```cypher
CALL pagerank.get() YIELD node, rank SET node.rank = rank;
CALL community_detection.get() YIELD node, community_id SET node.community = community_id;
```

### Run on label-filtered subgraph

```cypher
MATCH p=(n:User)-[r:FOLLOWS]->(m:User)
WITH project(p) AS subgraph
CALL pagerank.get(subgraph) YIELD node, rank
RETURN node.name, rank ORDER BY rank DESC;
```

### Chain algorithm with further query

```cypher
CALL community_detection.get() YIELD node, community_id
WITH community_id, collect(node) AS members
WHERE size(members) > 5
RETURN community_id, size(members) AS size
ORDER BY size DESC;
```

### Decision tree

1. **Shortest path (unweighted)?** → BFS expansion: `-[*BFS]->`
2. **Shortest path (weighted)?** → WSP: `-[*WSHORTEST (r,n|r.w)]->`
3. **All equal shortest?** → ASP: `-[*ALLSHORTEST (r,n|r.w)]->`
4. **Top-K paths?** → KSP: `-[*KSHORTEST|K]->`
5. **Node importance?** → `pagerank.get()` or `betweenness_centrality.get()`
6. **Groups/clusters?** → `community_detection.get()` or `leiden_community_detection.get()`
7. **Node embeddings?** → `node2vec.set_embeddings()` or `embeddings.node_sentence()`
8. **Real-time updates?** → Enterprise `*_online` modules with triggers
9. **NetworkX algorithm?** → `nxalg.*` (70+ procedures; prefer native C++ for perf)
10. **LLM completion?** → `llm.complete()` function

## Additional resources

- For the complete module list with procedure signatures, see [REFERENCE.md](references/REFERENCE.md)
