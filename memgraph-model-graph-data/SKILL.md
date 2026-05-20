---
name: memgraph-model-graph-data
description: >-
  Design graph data models for Memgraph using Labeled Property Graph (LPG)
  principles. Use when the user asks how to model data as a graph, design a
  schema, decide between properties and relationships, structure nodes and edges,
  import CSV/Parquet into a graph, build a knowledge graph, or optimize a
  Memgraph data model for performance and memory.
compatibility: Any language with a Bolt-compatible driver. Memgraph instance required.
integrations:
  - memgraph-lab>=3.11
metadata:
  version: "0.0.1"
  author: memgraph
---

# Graph Data Modeling for Memgraph

Memgraph uses the Labeled Property Graph (LPG) model: nodes and relationships
both carry properties (key-value pairs), and nodes can have multiple labels.

## Core concepts

### Four components

1. **Nodes** — entities with zero or more labels
2. **Relationships** — directed edges with exactly one type (immutable after creation)
3. **Properties** — key-value pairs on nodes and/or relationships
4. **Labels** — classify nodes; enable indexed lookups

```cypher
(:Person:Student {name: "Alice", age: 20})-[:STUDIES {grade: "A"}]->(:Subject {name: "Math"})
```

### Key properties of LPG

- Flexible, dynamic schema — add labels/properties anytime without migrations
- Relationships are first-class (not inferred via JOINs)
- Optimized for multi-hop traversals
- In-memory storage means property types directly affect RAM

---

## Design methodology

### Step 1: Define requirements

Write down what the database is for — use case drives the model. Ask:
- What entities exist?
- How do entities relate to each other?
- What questions will the graph answer?
- What properties are needed, and where should they live?

### Step 2: Identify nodes and relationships

**Nouns become nodes.** Group similar entities under labels.
**Verbs become relationships.** Name them as actions: `KNOWS`, `WORKS_ON`, `BELONGS_TO`.

### Step 3: Place properties strategically

| Data describes... | Store as... |
|-------------------|-------------|
| The entity itself | Node property |
| The connection | Relationship property |
| A shared category/concept | Separate node + relationship |

### Step 4: Validate with real queries

Write the queries you'll actually run. Use `PROFILE` to check the query plan.
If a query is slow or awkward, revisit the model.

---

## Property vs relationship — decision framework

### Use a property when

- The value is unique/specific to that node
- It's rarely used to find related entities
- It doesn't represent a shared concept

```cypher
(:Product {name: "Milk", price: 2.99, expirationDate: "2024-01-01"})
```

### Use a relationship when

- The data connects entities and can be shared across nodes
- You frequently query "which other nodes share this value?"

Anti-pattern — categories as array property:

```cypher
(:Product {name: "Milk", categories: ["Dairy", "Organic"]})
```

This forces scanning every node's array to find shared categories.

Pattern — categories as nodes:

```cypher
(:Product {name: "Milk"})-[:BELONGS_TO]->(:Category {name: "Dairy"})
(:Product {name: "Milk"})-[:BELONGS_TO]->(:Category {name: "Organic"})
```

Query for related products:

```cypher
MATCH (:Product {name: "Milk"})-[:BELONGS_TO]->(c)<-[:BELONGS_TO]-(other:Product)
RETURN other.name;
```

### Supernode warning

When a shared-value node accumulates too many relationships (e.g., a `Country`
node connected to millions of `Person` nodes), it becomes a **supernode** —
traversals through it are expensive. Strategies:
- Keep high-cardinality shared data as properties when traversal isn't needed
- Partition supernodes (e.g., `Country` + `Region` hierarchy)

---

## Anti-patterns and patterns

| Anti-pattern | Better pattern |
|--------------|----------------|
| Model every detail as nodes/relationships | Focus on key entities and direct relationships |
| Duplicate entity data on multiple nodes | Single canonical node + relationships |
| Categories/tags as array properties | Category/tag nodes with typed relationships |
| String dates and numbers | Temporal types (`date()`, `datetime()`) and `toInteger()` |
| No indexes on frequently queried properties | Targeted label and label-property indexes |
| Index every property | Index only hot query fields |
| SQL-style JOIN thinking | Traversal-first Cypher |
| Knowledge encoded only in query strings | Encode semantics in graph structure |
| `CREATE` for bulk relationship import | `MERGE` + indexes + `LIMIT` |
| Unconstrained cartesian `MATCH (a), (b)` | Filtered MATCH with indexes and limits |
| Design without profiling | `PROFILE` real queries during modeling |

---

## Knowledge graph modeling

A knowledge graph encodes domain knowledge in the graph structure so the graph
itself is "readable as sentences."

### Evolution example

Weak model — skills stored as property arrays:

```cypher
MATCH (p:Person)-[:WORKS_ON]->(t:Task)
WHERE all(skill IN t.Skills WHERE skill IN p.Skills)
RETURN *;
```

Knowledge is in the query, not the graph.

Strong model — skills as nodes with semantic relationships:

