---
name: memgraph-import-data
description: >-
  Import or migrate data into Memgraph from CSV, Parquet, JSON/JSONL, CYPHERL
  dumps, relational databases (PostgreSQL, MySQL, SQL Server, Oracle, DuckDB)
  or Neo4j: choosing between LOAD CSV, cross_database procedures and
  client-driven batches, preparing indexes and storage mode, ordering nodes
  before relationships, and verifying counts. Use when the user wants to load,
  bulk-insert, ingest or migrate data into Memgraph, or an import is slow or
  failing.
compatibility: Any language with a Bolt-compatible driver. Memgraph instance required; cross_database procedures need the memgraph-mage image.
metadata:
  version: "0.0.1"
  author: memgraph
---

# Importing data into Memgraph

Work through these questions in order and take the first route that fits:

1. **Is it a `.cypherl` dump?** Pipe it into `mgconsole` (Memgraph Lab for under a million
   objects). No modelling is needed; the statements already are the model.
2. **Is it a flat file (CSV, Parquet, JSON Lines), or can the source export one cheaply?**
   Put the file where the server can read it (local disk, `http(s)://`, `ftp://`, `s3://`,
   or `docker cp` into the container) and use `LOAD CSV`, `LOAD PARQUET` or `LOAD JSONL`.
   This is the fastest and simplest route; prefer it even if it means exporting first.
3. **Is it a JSON array or nested JSON?** `json_util.load_from_path()` / `load_from_url()`
   with `UNWIND`, or `import_util.json()` for files written by `export_util.json()`.
4. **Is it in another database (PostgreSQL, MySQL, SQL Server, Oracle, DuckDB, Neo4j,
   Memgraph) and is `cross_database` available?** It needs the memgraph-mage image and, since
   3.13, an Enterprise license. Stream it straight into `CREATE`/`MERGE`. Without
   `cross_database`, export to CSV and go back to step 2.
5. **Does it arrive from Kafka or Pulsar?** Use the built-in stream consumers with a
   transformation module; that is a separate topic.
6. **Otherwise** write a client script that sends parameterised `UNWIND $rows AS row` batches.
   This covers data that lives only on the client, needs transformation or validation in code,
   arrives incrementally, or is part of a larger pipeline.

## Choose a route

| Source | Route |
|---|---|
| CSV file the **server** can read (local disk, `http(s)://`, `ftp://`, `s3://`; gzip/bzip2 ok) | `LOAD CSV` |
| Parquet file, same locations as CSV | `LOAD PARQUET` |
| JSON Lines file, same locations as CSV | `LOAD JSONL` |
| JSON array or arbitrary JSON | `json_util.load_from_path()` / `load_from_url()` + `UNWIND` |
| JSON produced by `export_util.json()` | `import_util.json()` |
| CSV/JSON on the **client** machine only, or data needing transformation | Client script: parameterised `UNWIND $rows AS row` batches |
| PostgreSQL, MySQL, SQL Server, Oracle, DuckDB | `cross_database.<source>()` streamed straight into `CREATE`/`MERGE` |
| Neo4j or another Memgraph | `cross_database.neo4j()` / `cross_database.bolt()`, or a CYPHERL dump |
| `.cypherl` file (one statement per line) | Pipe into `mgconsole`; Memgraph Lab for < 1M objects |
| Kafka (or a Kafka-compatible broker such as Redpanda) / Pulsar | Built-in stream consumers with a transformation module (separate topic) |

`cross_database` was named `migrate` before Memgraph 3.11; the old `migrate.*` names still work as
aliases. Since 3.13 the module needs an Enterprise license.

## File paths resolve on the server

`LOAD CSV`, `LOAD PARQUET`, `LOAD JSONL` and `json_util.load_from_path()` open the path on the machine
running Memgraph, not where the client runs. With Docker, copy the file in first or mount a volume:

```bash
docker cp people.csv memgraph:/usr/lib/memgraph/people.csv
# or at start-up
docker run -p 7687:7687 -v /host/data:/data memgraph/memgraph-mage
```

Memgraph Cloud cannot read local files; upload to a public URL or S3 and load from there.

## Remote files and S3 credentials

`LOAD CSV`, `LOAD PARQUET` and `LOAD JSONL` all accept `http://`, `https://`, `ftp://` and `s3://`
locations as well as local paths. Remote files are downloaded to `/tmp` on the server before
parsing, so the server needs disk space and network access to the source.

