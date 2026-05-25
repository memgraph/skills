# MAGE Module Reference

Complete list of available algorithm modules organized by category.

## Centrality

| Module | Lang | Key procedure | YIELD |
|--------|------|---------------|-------|
| `pagerank` | C++ | `pagerank.get(max_iterations?, damping_factor?, stop_epsilon?, num_of_threads?)` | `node`, `rank` |
| `betweenness_centrality` | C++ | `betweenness_centrality.get(directed?, normalized?, threads?)` | `node`, `betweenness_centrality` |
| `degree_centrality` | C++ | `degree_centrality.get(type?)` | `node`, `degree` |
| `katz_centrality` | C++ | `katz_centrality.get(alpha?, beta?, epsilon?, max_iterations?)` | `node`, `rank` |

## Community detection

| Module | Lang | Key procedure | YIELD |
|--------|------|---------------|-------|
| `community_detection` | C++ | `community_detection.get(weight?, coloring?, min_graph_shrink?, community_alg_threshold?, coloring_alg_threshold?, num_of_threads?)` | `node`, `community_id` |
| `leiden_community_detection` | C++ | `leiden_community_detection.get(weight_property?, gamma?, theta?, resolution_parameter?, max_iterations?)` | `node`, `community_id` |
| `weakly_connected_components` | C++ | `weakly_connected_components.get()` | `node`, `component_id` |

## Path & structure

| Module | Lang | Key procedure | YIELD |
|--------|------|---------------|-------|
| `algo` | C++ | Various traversal utilities | - |
| `path` | C++ | Path navigation/analysis | - |
| `cycles` | C++ | `cycles.get()` | `cycles` |
| `bridges` | C++ | `bridges.get()` | `bridges` |
| `biconnected_components` | C++ | `biconnected_components.get()` | `bcc_id`, `node_from`, `node_to` |
| `bipartite_matching` | C++ | `bipartite_matching.max()` | `maximum_matching` |
| `max_flow` | Python | `max_flow.get_flow(source, sink, cap_property?)` | `max_flow` |
| `tsp` | Python | `tsp.solve(...)` | `sources`, `destinations` |
| `vrp` | Python | Vehicle routing | - |
| `set_cover` | Python | `set_cover.cp_solve(...)` | `total_cost`, `element_id` |
| `distance_calculator` | C++ | `distance_calculator.single(start, end)` | `distance` |

## Graph ML

| Module | Lang | Key procedure | YIELD |
|--------|------|---------------|-------|
| `node2vec` | Python | `node2vec.get_embeddings(is_directed, p, q, num_walks, walk_length, vector_size, ...)` | `nodes`, `embeddings` |
| `node2vec` | Python | `node2vec.set_embeddings(...)` - writes `embedding` property | `nodes`, `embeddings` |
| `gnn` | Python | `gnn.pyg_export(node_props?, edge_props?, label_prop?)` | `json_data` |
| `gnn_link_prediction` | Python | GNN link prediction pipeline | - |
| `gnn_node_classification` | Python | GNN node classification pipeline | - |
| `tgn` | Python | Temporal Graph Networks - `set_params()`, `update()`, `train_and_eval()`, `predict_link_score()` | - |
| `embeddings` | Python | `embeddings.node_sentence(input_nodes?, config?)` | `node`, `embedding` |
| `knn` | Python | K-nearest neighbors | - |
| `kmeans_clustering` | Python | `kmeans_clustering.get(n_clusters, ...)` | `node`, `cluster_id` |
| `graph_coloring` | Python | `graph_coloring.color_graph(...)` | `node`, `color` |
| `node_similarity` | C++ | `node_similarity.jaccard(node1, node2)` | `similarity` |

## Online / dynamic (Enterprise)

| Module | Lang | Procedures | YIELD |
|--------|------|-----------|-------|
| `pagerank_online` | C++ | `set(walks?, epsilon?)`, `get()`, `update(cv, ce, dv, de)`, `reset()` | `node`, `rank` |
| `community_detection_online` | C++ | `set(directed?, weighted?, ...)`, `get()`, `update(cv, ce, uv, ue, dv, de)`, `reset()` | `node`, `community_id` |
| `betweenness_centrality_online` | C++ | `set()`, `get()`, `update(...)`, `reset()` | `node`, `betweenness_centrality` |
| `katz_centrality_online` | C++ | `set()`, `get()`, `update(...)`, `reset()` | `node`, `rank` |
| `node2vec_online` | Python | `set()`, `get()`, `update(...)`, `reset()` | `node`, `embedding` |

