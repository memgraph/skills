---
name: memgraph-indexes-and-database-administration
description: >-
  Create and manage Memgraph indexes, constraints, triggers, enums, transactions,
  storage modes, and data durability settings. Use when the user asks about
  indexing strategy, schema enforcement, data type constraints, triggers,
  transaction isolation, storage modes, snapshots, WAL, or performance tuning via
  schema-level DDL.
compatibility: Any language with a Bolt-compatible driver. Memgraph instance required.
integrations:
  - memgraph-lab>=3.11
metadata:
  version: "0.0.1"
  author: memgraph
---

# Managing Indexes & Schema in Memgraph

## Indexes

Indexes are NOT created automatically unless explicitly enabled via flags.
Adding an index speeds reads but slows writes and uses extra memory.

### Index types

| Type | Create | Drop |
|------|--------|------|
| Label | `CREATE INDEX ON :Label;` | `DROP INDEX ON :Label;` |
| Label-property | `CREATE INDEX ON :Label(prop);` | `DROP INDEX ON :Label(prop);` |
| Composite | `CREATE INDEX ON :Label(p1, p2);` | `DROP INDEX ON :Label(p1, p2);` |
| Descending | `CREATE INDEX ON :L(p) WITH CONFIG {"order": "DESC"};` | `DROP INDEX ON :L(p) WITH CONFIG {"order": "DESC"};` |
| Edge-type | `CREATE EDGE INDEX ON :TYPE;` | `DROP EDGE INDEX ON :TYPE;` |
| Edge-type property | `CREATE EDGE INDEX ON :TYPE(prop);` | `DROP EDGE INDEX ON :TYPE(prop);` |
| Global edge property | `CREATE GLOBAL EDGE INDEX ON :(prop);` | `DROP GLOBAL EDGE INDEX ON :(prop);` |
| Point | `CREATE POINT INDEX ON :L(prop);` | `DROP POINT INDEX ON :L(prop);` |
| Text | `CREATE TEXT INDEX name ON :L;` | `DROP TEXT INDEX name;` |
| Vector | `CREATE VECTOR INDEX name ON :L(prop) WITH CONFIG {...};` | `DROP VECTOR INDEX name;` |
| Drop all | — | `DROP ALL INDEXES;` |

Show: `SHOW INDEX INFO;` or `SHOW INDEXES;`

### Label-property index

```cypher
CREATE INDEX ON :Person(age);
```

Creating a label-property index does NOT create a label index — create both if
needed. Best performance on high-cardinality properties (unique IDs, names).
Avoid on booleans or low-cardinality fields.

### Composite index

```cypher
CREATE INDEX ON :Person(name, occupation);
```

Follows the leftmost prefix rule:

| Query filters | Uses index? |
|---------------|-------------|
| `p0` | Yes |
| `p0, p1` | Yes |
| `p0, p1, p2` | Yes |
| `p0, p2` (skip p1) | Yes + extra filter |
| `p1` only | No |
| `p2` only | No |

Put highest-cardinality property first.

### Descending index

```cypher
CREATE INDEX ON :Person(age) WITH CONFIG {"order": "DESC"};
```

Optimizes `ORDER BY prop DESC` and top-N queries. ASC and DESC can coexist on
the same label+property. Only supported in `IN_MEMORY_TRANSACTIONAL`.

Dropping without config removes both ASC and DESC variants.

### Nested (map) property index

```cypher
CREATE INDEX ON :Project(delivery.status.due_date);
```

Must use `WHERE` clause to query — inline map matching won't use the index:

```cypher
-- Wrong (compares entire map):
MATCH (p:Project {delivery: {status: {due_date: date("2025-06-04")}}}) RETURN p;

-- Correct:
MATCH (p:Project) WHERE p.delivery.status.due_date = date("2025-06-04") RETURN p;
```

### Edge indexes

Require `--storage-properties-on-edges=true`.

