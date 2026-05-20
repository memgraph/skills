---
name: memgraph-write-cypher
description: >-
  Write Cypher queries for Memgraph, including Memgraph-specific extensions like
  deep path traversals (BFS, DFS, WSP, ASP, KSP with filter/weight lambdas),
  text and vector search, parallel execution, and CALL subqueries. Use when the
  user asks to write, fix, or optimize a Cypher query for Memgraph, or asks
  about Cypher syntax differences between Memgraph and Neo4j.
compatibility: Any language with a Bolt-compatible driver. Memgraph instance required.
integrations:
  - memgraph-lab>=3.11
metadata:
  version: "0.0.1"
  author: memgraph
---

# Writing Cypher for Memgraph

Memgraph implements openCypher with several extensions. This skill covers
Memgraph-specific syntax and patterns that differ from standard Neo4j Cypher.

## Clauses quick reference

### Read

```cypher
MATCH (n:Person {name: "Alice"})-[:KNOWS]->(m) RETURN m;
MATCH (n:Person) WHERE n.age > 30 RETURN n ORDER BY n.age DESC LIMIT 10;
OPTIONAL MATCH (n)-[:LIVES_IN]->(c:City) RETURN n, c;
MATCH (n) RETURN DISTINCT n.name;
UNWIND [1, 2, 3] AS x RETURN x;
```

### Write

```cypher
CREATE (n:Person {name: "Alice", age: 30});
CREATE (a)-[:KNOWS {since: 2020}]->(b);
MERGE (n:Person {name: "Alice"}) ON CREATE SET n.created = timestamp() ON MATCH SET n.seen = timestamp();
SET n.age = 31;
SET n:Employee;
REMOVE n:Intern;
REMOVE n.temporary;
DELETE r;
DETACH DELETE n;
DROP GRAPH;
```

### Control

```cypher
WITH n ORDER BY n.name RETURN collect(n.name);
MATCH (a) RETURN a UNION MATCH (b) RETURN b;
FOREACH (x IN [1,2,3] | CREATE (:N {id: x}));
```

### Analysis

```cypher
EXPLAIN MATCH (n:Person) RETURN n;
PROFILE MATCH (n:Person {age: 42}) RETURN n;
```

## MATCH patterns

### Label matching

```cypher
MATCH (n:Person) RETURN n;
MATCH (n:Person:Employee) RETURN n;       -- ALL labels (AND)
MATCH (n:Country|Person) RETURN n;        -- ANY label (OR)
```

Label OR (`|`) cannot be used in `CREATE` or `MERGE`.

### Variable-length paths

```cypher
MATCH (a)-[*1..3]->(b) RETURN a, b;       -- 1 to 3 hops
MATCH (a)-[*2]->(b) RETURN a, b;           -- exactly 2 hops
MATCH p=(a)-[*]->(b) RETURN relationships(p);
```

## Deep path traversals (Memgraph-specific)

Built-in C++ traversal algorithms using relationship expansion syntax.

### BFS (unweighted shortest)

```cypher
MATCH p=(a {name: "A"})-[*BFS]->(b {name: "E"}) RETURN p;
MATCH p=(a)-[r:ROAD *BFS]->(b) RETURN p;
```

### DFS (all paths)

```cypher
MATCH p=(a {name: "A"})-[*]->(b {name: "E"}) RETURN p;
```

### Weighted shortest path (WSP)

```cypher
MATCH p=(a)-[*WSHORTEST (r, n | r.weight) total_weight]->(b) RETURN p, total_weight;
MATCH p=(a)-[*WSHORTEST (r, n | n.cost + coalesce(r.weight, 0)) total]->(b) RETURN p, total;
```

### All shortest paths (ASP)

```cypher
MATCH p=(a)-[*ALLSHORTEST (r, n | r.weight)]->(b) RETURN p;
```

### K shortest paths (KSP)

Source/target must be matched first, then passed via `WITH`:

```cypher
MATCH (a:Node {name: "A"}), (b:Node {name: "E"})
WITH a, b
MATCH p=(a)-[*KSHORTEST|3]->(b) RETURN p;
```

### Filter lambdas

2-argument `(r, n | predicate)` -- r is the relationship, n is the target node:

```cypher
MATCH p=(a)-[*BFS (r, n | r.eu_border = false AND n.drinks < 15)]->(b) RETURN p;
```

