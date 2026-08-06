---
name: memgraph-agentic-graphrag
description: Answers questions over any knowledge graph stored in Memgraph using agentic GraphRAG techniques (text2Cypher; vector/text search also called local graph search; query-focused summarization).
---

## Deterministic Analytical Questions - Text2Cypher

When a user asks a question that requires precise information from the graph—for
example, counts, aggregations, or analytical queries where exact data is needed—use
a **text2Cypher** approach:

1. **Generate a Cypher query** from the natural language question, based on the
   graph schema (use `SHOW SCHEMA INFO;` query to get the schema).
2. **Execute the query** using the Memgraph MCP tool `run_query` when the
   workspace is connected to Memgraph.
3. **Return the result** to the user with a clear summary of the findings.

Example: if asked "How many nodes of type X exist?", generate and run:
```cypher
MATCH (n:X) RETURN n.name AS name, count(n) AS count ORDER BY count DESC;
```
Then report back the result to the user.

## Similar entities and semantic search - Local Graph Search

When a user requests to find entities similar to a given one, or to determine
which nodes are related to a concept, employ vector or text search combined with
graph traversals to discover the most relevant results.
```
CALL embeddings.text(['<user query or entity description>']) YIELD embeddings, success
CALL vector_search.search('vs_index', 5, embeddings[0]) YIELD distance, node, similarity
WITH node AS chunk, similarity
MATCH (entity:<Label>)-[:HAS_CHUNK]->(chunk)
RETURN entity.title, similarity ORDER BY similarity DESC LIMIT 5;
```

Replace `<Label>` with the actual node label from the schema.

See [text search reference](references/text_search.md).
See [vector search reference](references/vector_search.md).

## Broad questions - Query-focuse Summarization

When a user asks a broad question, consider using query-focused summarization
over pre-computed community summaries (map-reduce over the graph).

```
WITH "{{the_user_question}}" AS USER_QUESTION
// 1. Identify relevant communities (Thresholding)
MATCH (c:Community)
    WHERE c.nodes_count > 5  // Optional: only use significant communities
// 2. Map Step: Generate a partial answer for EACH community
WITH USER_QUESTION, c,
     llm.complete("How does the following community summary: " + c.summary + " relate to: " + USER_QUESTION) AS partial_answer
  WHERE partial_answer IS NOT NULL AND partial_answer <> ""
WITH USER_QUESTION, collect(partial_answer) AS map_results
// 3. Reduce Step: Synthesize the final consolidated answer
WITH "The following are partial answers from different thematic clusters of " +
     " a dataset. Synthesize them into a single, cohesive response to the " +
     "original query: " + USER_QUESTION +
      "\n\nPartial Answers:\n" +
      reduce(s = "", res IN map_results | s + "- " + res + "\n") AS reduce_prompt
RETURN llm.complete(reduce_prompt) AS final_answer;
```

If the graph is missing required preprocessing, see [preprocessing](references/preprocessing.md).