```cypher
CREATE EDGE INDEX ON :KNOWS;
CREATE EDGE INDEX ON :KNOWS(since);
CREATE GLOBAL EDGE INDEX ON :(weight);
```

### Point index

```cypher
CREATE POINT INDEX ON :Location(coords);
MATCH (n:Location) WHERE point.distance(point({x:1, y:1}), n.coords) < 1000 RETURN n;
MATCH (n:Location) WHERE point.withinbbox(n.coords, point({x:0, y:0}), point({x:10, y:10})) RETURN n;
```

### Index hinting

```cypher
USING INDEX :Person(name)
MATCH (n:Person {name: "Alice", gender: "F"}) RETURN n;
```

### ANALYZE GRAPH

Run once after indexes are created and data is loaded:

```cypher
ANALYZE GRAPH;
ANALYZE GRAPH ON LABELS :Person, :City;
ANALYZE GRAPH DELETE STATISTICS;
```

Calculates property value distribution for optimal index and MERGE selection.
Statistics persist via snapshots/WAL.

### Automatic index creation

Only in `IN_MEMORY_TRANSACTIONAL`. Flags:

- `--storage-automatic-label-index-creation-enabled`
- `--storage-automatic-edge-type-index-creation-enabled`

### Concurrent index creation

Label, label-property, composite, and edge indexes are created concurrently.
Brief `READ ONLY` during registration phase (waits for pending writes), then
background indexing proceeds while reads and writes resume.

---

## Constraints

### Existence constraint

```cypher
CREATE CONSTRAINT ON (n:Employee) ASSERT EXISTS (n.first_name);
DROP CONSTRAINT ON (n:Employee) ASSERT EXISTS (n.first_name);
SHOW CONSTRAINT INFO;
```

One label + one property at a time.

### Uniqueness constraint

```cypher
CREATE CONSTRAINT ON (n:Employee) ASSERT n.email IS UNIQUE;
CREATE CONSTRAINT ON (n:Employee) ASSERT n.name, n.address IS UNIQUE;
DROP CONSTRAINT ON (n:Employee) ASSERT n.email IS UNIQUE;
```

Multi-property: same name OR same address is allowed; same name AND address is
forbidden. Uniqueness constraints do NOT create indexes — add them separately.

### Data type constraint

```cypher
CREATE CONSTRAINT ON (n:Person) ASSERT n.name IS TYPED STRING;
CREATE CONSTRAINT ON (n:Person) ASSERT n.age IS TYPED INTEGER;
DROP CONSTRAINT ON (n:Person) ASSERT n.name IS TYPED STRING;
```

Supported types: `NULL`, `STRING`, `BOOLEAN`, `INTEGER`, `FLOAT`, `LIST`, `MAP`,
`DURATION`, `DATE`, `LOCALTIME`, `LOCALDATETIME`, `ZONEDDATETIME`, `ENUM`, `POINT`.

Only one type constraint per label-property pair.

### Drop all

```cypher
DROP ALL CONSTRAINTS;
```

### Constraint behavior

Constraints are checked optimistically on commit. In multi-query explicit
transactions, intermediate violations are allowed as long as the final state
satisfies all constraints.

---

## Enums

```cypher
CREATE ENUM Status VALUES { Good, Okay, Bad };
SHOW ENUMS;
ALTER ENUM Status ADD VALUE Excellent;
ALTER ENUM Status UPDATE VALUE Bad TO Poor;
```

Use in queries:

```cypher
CREATE (:Machine {status: Status::Good});
MATCH (n:Machine) WHERE n.status = Status::Bad RETURN n;
RETURN ToEnum("Status", "Good");
RETURN ToEnum("Status::Okay");
```

Less memory and faster comparison than string properties.

---

## Triggers

### Syntax

```
CREATE TRIGGER name
  [SECURITY DEFINER|INVOKER]
  [ON [() | -->] CREATE|UPDATE|DELETE]
  [BEFORE|AFTER COMMIT]
  EXECUTE <cypher statements>
```