For `s3://` locations, credentials can come from three places. The query wins over the server
environment, which wins over database settings:

```cypher
-- 1. In the query, for query-specific credentials
LOAD CSV FROM "s3://my-bucket/people.csv"
WITH CONFIG {"aws_region": "eu-central-1", "aws_access_key": $key, "aws_secret_key": $secret}
WITH HEADER AS row
CREATE (:Person {id: toInteger(row.id)});

-- 3. Database settings, persisted on the server
SET DATABASE SETTING 'aws.region' TO 'eu-central-1';
SET DATABASE SETTING 'aws.access_key' TO '...';
SET DATABASE SETTING 'aws.secret_key' TO '...';
```

```bash
# 2. Server environment, set before Memgraph starts
AWS_REGION=eu-central-1 AWS_ACCESS_KEY=... AWS_SECRET_KEY=...
```

The config map keys must be quoted strings; unquoted keys are a parse error. Add
`"aws_endpoint_url"` (or `AWS_ENDPOINT_URL` / `aws.endpoint_url`) for S3-compatible services such
as RustFS. Pass secrets as query parameters rather than literals so they stay out of query logs.
The `cross_database.s3()` procedure is different: it takes boto-style keys (`aws_access_key_id`,
`aws_secret_access_key`, `region_name`) and has no endpoint key, so an S3-compatible store needs
`AWS_ENDPOINT_URL` in the server environment. See the reference.

## Before loading

1. **Inspect a sample** of the file: delimiter, header, quoting, encoding, empty cells, number and
   date formats. `head -5 file.csv` is enough.
2. **Design the model**: which columns become node labels, which become relationships, and which
   column uniquely identifies each node. Keep nodes and relationships in separate files when you can.
3. **Create indexes on every property you `MATCH` or `MERGE` on** before importing, otherwise every
   relationship row scans all nodes. A constraint does not create an index.
   ```cypher
   CREATE INDEX ON :Person(id);
   ```
4. **Consider analytical storage mode** for large imports. It drops the per-write `Delta` objects,
   so loading is up to 6x faster with far less memory, but there are no ACID guarantees or WAL
   while it is on. Switching between the two in-memory modes works with data present; Memgraph
   waits for other transactions to finish first, and switching back writes a snapshot before it
   completes. Only a switch to or from on-disk mode needs an empty database. Confirm with the
   user before switching, and switch back afterwards.
   ```cypher
   STORAGE MODE IN_MEMORY_ANALYTICAL;
   SHOW STORAGE INFO ON CURRENT DATABASE;   -- storage_mode; the unscoped form shows the start-up default
   -- ... import ...
   STORAGE MODE IN_MEMORY_TRANSACTIONAL;
   ```

## LOAD CSV

```
LOAD CSV FROM <location> [WITH CONFIG {...}] (WITH | NO) HEADER
  [IGNORE BAD] [DELIMITER ","] [QUOTE "\""] [NULLIF ""] AS row
```

Nodes first:

```cypher
LOAD CSV FROM "/data/people.csv" WITH HEADER NULLIF "" AS row
CREATE (:Person {id: toInteger(row.id), name: row.name, age: toInteger(row.age)});
```

Then relationships, matching on the indexed property:

```cypher
LOAD CSV FROM "/data/knows.csv" WITH HEADER AS row
MATCH (a:Person {id: toInteger(row.from_id)}), (b:Person {id: toInteger(row.to_id)})
CREATE (a)-[:KNOWS {since: toInteger(row.since)}]->(b);
```

Rules that bite:

- **Every value is a string.** Cast explicitly: `toInteger`, `toFloat`, `toBoolean`, `date()`,
  `localDateTime()`. Compare `toInteger(row.id)` with an integer property, never `row.id`.
- **Empty cells are empty strings**, not null, unless you add `NULLIF ""`.
- `WITH HEADER` gives `row.column`; `NO HEADER` gives `row[0]`, `row[1]`.
- `IGNORE BAD` skips malformed rows instead of aborting on the first one.
- `LOAD CSV` can appear once per query and cannot stand alone. A `MATCH` or `MERGE` before it must
  not return more than one row, or the query fails with "LOAD CSV can be executed only once".
- `CREATE` is faster than `MERGE`. Use `MERGE` only when the file may contain duplicates or the
  nodes may already exist, and index the merge key first.
