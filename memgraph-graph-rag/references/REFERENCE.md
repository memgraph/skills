# Reference: GraphRAG with Memgraph (Agent-Oriented)

This reference supplements the skill with concrete patterns, tool contracts, and queries that are language-agnostic.

## Tool Contract Examples

### Tool: `retrieve_context`

**Input**
```json
{
  "question": "string",
  "vector_k": 5,
  "hop_limit": 2,
  "max_chunks": 10
}
```

**Output**
```json
{
  "chunks": [
    {
      "id": "chunk-uuid",
      "text": "...",
      "source": "url|path",
      "entities": ["EntityA", "EntityB"]
    }
  ],
  "graph_stats": {
    "vector_hits": 5,
    "expanded_chunks": 12,
    "hops": 2
  }
}
```

### Tool: `run_query`

**Input**
```json
{
  "cypher": "MATCH (n) RETURN count(n) AS cnt",
  "params": {}
}
```

**Output**
```json
{
  "rows": [{"cnt": 1234}]
}
```

## Schema Template

**Nodes**
- `Document` {id, title, source, created_at}
- `Chunk` {id, text, source, embedding}
- `Entity` {id, name, type, description}
- `Concept` {id, name}

**Relationships**
- `(Document)-[:HAS_CHUNK]->(Chunk)`
- `(Entity)-[:MENTIONED_IN]->(Chunk)`
- `(Entity)-[:RELATES_TO]->(Entity)`
- `(Chunk)-[:NEXT]->(Chunk)`

## Core Indexes

```cypher
CREATE INDEX ON :Document(id);
CREATE INDEX ON :Chunk(id);
CREATE INDEX ON :Entity(name);
CREATE INDEX ON :Chunk;
```

Vector index (dimension must match your embedding model):

```cypher
CREATE VECTOR INDEX vs_chunks
ON :Chunk(embedding)
WITH CONFIG {"dimension": 384, "capacity": 100000};
```

## Retrieval Patterns

### Pattern A: Vector → Chunk → Entity Context

```cypher
CALL embeddings.text([$question]) YIELD embeddings
CALL vector_search.search('vs_chunks', $vector_k, embeddings[0])
YIELD node, similarity
OPTIONAL MATCH (e:Entity)-[:MENTIONED_IN]->(node)
RETURN node.text AS text, similarity, collect(e.name) AS entities
ORDER BY similarity DESC
LIMIT $max_chunks;
```

### Pattern B: Vector + BFS Expansion (bounded)

```cypher
CALL embeddings.text([$question]) YIELD embeddings
CALL vector_search.search('vs_chunks', $vector_k, embeddings[0]) YIELD node
MATCH (node)-[*bfs..$hop_limit]-(expanded:Chunk)
WITH DISTINCT expanded, degree(expanded) AS importance
ORDER BY importance DESC
RETURN expanded.text AS text
LIMIT $max_chunks;
```

### Pattern C: Sequential Context Around Hits

```cypher
CALL embeddings.text([$question]) YIELD embeddings
CALL vector_search.search('vs_chunks', $vector_k, embeddings[0]) YIELD node
OPTIONAL MATCH (prev:Chunk)-[:NEXT]->(node)
OPTIONAL MATCH (node)-[:NEXT]->(next:Chunk)
RETURN prev.text AS previous, node.text AS matched, next.text AS next;
```

## Safe Parameterization

Always pass user inputs via parameters instead of string interpolation.

```cypher
CALL embeddings.text([$question]) YIELD embeddings
CALL vector_search.search('vs_chunks', $vector_k, embeddings[0]) YIELD node
RETURN node.text AS text
LIMIT $max_chunks;
```

## Evaluation Checklist

- **Recall@k**: sample questions with known answers
- **Groundedness**: answer must quote or cite retrieved chunks
- **Latency**: P95 retrieval duration
- **Coverage**: % of sources ingested and indexed

## Guardrails

- Enforce max hops and max chunks
- Reject queries without a vector index
- Log query traces (vector hits + expansions)
- If context is insufficient, respond accordingly