Default security: `DEFINER`. Triggers are persisted to disk.

### Predefined variables by event

| Event | Available variables |
|-------|--------------------|
| `ON () CREATE` | `createdVertices` |
| `ON --> CREATE` | `createdEdges` |
| `ON CREATE` | `createdVertices`, `createdEdges`, `createdObjects` |
| `ON () UPDATE` | `setVertexProperties`, `removedVertexProperties`, `setVertexLabels`, `removedVertexLabels`, `updatedVertices` |
| `ON --> UPDATE` | `setEdgeProperties`, `removedEdgeProperties`, `updatedEdges` |
| `ON UPDATE` | All update vars + `updatedObjects` |
| `ON () DELETE` | `deletedVertices` |
| `ON --> DELETE` | `deletedEdges` |
| `ON DELETE` | `deletedVertices`, `deletedEdges`, `deletedObjects` |
| No event | All variables available |

### Examples

Auto-set creation timestamp:

```cypher
CREATE TRIGGER setCreatedAt
ON () CREATE AFTER COMMIT EXECUTE
UNWIND createdVertices AS v SET v.created_at = timestamp();
```

Auto-set updated_at:

```cypher
CREATE TRIGGER setUpdatedAt
ON UPDATE AFTER COMMIT EXECUTE
UNWIND updatedObjects AS obj
WITH CASE
  WHEN obj.vertex IS NOT null THEN obj.vertex
  WHEN obj.edge IS NOT null THEN obj.edge
END AS entity
SET entity.updated_at = timestamp();
```

Dynamic PageRank via trigger:

```cypher
CREATE TRIGGER pagerankTrigger
BEFORE COMMIT EXECUTE
CALL pagerank_online.update(createdVertices, createdEdges, deletedVertices, deletedEdges)
YIELD node, rank SET node.rank = rank;
```

### Manage

```cypher
DROP TRIGGER name;
SHOW TRIGGERS;
```

---

## Transactions

### Explicit transactions

```cypher
BEGIN;
MATCH (n:Account {id: 1}) SET n.balance = n.balance - 100;
MATCH (n:Account {id: 2}) SET n.balance = n.balance + 100;
COMMIT;
```

`ROLLBACK;` to discard. If any query fails, the transaction cannot be committed.

### Show and terminate

```cypher
SHOW TRANSACTIONS;
SHOW RUNNING TRANSACTIONS;
TERMINATE TRANSACTIONS "tid1", "tid2";
```

Requires `TRANSACTION_MANAGEMENT` privilege to see/terminate other users' transactions.

### Isolation levels

```cypher
SET GLOBAL TRANSACTION ISOLATION LEVEL SNAPSHOT ISOLATION;
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
SET NEXT TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
SHOW STORAGE INFO;
```

| Level | Default | Protects against |
|-------|---------|------------------|
| `SNAPSHOT ISOLATION` | Yes (IN_MEMORY_TRANSACTIONAL) | Dirty read, non-repeatable read, phantom |
| `READ COMMITTED` | | Dirty read |
| `READ UNCOMMITTED` | | Nothing (read-only access) |

`IN_MEMORY_ANALYTICAL` has no isolation levels.
`ON_DISK_TRANSACTIONAL` supports only `SNAPSHOT ISOLATION`.

---

## Data types

### Property types

| Type | Notes |
|------|-------|
| `Null` | Same as property absent |
| `String` | |
| `Boolean` | |
| `Integer` | |
| `Float` | Resolution via `--storage-floating-point-resolution-bits` |
| `List` | Homogeneous for storage as node property |
| `Map` | Must replace entirely |
| `Duration` | `duration("P2DT3H")` |
| `Date` | `date("2024-01-15")` |
| `LocalTime` | `localTime("14:30:00")` |
| `LocalDateTime` | `localDateTime("2024-01-15T14:30:00")` |
| `ZonedDateTime` | `datetime("2024-01-15T14:30:00Z")` |
| `Enum` | Must be defined first |
| `Point` | 2D/3D, Cartesian or WGS-84 |

