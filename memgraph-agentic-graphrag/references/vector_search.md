# Vector Search

### Query the vector index

Search for the nearest neighbors of a query vector:

```cypher
CALL vector_search.search('vs_index', 5, [1.0, 2.0, 3.0])
YIELD node, distance, similarity
RETURN node, similarity
ORDER BY similarity DESC;
```

Combine vector search with **graph traversals** to enrich results (replace `<Label>` and `<RELATIONSHIP>` with values from your schema):

```cypher
CALL vector_search.search('vs_index', 5, [1.0, 2.0, 3.0])
YIELD node, similarity
MATCH (entity:<Label>)-[:<RELATIONSHIP>]->(node)
RETURN entity.title AS title, similarity
ORDER BY similarity DESC;
```

Use the **embeddings module** to generate a query vector from text on the fly:

```cypher
CALL embeddings.text(['<natural language query>']) YIELD embeddings, success
CALL vector_search.search('vs_index', 5, embeddings[0]) YIELD node, similarity
MATCH (entity:<Label>)-[:<RELATIONSHIP>]->(node)
RETURN entity.title AS title, similarity
ORDER BY similarity DESC;
```

Search a **vector index on edges**:

```cypher
CALL vector_search.search_edges('edge_vs_index', 5, [1.0, 2.0, 3.0])
YIELD edges, distance, similarity
RETURN edges, similarity
ORDER BY similarity DESC;
```

Compute **cosine similarity** between two vectors without an index:

```cypher
RETURN vector_search.cosine_similarity([1.0, 2.0], [1.0, 3.0]) AS similarity;
```

Inspect the current state of all vector indices:

```cypher
CALL vector_search.show_index_info() YIELD * RETURN *;
```

### Similarity metrics

| Metric     | Description                                       |
|------------|---------------------------------------------------|
| l2sq       | Squared Euclidean distance (default)              |
| cos        | Cosine similarity                                 |
| ip         | Inner product (dot product)                       |
| haversine  | Haversine distance (suitable for geographic data) |
| pearson    | Pearson correlation coefficient                   |
| divergence | A divergence-based metric                         |
| hamming    | Hamming distance                                  |
| tanimoto   | Tanimoto coefficient                              |
| sorensen   | Sorensen-Dice coefficient                         |
| jaccard    | Jaccard index                                     |

### Notes

- Vector indices are powered by [USearch](https://github.com/unum-cloud/usearch).
- Memgraph uses `READ_UNCOMMITTED` isolation specifically for vector indices; all other ACID guarantees remain intact.
- `dimension` and `capacity` are **mandatory** when creating an index.
- The default metric is `l2sq` and the default scalar kind is `f32`.
- Dropping a single-store vector index rewrites all vectors back into the property store — this can be slow and memory-intensive on large datasets.
- To drop an index: `DROP VECTOR INDEX vs_index;`

Run the `CREATE VECTOR INDEX` command before attempting any vector search queries
on the graph.

For more details visit https://memgraph.com/docs/querying/vector-search.