# Import reference

## cross_database procedures

Available in the `memgraph/memgraph-mage` image. Named `migrate.*` before Memgraph 3.11 (the old
names remain as aliases). Enterprise-licensed from Memgraph 3.13.

Every procedure yields `row: Map`, one per source row, and takes an optional `config_path` to a
JSON file instead of the inline `config` map.

| Procedure | First argument | Config map |
|---|---|---|
| `cross_database.postgresql(table_or_sql, config, config_path?, params?)` | table name or `SELECT` | `psycopg2.connect` kwargs: `host`, `port`, `user`, `password`, `database` |
| `cross_database.mysql(table_or_sql, config, config_path?, params?)` | table name or `SELECT` | `mysql.connector.connect` kwargs |
| `cross_database.sql_server(table_or_sql, config, config_path?, params?)` | table name or `SELECT` | `pyodbc.connect` kwargs: `driver`, `server`, `database`, `uid`, `pwd`, `TrustServerCertificate` |
| `cross_database.oracle_db(table_or_sql, config, config_path?, params?)` | table name or `SELECT` | `oracledb.connect` kwargs: `user`, `password`, `dsn` (`host:port/service`) or `host`/`port`/`service_name`; no `database` key |
| `cross_database.duckdb(query, setup_queries?)` | SQL | list of statements run first, e.g. `['LOAD json;']` |
| `cross_database.bolt(label_or_rel_or_query, config, config_path?, params?)` | Cypher, `"(:Label)"` or `"[:TYPE]"` | `host` (default `localhost`), `port`, `username`, `password`, `database` |
| `cross_database.neo4j(...)` | same as `bolt` | defaults `username`/`password` to `neo4j`/`password` |
| `cross_database.s3(file_path, config, config_path?)` | `s3://bucket/key.csv` | `aws_access_key_id`, `aws_secret_access_key`, `aws_session_token`, `region_name`, all optional; no endpoint key |
| `cross_database.arrow_flight(query, config, config_path?)` | SQL | `host`, `port`, `username`, `password` |
| `cross_database.servicenow(endpoint, config, config_path?, params?)` | REST URL | `username`, `password` |

`params` passes query parameters to the source driver for the SQL sources. Every value from
`s3` arrives as a string, like `LOAD CSV`; the SQL sources keep the driver's types.

The S3 procedure reads an S3-compatible store (RustFS, MinIO, Ceph) only through the
`AWS_ENDPOINT_URL` environment variable of the Memgraph server; an endpoint key in the config map
is ignored. The `LOAD` clauses, by contrast, take `"aws_endpoint_url"` in `WITH CONFIG`.

### One example per source

```cypher
CALL cross_database.postgresql('SELECT id, email FROM customers',
  {user: 'memgraph', password: 'password', host: 'localhost', database: 'demo_db'})
YIELD row
CREATE (:Customer {id: row.id, email: row.email});

CALL cross_database.mysql('products',
  {user: 'memgraph', password: 'password', host: 'localhost', database: 'shop_db'})
YIELD row
CREATE (:Product {sku: row.sku, price: row.price});

-- SQL Server: the map is a pyodbc connection string, so the keys are driver/server/uid/pwd.
-- The MAGE image ships "ODBC Driver 18 for SQL Server", which requires TrustServerCertificate
-- (or a real certificate). The docs' user/password/host form fails with "Data source name not found".
CALL cross_database.sql_server('SELECT id, title FROM books',
  {driver: 'ODBC Driver 18 for SQL Server', server: 'localhost', database: 'library_db',
   uid: 'memgraph', pwd: 'password', TrustServerCertificate: 'yes'})
YIELD row
MERGE (b:Book {id: row.id}) SET b.title = row.title;

-- Oracle: oracledb has no `database` key; pass a dsn (or host/port/service_name). Oracle returns
-- column names in UPPER CASE unless the SELECT uses quoted aliases.
CALL cross_database.oracle_db('SELECT dept_id AS "dept_id", dept_name AS "dept_name" FROM departments',
  {user: 'memgraph', password: 'password', dsn: 'localhost:1521/FREEPDB1'})
YIELD row
MERGE (d:Department {id: row.dept_id}) SET d.name = row.dept_name;

CALL cross_database.duckdb("SELECT * FROM read_csv_auto('/data/people.csv')", [])
YIELD row
CREATE (:Person {name: row.name});

CALL cross_database.bolt('MATCH (m:Movie) RETURN m.title AS title', {host: 'other-memgraph', port: 7687})
YIELD row
CREATE (:Movie {title: row.title});

CALL cross_database.s3('s3://my-bucket/orders.csv',
  {aws_access_key_id: 'your-key', aws_secret_access_key: 'your-secret', region_name: 'eu-central-1'})
YIELD row
CREATE (:Order {id: row.id, total: row.total});
```

