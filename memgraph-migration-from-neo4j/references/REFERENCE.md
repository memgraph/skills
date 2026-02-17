# Neo4j → Memgraph Migration — Reference

Full Cypher queries and details for migration. Requires Memgraph with MAGE (migrate module).

## Step 1: Create migration indices

```cypher
CREATE INDEX ON :__MigrationNode__;
CREATE INDEX ON :__MigrationNode__(__elementId__);
```

## Step 2: Migrate orphan nodes (if any)

Run before triplet migration if the graph has nodes with no relationships:

```cypher
CALL migrate.neo4j(
  "MATCH (n) RETURN labels(n) AS node_labels, elementId(n) as node_id, properties(n) as node_props",
  {host: "localhost", port: 7687})
YIELD row
MERGE (n:__MigrationNode__ {__elementId__: row.node_id})
SET n:row.node_labels
SET n += row.node_props;
```

## Step 3: Migrate triplets (nodes and relationships)

```cypher
CALL migrate.neo4j(
  "MATCH (n)-[r]->(m) RETURN labels(n) AS src_labels, type(r) as rel_type, labels(m) AS dest_labels, elementId(n) AS src_id, elementId(m) AS dest_id, properties(n) AS src_props, properties(r) AS edge_props, properties(m) AS dest_props",
  {host: "localhost", port: 7687})
YIELD row
MERGE (n:__MigrationNode__ {__elementId__: row.src_id})
MERGE (m:__MigrationNode__ {__elementId__: row.dest_id})
SET n:row.src_labels
SET m:row.dest_labels
SET n += row.src_props
SET m += row.dest_props
CREATE (n)-[r:row.rel_type]->(m)
SET r += row.edge_props;
```

Adjust `host` and `port` in the config map.

## Step 4: Clean up

```cypher
DROP INDEX ON :__MigrationNode__;
DROP INDEX ON :__MigrationNode__(__elementId__);
MATCH (n) SET n.__elementId__ = null;
```

## Migrate specific data

Partial migration returns rows; use Cypher to create nodes/relationships.

**Nodes with label `Person`:**
```cypher
CALL migrate.neo4j(":Person", {host: "localhost", port: 7687}) YIELD row RETURN row;
```

**Relationships of type `KNOWS`:**
```cypher
CALL migrate.neo4j("[:KNOWS]", {host: "localhost", port: 7687}) YIELD row RETURN row;
```