Lists and Maps cannot be mutated element-by-element — replace the whole value.

### Temporal arithmetic

Duration +/- Duration = Duration. Date +/- Duration = Date. Date - Date = Duration.
Same for LocalTime, LocalDateTime, ZonedDateTime.

### Point types

| Type | SRID | Constructor |
|------|------|-------------|
| WGS-84 2D | 4326 | `point({longitude: -73.93, latitude: 40.73})` |
| WGS-84 3D | 4979 | `point({longitude: -73.93, latitude: 40.73, height: 10})` |
| Cartesian 2D | 7203 | `point({x: 0, y: 1})` |
| Cartesian 3D | 9157 | `point({x: 0, y: 1, z: 2})` |

---

## Storage modes

```cypher
STORAGE MODE IN_MEMORY_TRANSACTIONAL;
STORAGE MODE IN_MEMORY_ANALYTICAL;
STORAGE MODE ON_DISK_TRANSACTIONAL;
SHOW STORAGE INFO;
```

| Mode | ACID | WAL | Periodic snapshots | Use case |
|------|------|-----|-------------------|----------|
| `IN_MEMORY_TRANSACTIONAL` | Full | Yes | Yes | Default — concurrent reads/writes |
| `IN_MEMORY_ANALYTICAL` | No | No | Manual only | Bulk import, analytics (up to 6x faster) |
| `ON_DISK_TRANSACTIONAL` | Snapshot isolation | RocksDB | — | Experimental, larger-than-memory |

Cannot switch in-memory to on-disk with data present. Cannot switch with active transactions.

---

## Data durability

### Snapshots

```cypher
CREATE SNAPSHOT;
SHOW SNAPSHOTS;
```

Periodic interval (runtime):

```cypher
SET DATABASE SETTING "storage.snapshot.interval" TO "1200";
SET DATABASE SETTING "storage.snapshot.interval" TO "* * 12 * * *";
```

Flags: `--storage-snapshot-interval`, `--storage-snapshot-on-exit`,
`--storage-parallel-snapshot-creation`.

### WAL

Enabled by default (`--storage-wal-enabled`). Cannot use WAL without snapshots.
Older WAL files are deleted after each snapshot.

### Data directory management

```cypher
LOCK DATA DIRECTORY;
UNLOCK DATA DIRECTORY;
DATA DIRECTORY LOCK STATUS;
```

### Memory management

```cypher
MATCH (n) RETURN n QUERY MEMORY LIMIT 50 MB;
CALL proc() PROCEDURE MEMORY LIMIT 100 MB YIELD *;
FREE MEMORY;
SHOW STORAGE INFO;
```

Instance limit: `--memory-limit` (MiB). Property compression:
`--storage-property-store-compression-enabled`.

### Memory estimation

```
RAM ≈ nodes × 204B + edges × 154B + properties + indexes
```

For 50+ indexes add ~20% overhead.

---

## Storage access

Index/constraint/enum DDL requires exclusive (unique) access — briefly blocks
other queries during execution. Normal Cypher queries use shared access.

Timeout for write access during index creation:

```cypher
SET DATABASE SETTING 'storage.access_timeout_sec' TO '30';
```

---

## Key rules summary

1. Indexes are not auto-created unless flags are enabled (IN_MEMORY_TRANSACTIONAL only)
2. Uniqueness constraints do NOT create indexes — add them separately
3. Label-property index does NOT imply a label index
4. Composite index follows the leftmost prefix rule
5. Nested map indexes require WHERE clause, not inline map matching
6. Edge indexes require `--storage-properties-on-edges=true`
7. Descending indexes only work in IN_MEMORY_TRANSACTIONAL
8. Run `ANALYZE GRAPH` once after data load for optimal index selection
9. `DROP INDEX` without config drops both ASC and DESC variants
10. Constraints are checked on commit (optimistic)
11. Snapshots and WAL are not compatible across Memgraph versions
