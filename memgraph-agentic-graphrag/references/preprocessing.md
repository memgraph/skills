## Retrieve Schema

Schema is useful in almost all GraphRAG cases. To get the schema run the `SHOW
SCHEMA INFO;` query (there is probably an MCP tool available to do that).

## Text Search Preprocessing

To use text search for finding nodes whose properties contain specific text, you
first need to create a text index on the target label and (optionally) specify
which properties to index.

### Create a text index

Index **all** text-indexable properties on a label:

```cypher
CREATE TEXT INDEX entitySearch ON :<Label>;
```

Or index only **specific** properties:

```cypher
CREATE TEXT INDEX entitySearch ON :<Label>(title, description);
```

Replace `<Label>` with the actual node label from the schema (e.g., `Document`, `Product`, `Article`).

## Vector Search Preprocessing

To use vector search for finding similar content in your graph, you first need to:

1. **Create a vector index** on the target node label (e.g., `Chunk`) and specify the embedding property.
2. **Generate and store embeddings** for each node you want searchable.

Here's how you can do both steps in Memgraph:

```cypher
-- Step 1: Create the vector index for your embeddings
CREATE VECTOR INDEX vs_index ON :Chunk(embedding) WITH CONFIG {"dimension": <embedding_dimension>, "capacity": <expected_node_count>};

-- Step 2: Compute sentence embeddings for all Chunk nodes
MATCH (c:Chunk)
WITH collect(c) AS chunks
CALL embeddings.node_sentence(
  chunks,
  {excluded_properties: ["<id_property>", "<metadata_property>"]}
) YIELD success;
```

- The first command sets up a vector index called `vs_index` for the `embedding` property of `Chunk` nodes.
- The second part computes embeddings for every `Chunk` node, excluding properties that should not contribute to the semantic representation (e.g. IDs, internal metadata).

Run these commands before attempting any vector search queries on the graph.

## Communities Preprocessing

Replace `<Label>` and `<RELATIONSHIP>` with the actual node label and relationship type from the schema.

```
MATCH p=(n1:<Label>)-[r:<RELATIONSHIP>]->(n2:<Label>) WITH p
WITH project(p) AS subgraph
CALL community_detection.get(subgraph) YIELD node, community_id
SET node.community_id = community_id;
```

## Ranking (PageRank) Preprocessing

Replace `<Label>` and `<RELATIONSHIP>` with the actual node label and relationship type from the schema.

```
MATCH p=(n1:<Label>)-[r:<RELATIONSHIP>]->(n2:<Label>) WITH p
WITH project(p) AS subgraph
CALL pagerank.get(subgraph, 100, 0.85, 1e-5)
YIELD node, rank
SET node.rank = rank;
```

## Query-focused Summarization Preprocessing

This step generates a natural-language summary for each detected community and
stores it as a `Community` node. Adapt the prompt to fit your domain.

```
WITH "You are summarizing a community (cluster) of nodes from a knowledge graph." +
     " Below are the titles and descriptions of nodes belonging to one community." +
     " Write a concise summary in 2-4 paragraphs that:" +
     " - Captures the main themes and recurring topics." +
     " - Describes what this cluster of nodes represents." +
     " - Does not list individual nodes; synthesize into a coherent narrative." +
     " Once the analysis is done, propose a single label that best describes the community. ---"
     AS COMMUNITY_SUMMARY_PROMPT_TEMPLATE
MATCH (n) WHERE n.community_id IS NOT NULL
WITH n.community_id AS c_id, count(n) AS c_count, collect(n) AS c_members,
     llm.complete(reduce(s=COMMUNITY_SUMMARY_PROMPT_TEMPLATE, m IN collect(n) | s + m.title + " " + m.description + "; ")) AS c_summary
MERGE (community:Community {id: c_id, nodes_count: c_count})
SET community.summary = c_summary
WITH community, c_members
UNWIND c_members AS c_member
MERGE (c_member)-[:BELONGS_TO]->(community)
RETURN community.id AS community_id, community.summary AS community_summary;
```