## Utility modules

| Module | Lang | Description |
|--------|------|-------------|
| `collections` | C++ | List operations: `sort`, `union`, `union_all`, `remove_all`, `contains`, `flatten`, `frequencies_as_map`, `pairs`, `to_set`, `sum`, `partition` |
| `map` | C++ | Map operations |
| `text` | C++ | String manipulation |
| `math` | C++ | Math operations |
| `convert` / `convert_c` | C++ | Data structure conversion, `to_tree()` |
| `create` | C++ | `create.node()`, `create.nodes()`, `create.relationship()` |
| `merge` | C++ | MERGE-like operations |
| `refactor` | C++ | Node/relationship refactoring |
| `label` | C++ | Label utilities, `label.exists()` |
| `node` / `nodes` | C++ | Node management |
| `neighbors` | C++ | Direct neighbor queries |
| `set_property` | C++ | Dynamic property access/edit |
| `periodic` | C++ | Periodic query execution |
| `uuid_generator` | C++ | UUID generation |
| `csv_utils` | C++ | CSV file create/delete |
| `date` | Python | Date/time operations |
| `temporal` | Python | Extended temporal operations |
| `do` | C++ | Conditional query execution |
| `meta` | C++ | Graph node/rel info + online stats |
| `meta_util` | Python | Meta-level graph descriptions |
| `mgps` | Python | `mgps.version()`, `mgps.validate_predicate()` |
| `util_module` | C++ | Validation, MD5 hash |

## LLM / AI

| Module | Lang | Description |
|--------|------|-------------|
| `llm` | Python | `llm.complete(text, config?)` - LiteLLM completions. Config: `model`, `api_base`, `system_prompt` |
| `llm_util` | Python | **Deprecated** - `llm_util.schema()`. Use `SHOW SCHEMA INFO` instead |
| `embeddings` | Python | Sentence embeddings via SentenceTransformer or LiteLLM |

## Data import/export

| Module | Lang | Description |
|--------|------|-------------|
| `export_util` | Python | `export_util.json(path)` - graph to JSON |
| `import_util` | Python | `import_util.json(path)` - JSON to graph |
| `json_util` | Python | `json_util.load_from_path(path)`, `json_util.load_from_url(url)` |
| `xml_module` | Python | XML loading/parsing |
| `migrate` | Python | MySQL, SQL Server, Oracle access |

## Integrations

| Module | Lang | Description |
|--------|------|-------------|
| `nxalg` | Python | 70+ NetworkX algorithm wrappers |
| `igraphalg` | Python | igraph algorithm wrappers |
| `cugraph` | CUDA | NVIDIA GPU algorithms (centrality, link analysis, clustering) |
| `elasticsearch_synchronization` | Python | Memgraph ↔ Elasticsearch sync |

## APOC → MAGE migration map

| APOC | MAGE |
|------|------|
| `apoc.coll.union` | `collections.union()` |
| `apoc.coll.flatten` | `collections.flatten()` |
| `apoc.coll.toSet` | `collections.to_set()` |
| `apoc.coll.sum` | `collections.sum()` |
| `apoc.convert.toTree` | `convert_c.to_tree()` |
| `apoc.convert.fromJsonList` | `json_util.from_json_list()` |
| `apoc.convert.toJson` | `json_util.to_json()` |
| `apoc.create.node` | `create.node()` |
| `apoc.date.convertFormat` | `date.convert_format()` |
| `apoc.label.exists` | `label.exists()` |
| `apoc.meta.nodeTypeProperties` | `schema.node_type_properties()` |
| `apoc.refactor.*` | `refactor.*` |
| `apoc.text.*` | `text.*` |
| `apoc.util.md5` | `util_module.md5()` |
| `apoc.util.validatePredicate` | `mgps.validate_predicate()` |
| `apoc.version` | `mgps.version()` |

## Procedure alias configuration

Map Neo4j/APOC names to MAGE names via JSON file + `--query-callable-mappings-path`:

```json
{"db.components": "mgps.components", "util.validate": "mgps.validate"}
```

Inspect: `SHOW QUERY CALLABLE MAPPINGS;`