DuckDB can also read Parquet, JSON and remote files through its own readers, which makes it a
handy transformation step when a file needs reshaping before it becomes nodes.

## Migrating a whole graph from Neo4j

Run Neo4j and Memgraph on different Bolt ports, for example Memgraph as
`docker run -p 7688:7687 memgraph/memgraph-mage` and connect the client to 7688.

1. Create the temporary index the merge relies on:

   ```cypher
   CREATE INDEX ON :__MigrationNode__(__elementId__);
   ```

2. Nodes, including orphans that the triplet query would skip:

   ```cypher
   CALL cross_database.neo4j(
     "MATCH (n) RETURN labels(n) AS node_labels, elementId(n) AS node_id, properties(n) AS node_props",
     {host: "neo4j-host", port: 7687, username: "neo4j", password: $pw})
   YIELD row
   MERGE (n:__MigrationNode__ {__elementId__: row.node_id})
   SET n:row.node_labels
   SET n += row.node_props;
   ```

3. Relationships:

   ```cypher
   CALL cross_database.neo4j(
     "MATCH (n)-[r]->(m) RETURN elementId(n) AS src_id, elementId(m) AS dest_id, type(r) AS rel_type, properties(r) AS edge_props",
     {host: "neo4j-host", port: 7687, username: "neo4j", password: $pw})
   YIELD row
   MATCH (n:__MigrationNode__ {__elementId__: row.src_id}), (m:__MigrationNode__ {__elementId__: row.dest_id})
   CREATE (n)-[r:row.rel_type]->(m)
   SET r += row.edge_props;
   ```

4. Clean up and recreate the schema objects Neo4j does not export through Cypher:

   ```cypher
   MATCH (n:__MigrationNode__) REMOVE n:__MigrationNode__, n.__elementId__;
   DROP INDEX ON :__MigrationNode__(__elementId__);
   CREATE INDEX ON :Person(id);          -- whatever the Neo4j schema had
   CREATE CONSTRAINT ON (p:Person) ASSERT p.id IS UNIQUE;
   ```

## Neo4j shorthand forms

A node pattern `"(:Person)"` yields rows of `{labels, properties}`; a relationship pattern
`"[:KNOWS]"` yields `{from_labels, from_properties, to_labels, to_properties, edge_properties}`.
The parentheses and brackets are required: a bare `":Person"` is sent to Neo4j as Cypher and
fails with a syntax error. Neither form creates anything; you write the `CREATE`:

```cypher
CALL cross_database.neo4j("(:Person)", {host: "neo4j-host", port: 7687, username: "neo4j", password: $pw})
YIELD row
CREATE (n) SET n:row.labels SET n += row.properties;

CALL cross_database.neo4j("[:KNOWS]", {host: "neo4j-host", port: 7687, username: "neo4j", password: $pw})
YIELD row
MATCH (a:Person {id: row.from_properties.id}), (b:Person {id: row.to_properties.id})
CREATE (a)-[r:KNOWS]->(b) SET r += row.edge_properties;
```

Dynamic labels only work from a property access such as `SET n:row.labels`. Binding the list to a
plain variable first and writing `CREATE (n:labels)` or `SET n:labels`, as the docs example does,
creates a node whose label is literally `labels`.

## Parallel client loader with retry

