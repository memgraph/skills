---
name: memgraph-graph-rag
description: Language-agnostic blueprint for building GraphRAG systems with Memgraph and agent tooling. Covers end-to-end architecture, schema design, ingestion, hybrid retrieval, tool contracts, and evaluation. Use when designing GraphRAG platforms that must work across multiple programming languages.
license: Apache-2.0
compatibility: Any language with a Bolt-compatible driver. Memgraph instance required.
metadata:
  author: memgraph
  version: "0.1.0"
  repository: https://github.com/memgraph/skills
---

# Memgraph GraphRAG for Agent Systems (Language-Agnostic)

Build Graph Retrieval-Augmented Generation systems that combine vector similarity search with graph traversal, and expose retrieval as tools for agents across any programming language.

## When to Use

Use this skill when:

- Designing a GraphRAG platform (not a single app)
- Supporting multiple client languages (Python, JS, Java, Go, etc.)
- Building agent tools for ingestion, retrieval, and diagnostics
- Combining document chunk retrieval with entity/relationship context

Do NOT use this skill for:

- Simple vector-only RAG or standalone chatbots
- Pure ETL without retrieval or agent workflows
- Use cases that require strict SQL semantics

## Outcomes

By following this skill, you will deliver:

- A graph schema that supports hybrid retrieval
- A repeatable ingestion pipeline
- A retrieval tool contract usable by agents
- An evaluation plan for recall, latency, and groundedness

## Architecture Overview

```
Sources (files, URLs, APIs)
        │
        ▼
┌──────────────────────┐
│ Ingestion Pipeline   │  Parse → chunk → entity extract
└──────────────────────┘
        │
        ▼
┌──────────────────────┐
│ Memgraph             │  Graph + embeddings + indexes
└──────────────────────┘
        │
        ▼
┌──────────────────────┐
│ Hybrid Retriever     │  Vector search + graph expansion
└──────────────────────┘
        │
        ▼
┌──────────────────────┐
│ Agent Tools          │  run_query / retrieve_context
└──────────────────────┘
        │
        ▼
┌──────────────────────┐
│ LLM Response         │  Answer with citations
└──────────────────────┘
```

## Step 1: Define GraphRAG Requirements

Document the following before implementation:

- **Use cases**: Q&A, research, report generation, troubleshooting
- **Source types**: PDFs, HTML, Markdown, APIs, databases
- **Entity types**: People, systems, components, products, errors
- **Relationship types**: MENTIONS, CONNECTS_TO, DEPENDS_ON, NEXT
- **Latency targets**: P95 retrieval time, max hops for expansion

## Step 2: Choose Ingestion Strategy

Pick one of these:

- **Toolkit-based**: `unstructured2graph` + `lightrag-memgraph`
- **Custom ETL**: your parser + entity extractor + Cypher loader
- **Batch migration**: sql2graph for relational sources

Ingestion must always produce:

- Chunk nodes with text + source metadata
- Entity nodes with normalized names
- Relationships that connect entities to chunks and each other

## Step 3: Standard Graph Schema (Recommended)

Use a stable schema so any client can query consistently:

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

## Step 4: Embeddings + Vector Index

- Store embeddings on `Chunk.embedding`
- Create a vector index for `Chunk(embedding)`
- Use Memgraph’s vector search in retrieval

Keep embeddings consistent across ingestion and queries.

## Step 5: Hybrid Retrieval Strategy

Default retrieval flow:

1. **Vector search** to get top-$k$ chunks
2. **Graph expansion** to include related chunks/entities
3. **Ranking** by degree, recency, or path length
4. **Dedup** and trim to the model context budget

Recommended query pattern (pseudo-Cypher):

- Vector search on `Chunk`
- BFS traversal limited to $1–3$ hops
- Return chunk text + related entities

## Step 6: Agent Tool Contracts

Expose retrieval and diagnostics as tools. Minimal contract:

**Tool: `run_query`**
- Input: `{ cypher: string, params?: object }`
- Output: `{ rows: array }`

**Tool: `retrieve_context`**
- Input: `{ question: string, vector_k?: number, hop_limit?: number }`
- Output: `{ chunks: [{text, source, entities[]}], graph_stats }`

**Tool: `ingest_sources`**
- Input: `{ sources: string[], mode?: "append" | "replace" }`
- Output: `{ documents, chunks, entities, duration_ms }`

Agents should:

- Call `get_schema` once per session
- Use parameterized queries
- Log retrieval traces for debugging

## Step 7: Language-Agnostic Integration

Memgraph supports the Bolt protocol. Use a Bolt-compatible driver in your language of choice.

Integration responsibilities in each language:

- Create a connection pool
- Execute parameterized Cypher
- Map results to your tool contract
- Handle retries and timeouts

## Step 8: Evaluation & Observability

Minimum evaluation suite:

- **Recall@k**: relevant chunks retrieved
- **Groundedness**: answer supported by chunks
- **Latency**: P95 retrieval under target
- **Coverage**: percent of sources indexed

Log for each request:

- Query text
- Top vector hits
- Expansion hops used
- Final context length

## Guardrails

- Always answer from retrieved context
- If context is insufficient, say so
- Avoid unbounded graph traversal
- Enforce per-request timeouts

## Optional: Use Memgraph AI Toolkit

Use the Memgraph AI Toolkit for faster setup:

- `memgraph-toolbox` for core utilities
- `unstructured2graph` for parsing and ingestion
- `lightrag-memgraph` for entity extraction
- `langchain-memgraph` for agent tooling

Treat these as implementation options, not requirements.

## Deliverable Checklist

- [ ] Graph schema documented and versioned
- [ ] Ingestion pipeline with idempotency
- [ ] Vector index created and verified
- [ ] Retrieval tool contract implemented
- [ ] Evaluation harness with sample queries
- [ ] Monitoring dashboards for latency and errors