- Labels and relationship types can come from the file: `CREATE (n:row.label ...)`,
  `CREATE (a)-[:row.type]->(b)`.

### Batching in transactional mode

A single `LOAD CSV` runs as one transaction. For millions of rows in `IN_MEMORY_TRANSACTIONAL`
mode, commit in batches to bound memory:

```cypher
USING PERIODIC COMMIT 10000
LOAD CSV FROM "/data/people.csv" WITH HEADER AS row
CREATE (:Person {id: toInteger(row.id), name: row.name});
```

or

```cypher
LOAD CSV FROM "/data/people.csv" WITH HEADER AS row
CALL {
  WITH row
  CREATE (:Person {id: toInteger(row.id), name: row.name})
} IN TRANSACTIONS OF 10000 ROWS;
```

Each batch commits separately, so a failure halfway leaves earlier batches in place.

### Parallel LOAD CSV

In `IN_MEMORY_ANALYTICAL` mode, split a big file into chunks and run one `LOAD CSV` per chunk from
parallel client connections, with at least as many chunks as CPU cores. Load **all** node files
before **any** relationship file; concurrent node and relationship imports in analytical mode can
leave relationships without endpoints.

## LOAD PARQUET and LOAD JSONL

Same shape as `LOAD CSV`, but typed values come through as-is:

```cypher
LOAD PARQUET FROM "/data/people.parquet" AS row
CREATE (:Person {id: row.id, name: row.name});

LOAD JSONL FROM "https://example.com/people.jsonl" AS row
CREATE (n:Person) SET n += row;
```

## JSON

For a file holding a JSON array of objects (needs MAGE):

```cypher
CALL json_util.load_from_path("/data/people.json") YIELD objects
UNWIND objects AS o
CREATE (:Person {id: o.id, name: o.name, pets: o.pets});
```

`json_util.load_from_url("https://...")` is identical for remote files. Only use
`import_util.json()` for files written by `export_util.json()`; it expects the node/relationship
envelope format with `type`, `labels`, `properties`, `start` and `end` fields.

When the JSON is already a string inside the query, such as a client parameter or a CSV column
holding embedded JSON, parse it inline with the C++ `convert` functions rather than loading a
file. They ship in the base `memgraph/memgraph` image, and the docs prefer them over
`json_util.from_json_list()` / `to_json()`:

```cypher
UNWIND convert.from_json_list($payload) AS o
CREATE (:Event {id: o.id, kind: o.kind});

LOAD CSV FROM "/data/orders.csv" WITH HEADER AS row
WITH row, convert.from_json_map(row.address) AS addr
CREATE (:Order {id: toInteger(row.id), city: addr.city});
```

## Client-driven batches

When the file is only on the client machine, or rows need code to transform them, send
parameterised batches of 1,000 to 10,000 rows. One `UNWIND` per batch is far faster than one
statement per row, and the Bolt driver handles the transaction.

```python
from neo4j import GraphDatabase

def chunks(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i:i + size]

with GraphDatabase.driver("bolt://localhost:7687", auth=("", "")) as driver:
    with driver.session() as session:            # index DDL needs an autocommit query
        session.run("CREATE INDEX ON :Person(id);").consume()
    for batch in chunks(rows, 5000):            # rows: list of dicts
        driver.execute_query(
            "UNWIND $rows AS row "
            "MERGE (p:Person {id: row.id}) SET p.name = row.name, p.age = row.age",
            rows=batch,
        )
```

`execute_query` runs inside a managed transaction, and Memgraph refuses index and constraint
changes there ("Index manipulation is not allowed in multicommand transactions"), so schema
statements go through a plain `session.run`.

For parallel loading use processes, not threads, one driver per process, and never more
processes than hardware threads. In transactional mode, concurrent writers that touch the same
node raise `Cannot resolve conflicting transactions`; retry the batch with a short exponential
backoff plus jitter, inside an explicit transaction rather than autocommit. Supernodes make these
conflicts frequent; load their relationships from a single process.

## Relational databases and Neo4j

`cross_database` procedures stream rows from the source into the same query, so there is no
intermediate file. Create indexes and pick a storage mode first, exactly as for CSV. Pass a
`SELECT` with only the columns you need rather than a bare table name to cut per-row memory.