3-argument `(r, n, p | predicate)` -- p is the current path:

```cypher
MATCH p=(a)-[* (r, n, p | type(last(relationships(p))) != 'CloseTo')]->(b) RETURN p;
```

WSP/ASP with filter (4-argument adds w for current weight):

```cypher
MATCH p=(a)-[*WSHORTEST (r, n | r.weight) total (r, n, p, w | w < 1000)]->(b) RETURN p, total;
```

### Hop limits

```cypher
MATCH p=(a)-[*BFS ..5]->(b) RETURN p;        -- max 5 hops
MATCH p=(a)-[*WSHORTEST 4 (r, n | r.w)]->(b) RETURN p;
USING HOPS LIMIT 3 MATCH p=(a)-[*BFS]->(b) RETURN p;
```

## CALL subqueries

```cypher
MATCH (p:Person)
CALL {
  WITH p
  MATCH (p)-[:KNOWS]->(friend)
  RETURN count(friend) AS friendCount
}
RETURN p.name, friendCount;
```

Scoped import (v3.5+):

```cypher
CALL (p) {
  MATCH (p)-[:KNOWS]->(f) RETURN count(f) AS cnt
}
```

Batching writes:

```cypher
LOAD CSV FROM "file.csv" WITH HEADER AS row
CALL {
  WITH row
  CREATE (:Node {id: row.id})
} IN TRANSACTIONS OF 1000 ROWS;
```

## LOAD CSV / LOAD PARQUET

```cypher
LOAD CSV FROM "/path/file.csv" WITH HEADER AS row
CREATE (:Person {name: row.Name, age: toInteger(row.Age)});

LOAD CSV FROM "https://example.com/data.csv" WITH HEADER IGNORE BAD DELIMITER "|" AS row
CREATE (:Node {id: row.id});

LOAD PARQUET FROM "/path/file.parquet" AS row CREATE (:Node {val: row.value});
LOAD PARQUET FROM "s3://bucket/data.parquet" WITH CONFIG {
  aws_region: "us-east-1", aws_access_key: $key, aws_secret_key: $secret
} AS row CREATE (:Node {val: row.value});
```

CSV values are always strings -- cast with `toInteger()`, `toFloat()`, `date()`.

## Periodic commit

```cypher
USING PERIODIC COMMIT 1000
LOAD CSV FROM "/data.csv" WITH HEADER AS row
CREATE (:Node {id: row.id});
```

ACID only per batch. Avoid concurrent writes during periodic execution.

## Parameters

Use `$paramName` syntax (NOT curly braces):

```cypher
MATCH (n:Person {name: $name}) RETURN n;
MATCH (n) SET n.value = $newValue;
MATCH (n) RETURN n LIMIT $limit;
```

Label parameterization (v3.1+):

```cypher
MATCH (n:$label) RETURN n;
SET n:$labels;
```

Property map in CREATE only (not MATCH/MERGE):

```cypher
CREATE (n $propertyMap);
```

## Text search

```cypher
CREATE TEXT INDEX myIdx ON :Article;
CREATE TEXT INDEX myIdx ON :Article(title, body);
CREATE TEXT EDGE INDEX edgeIdx ON :CITES;

CALL text_search.search("myIdx", "data.title:GraphRAG") YIELD node, score RETURN node, score;
CALL text_search.search_all("myIdx", "GraphRAG") YIELD node RETURN node;
CALL text_search.regex_search("myIdx", "graph.*") YIELD node RETURN node;

DROP TEXT INDEX myIdx;
```

Property names in queries use `data.` prefix. Boolean operators: `AND`, `OR`, `NOT`.

## Vector search

```cypher
CREATE VECTOR INDEX vecIdx ON :Article(embedding)
  WITH CONFIG {"dimension": 256, "capacity": 10000, "metric": "cos"};

CALL vector_search.search("vecIdx", 10, [0.1, 0.2, ...]) YIELD node, distance, similarity
RETURN node, similarity ORDER BY similarity DESC;

SHOW VECTOR INDEX INFO;
DROP VECTOR INDEX vecIdx;
```

Metrics: `l2sq` (default), `cos`, `ip`, `pearson`, `haversine`, `hamming`, `jaccard`.

## Parallel execution (Enterprise)

