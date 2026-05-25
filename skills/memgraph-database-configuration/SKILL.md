---
name: memgraph-database-configuration
description: >-
  Configure Memgraph triggers, transactions, storage modes, data durability,
  and memory settings. Use when the user asks about triggers, transaction
  isolation levels, storage modes (transactional vs analytical), snapshots,
  WAL, memory limits, data types, or database runtime configuration.
compatibility: Any language with a Bolt-compatible driver. Memgraph instance required.
metadata:
  version: "0.0.1"
  author: memgraph
---

# Database Configuration in Memgraph

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
| `Enum` | Must be defined first (see `memgraph-indexes-and-constraints`) |
| `Point` | 2D/3D, Cartesian or WGS-84 |

Lists and Maps cannot be mutated element-by-element - replace the whole value.

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
| `IN_MEMORY_TRANSACTIONAL` | Full | Yes | Yes | Default - concurrent reads/writes |
| `IN_MEMORY_ANALYTICAL` | No | No | Manual only | Bulk import, analytics (up to 6x faster) |
| `ON_DISK_TRANSACTIONAL` | Snapshot isolation | RocksDB | - | Experimental, larger-than-memory |

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

## Key rules

1. Snapshots and WAL are not compatible across Memgraph versions
2. Cannot use WAL without snapshots enabled
3. Cannot switch in-memory to on-disk storage with data present
4. `IN_MEMORY_ANALYTICAL` has no isolation levels or ACID guarantees
5. Descending indexes and automatic index creation only work in `IN_MEMORY_TRANSACTIONAL` (see `memgraph-indexes-and-constraints`)