```cypher
CALL cross_database.postgresql(
  'SELECT musician_id, name, instrument FROM musicians',
  {user: 'postgres', password: $pw, host: 'db.internal', database: 'music'})
YIELD row
CREATE (:Musician {id: row.musician_id, name: row.name, instrument: row.instrument});
```

Join tables become relationships:

```cypher
CALL cross_database.postgresql(
  'SELECT musician_id, band_id FROM band_memberships',
  {user: 'postgres', password: $pw, host: 'db.internal', database: 'music'})
YIELD row
MATCH (m:Musician {id: row.musician_id}), (b:Band {id: row.band_id})
CREATE (m)-[:PERFORMS_IN]->(b);
```

`mysql`, `sql_server`, `oracle_db`, `duckdb`, `s3`, `arrow_flight` and `servicenow` follow the same
pattern, but the config map is passed straight to the underlying Python driver, so the keys differ
per source: `pyodbc` wants `driver`/`server`/`uid`/`pwd` and `oracledb` wants a `dsn`, and Oracle
returns upper-case column names. See [REFERENCE.md](references/REFERENCE.md) for signatures and a
tested example of each.

From Neo4j, `cross_database.neo4j()` accepts a Cypher query, a node pattern like `"(:Person)"` or a
relationship pattern like `"[:KNOWS]"`. The whole-graph recipe merges nodes on a temporary
`__MigrationNode__` label keyed by the Neo4j `elementId`, then drops it; it is in REFERENCE.md.
Neo4j and Memgraph must listen on different Bolt ports on the same host. Indexes and constraints
are not carried over; recreate them by hand.

## CYPHERL files

One statement per line. Pipe into `mgconsole`:

```bash
cat dump.cypherl | mgconsole --host 127.0.0.1 --port 7687
# Docker
docker cp dump.cypherl memgraph:/tmp/dump.cypherl
docker exec -i memgraph sh -c 'cat /tmp/dump.cypherl | mgconsole'
```

`mgconsole --import_mode=batched-parallel` splits the file and loads it with several connections.
Memgraph Lab's CYPHERL import is capped at 1 million nodes and relationships.

## After loading

1. **Verify counts** against the source and spot-check a few records:
   ```cypher
   MATCH (n:Person) RETURN count(n);
   MATCH ()-[r:KNOWS]->() RETURN count(r);
   MATCH (n:Person) RETURN n LIMIT 5;
   ```
2. **Look for orphans**: relationship rows whose endpoints did not match are silently dropped by
   `MATCH ... CREATE`. Compare the relationship count with the file's row count.
3. **Switch storage mode back** if you changed it, then `ANALYZE GRAPH;` so the planner has
   statistics for the new data.
4. **Check memory** with `SHOW STORAGE INFO;` (`peak_memory_res`). If the import blew past the
   limit in transactional mode, rerun with smaller batches.
5. **Report** rows read, nodes and relationships created, anything skipped, and the exact Cypher
   used so the user can rerun it.

## Common failures

| Symptom | Cause and fix |
|---|---|
| `CSV file not found: /path` | Path was resolved on the server. Copy or mount the file into the container, or use a URL. |
| Relationships missing, nodes present | Type mismatch on the key (`"1"` vs `1`), or nodes loaded after relationships. Cast and reorder. |
| Import is slow, CPU idle | No index on the `MATCH`/`MERGE` property. `EXPLAIN` shows `ScanAll`; create the index. |
| `Memory limit exceeded` / OOM | Single huge transaction in transactional mode. Use `USING PERIODIC COMMIT`, `IN TRANSACTIONS`, or analytical mode. |
| `Cannot resolve conflicting transactions` | Parallel writers on the same nodes. Retry with backoff, serialise supernode batches, or use analytical mode. |
| Empty-cell values stored as `""` | Add `NULLIF ""` or wrap with `CASE WHEN row.x = "" THEN null ELSE row.x END`. |
| `There is no procedure named cross_database...` | Image is `memgraph/memgraph` not `memgraph/memgraph-mage`, or Memgraph < 3.11 (use `migrate.*`), or missing Enterprise license on >= 3.13. |

## Additional resources

- [REFERENCE.md](references/REFERENCE.md): `LOAD CSV` clause details, memory and durability
  during a big import, a parallel client loader with retry, `cross_database` signatures and
  examples per source, and the Neo4j whole-graph migration.
- Memgraph docs: Data migration section, `LOAD CSV` clause, `cross_database` module.