```cypher
(:Person)-[:HAS]->(:Skill)
(:Task)-[:NEEDS]->(:Skill)
(:Person)-[:WORKS_ON]->(:Task)
```

Find sufficient skills:

```cypher
MATCH (p:Person)-[:HAS]->(s:Skill)<-[:NEEDS]-(t:Task)
WHERE exists((p)-[:WORKS_ON]->(t))
RETURN p.name, collect(s.name);
```

Find skill gaps:

```cypher
MATCH (p:Project)-[:REQUIRES]->(s:Skill)
OPTIONAL MATCH (person:Person)-[:HAS]->(s)
WITH p, s, collect(person) AS people
WHERE size(people) = 0
RETURN p.name AS project, collect(s.name) AS missingSkills;
```

### GraphRAG integration

1. Embed a question → vector search → find a **pivot node**
2. Expand from pivot (e.g., 2-hop neighborhood):
   ```cypher
   MATCH path=(pivot:Project {name: "Data Pipeline"})-[*..2]-(n)
   RETURN path;
   ```
3. Pass subgraph context to LLM

---

## Memgraph-specific modeling considerations

### Memory estimation

```
RAM ≈ nodes × 204B + edges × 154B + properties + indexes
```

- For 50+ indexes: add ~20% overhead
- Query multiplier: 1.5x (basic) to 2x (algorithms)
- Use the [storage calculator](https://memgraph.com/storage-calculator)

### Data type choices for memory

| Prefer | Over | Why |
|--------|------|-----|
| `Integer` | String numbers | Smaller, faster comparison |
| `Boolean` | String "true"/"false" | Lightest type |
| `date()`, `datetime()` | String dates | ~15B vs ~22B; enables temporal queries |
| `Enum` | Repeated strings | Less memory, faster comparison |

### Indexing during modeling

- Create indexes BEFORE large imports on MATCH/MERGE key properties
- Label-property indexes are NOT auto-created (unless flag enabled)
- Uniqueness constraints do NOT create indexes — add them separately
- Run `ANALYZE GRAPH` after data load

### Storage modes

| Mode | Best for |
|------|----------|
| `IN_MEMORY_TRANSACTIONAL` | Default — ACID, concurrent reads/writes |
| `IN_MEMORY_ANALYTICAL` | Bulk import (up to 6x faster), analytics workloads |

Switch for bulk loading:

```cypher
STORAGE MODE IN_MEMORY_ANALYTICAL;
-- bulk import here
STORAGE MODE IN_MEMORY_TRANSACTIONAL;
```

Create a manual snapshot before switching back: `CREATE SNAPSHOT;`

---

## CSV import workflow

### 1. Design the model from CSV columns

Map CSV columns to node properties. Identify which columns represent entities
(nodes) vs connections (relationships).

### 2. Create indexes before import

```cypher
CREATE INDEX ON :Person;
CREATE INDEX ON :Person(name);
```

### 3. Load and transform

```cypher
LOAD CSV FROM "/path/data.csv" WITH HEADER AS row
CREATE (:Person {
  name: row.Name,
  age: toInteger(row.Age),
  dob: date(row.Date_of_Birth)
});
```

CSV values are always strings — convert with `toInteger()`, `toFloat()`,
`date()`, `toBoolean()`.

### 4. Create relationships

```cypher
MATCH (a:Person {name: "Alice"}), (b:Person {name: "Bob"})
MERGE (a)-[:FRIENDS_WITH]->(b);
```

Use `MERGE` (not `CREATE`) to avoid duplicate relationships. Use `LIMIT` and
`WHERE a <> b` to control combinatorial explosion.

### 5. Batch large imports

```cypher
USING PERIODIC COMMIT 1000
LOAD CSV FROM "/path/data.csv" WITH HEADER AS row
CREATE (:Node {id: row.id, name: row.name});
```

---

## LPG vs RDF

| Feature | LPG (Memgraph) | RDF |
|---------|-----------------|-----|
| Data structure | Labeled nodes/edges + properties | Subject-predicate-object triples |
| Schema | Flexible, optional | Ontology-driven (RDFS/OWL) |
| Query language | Cypher | SPARQL |
| Performance | Real-time traversal + analytics | Semantic web / linked data |
| Ease of use | Intuitive, developer-friendly | Standards-heavy |

Choose LPG when: real-time analytics, schema flexibility, graph algorithms,
developer ergonomics.

Choose RDF when: linked data integration, semantic reasoning, ontology required.

---

## Checklist for a good data model

- [ ] Clear node labels that group similar entities
- [ ] Well-named relationship types (verbs: KNOWS, OWNS, BELONGS_TO)
- [ ] Properties on the right entity (node vs relationship vs separate node)
- [ ] No unnecessary data duplication
- [ ] Temporal and numeric types (not strings) for dates and numbers
- [ ] Indexes on properties used in MATCH/WHERE
- [ ] No supernodes without mitigation strategy
- [ ] Validated with `PROFILE` on real queries
- [ ] Memory estimate fits available RAM