Processes rather than threads (Python's GIL), one driver per process, at most one process per
hardware thread. Nodes are loaded completely before relationships start.

```python
import random, time
from multiprocessing import Pool
from neo4j import GraphDatabase
from neo4j.exceptions import TransientError

URI, AUTH = "bolt://localhost:7687", ("", "")
BATCH = 5000

NODE_Q = "UNWIND $rows AS row CREATE (:Person {id: row.id, name: row.name})"
REL_Q = """UNWIND $rows AS row
MATCH (a:Person {id: row.from_id}), (b:Person {id: row.to_id})
CREATE (a)-[:KNOWS {since: row.since}]->(b)"""


def chunks(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i:i + size]


def run_batch(args):
    query, rows = args
    delay = 0.5
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        for attempt in range(8):
            try:
                with driver.session() as session:
                    session.execute_write(lambda tx: tx.run(query, rows=rows).consume())
                return len(rows)
            except TransientError as e:          # "Cannot resolve conflicting transactions"
                if attempt == 7:
                    raise
                time.sleep(delay + random.uniform(0, delay / 2))
                delay *= 1.1
    return 0


if __name__ == "__main__":
    nodes = load_rows("people.csv")        # list of dicts, typed already
    rels = load_rows("knows.csv")

    with GraphDatabase.driver(URI, auth=AUTH) as driver, driver.session() as session:
        # index DDL is refused inside a managed transaction; use an autocommit query
        session.run("CREATE INDEX ON :Person(id);").consume()

    with Pool(8) as pool:
        n = sum(pool.map(run_batch, [(NODE_Q, b) for b in chunks(nodes, BATCH)]))
        r = sum(pool.map(run_batch, [(REL_Q, b) for b in chunks(rels, BATCH)]))
    print(f"nodes {n}, relationships {r}")
```

Rules of thumb from the Memgraph docs: start batching above roughly 10 million objects; a
single-threaded `LOAD CSV` is fine below that. Expect on the order of a million objects per
second on good hardware. With `IN_MEMORY_ANALYTICAL` there are no conflicts to retry, but do not
run node and relationship batches at the same time.

## LOAD CSV clause details

```
LOAD CSV FROM <location> [WITH CONFIG {"aws_region": .., "aws_access_key": .., "aws_secret_key": .., "aws_endpoint_url": ..}]
  (WITH | NO) HEADER
  [IGNORE BAD]
  [DELIMITER <string>]      -- default ","
  [QUOTE <string>]          -- default "\""
  [NULLIF <string>]         -- no null conversion by default
  AS <variable>
```

- `<location>`: local path on the server, `http://`, `https://`, `ftp://` or `s3://`. Remote files
  are downloaded to `/tmp` first; `gzip` and `bzip2` are decompressed transparently.
- At most one `LOAD CSV` per query; it cannot be the only clause.
- A `MATCH`/`MERGE` before `LOAD CSV` must not produce more than one row; otherwise the query
  fails with "LOAD CSV can be executed only once, please check if the cardinality of the operator
  before LOAD CSV is 1". Config map keys in `WITH CONFIG` must be quoted strings.
- `RETURN row[0], row[1]` needs aliases (`AS a, AS b`); the two expressions otherwise share a name.
- `file.download_conn_timeout_sec` controls the download timeout; a stuck download can be stopped
  with `TERMINATE TRANSACTIONS <tx_id>`.
- Rows from `WITH HEADER` files are maps (`row.name`); from `NO HEADER` files they are lists
  (`row[0]`).
- A single file holding both node and relationship rows can be split with
  `WITH row WHERE row.type = 'PERSON'` in one query and `WITH row WHERE row.type = 'IS_FRIEND'`
  in another.

## Memory and durability during a big import

- In transactional mode each write creates a `Delta` of about 56 bytes; a 10-million-row
  transaction holds hundreds of MB of deltas until commit. Batch, or use analytical mode.
- `SHOW STORAGE INFO;` reports `memory_res`, `peak_memory_res`, vertex and edge counts.
- Snapshots run every `--storage-snapshot-interval` seconds (default 300) and keep
  `--storage-snapshot-retention-count` copies (default 3). For very large imports raise the interval
  so snapshots do not overlap. Analytical mode writes no WAL. Switching back to transactional
  mode writes a snapshot synchronously before the switch completes; if that snapshot fails the
  query throws and the database stays in analytical mode.
- To clear a failed import quickly, delete relationships before nodes in batches:
  ```cypher
  MATCH ()-[r]->() WITH r LIMIT 100000 DELETE r RETURN count(r);
  MATCH (n) WITH n LIMIT 100000 DELETE n RETURN count(n);
  ```
  or `DROP GRAPH;` when the whole database should go.