```cypher
GRANT PARALLEL_EXECUTION TO user;
USING PARALLEL EXECUTION MATCH (n:Person) RETURN count(n);
USING PARALLEL EXECUTION 8 MATCH (n) WHERE n.age > 30 RETURN count(*);
```

Best for aggregation queries on scan operators. Requires `priority_queue` scheduler.

## Schema procedures

```cypher
SHOW SCHEMA INFO;
CALL schema.node_type_properties() YIELD nodeType, nodeLabels, propertyName, propertyTypes;
CALL schema.rel_type_properties() YIELD relType, propertyName, propertyTypes;
```

Requires `--schema-info-enabled=true`.

## TTL (Enterprise)

```cypher
ENABLE TTL EVERY "1h" AT "03:00:00";
CREATE (:TTL {ttl: timestamp(), name: "temp"});
STOP TTL;
DISABLE TTL;
```

Reserved label `TTL`, reserved property `ttl` (microseconds since epoch).

## Expressions

### String predicates

```cypher
WHERE n.name STARTS WITH "Al"
WHERE n.name ENDS WITH "son"
WHERE n.name CONTAINS "ice"
WHERE n.name =~ "^A.*e$"
```

### CASE

```cypher
RETURN CASE n.status WHEN "active" THEN "A" WHEN "inactive" THEN "I" ELSE "?" END;
RETURN CASE WHEN n.age < 18 THEN "minor" WHEN n.age >= 65 THEN "senior" ELSE "adult" END;
```

`exists()` cannot be used inside CASE.

### Pattern comprehension

```cypher
RETURN [(n)-->(m:Movie) WHERE m.year > 2000 | m.title] AS recentMovies;
```

### List comprehension

```cypher
RETURN [x IN range(1, 10) WHERE x % 2 = 0 | x * x] AS evenSquares;
```

### Existential subqueries

```cypher
WHERE EXISTS { MATCH (n)-[:KNOWS]->(:Person {city: "Berlin"}) }
WHERE NOT EXISTS { MATCH (n)-[:BLOCKED]->() }
```

## Query optimization

### Key operators in PROFILE output

| Operator | Meaning | Action |
|----------|---------|--------|
| `ScanAll` | Full scan | Add indexes |
| `ScanAllByLabel` | Label index | OK for label-only queries |
| `ScanAllByLabelProperties` | Label+property index | Best |
| `EdgeUniquenessFilter` | Cyphermorphism | Split MATCH if unwanted |
| `Cartesian` | Cartesian product | Ensure smaller set is left branch |

### Index hinting

```cypher
USING INDEX :Person(name)
MATCH (n:Person {name: "Alice"}) RETURN n;
```

### Analyze graph (run after data load)

```cypher
ANALYZE GRAPH;
ANALYZE GRAPH ON LABELS :Person, :City;
```

### Reduce roundtrip

Use `project(path)` to deduplicate nodes in path results:

```cypher
MATCH path=(a)-[*BFS]->(b) WITH project(path) AS subgraph RETURN subgraph;
```

Return only needed data:

```cypher
MATCH (n:Person) RETURN n.name, n.age;
```

### Efficient deletes (large graphs)

```cypher
USING PERIODIC COMMIT 10000 MATCH ()-[r]->() DELETE r;
USING PERIODIC COMMIT 10000 MATCH (n) DELETE n;
```

Never `MATCH (n) DETACH DELETE n` on >1M nodes (Delta memory spike).

## Key differences from Neo4j

| Feature | Neo4j | Memgraph |
|---------|-------|----------|
| Shortest path | `shortestPath(...)` | `-[*BFS]->` |
| K shortest | `SHORTEST k` | `-[*KSHORTEST\|k]->` |
| Fixed length | `--{2}--` | `-[*2]-` |
| NOT label | `WHERE NOT n:Label` | `WHERE NOT n:Label` (same since v3) |
| `elementId()` | Returns string | Use `id()` (integer) |
| COUNT/COLLECT subquery | Supported | Use `count()`/`collect()` aggregations |
| Type predicate | `val IS :: INTEGER` | `valueType(val) = "INTEGER"` |
| Index creation | Sometimes auto | Always manual (unless flag enabled) |
| Constraint naming | Stored | Parsed but not stored (warning) |

## Additional resources

- For the complete built-in function catalog, see [REFERENCE.md](references/REFERENCE.md)
