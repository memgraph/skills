# Rust Query Modules API Reference

Detailed API documentation for Memgraph Rust query modules using the `rsmgp-sys` crate.

## Core Types

### Memgraph

Main context for interacting with Memgraph. Created automatically and passed to procedures.

| Method | Return Type | Description |
|--------|-------------|-------------|
| `args()` | `Result<List>` | Get arguments passed to procedure |
| `result_record()` | `Result<ResultRecord>` | Create new result record |
| `vertices_iter()` | `Result<VerticesIterator>` | Iterator over all vertices |
| `vertex_by_id(id)` | `Result<Vertex>` | Get vertex by ID |
| `add_read_procedure(...)` | `Result<()>` | Register read procedure |
| `must_abort()` | `bool` | Check if procedure should abort |
| `module_ptr()` | `*mut mgp_module` | Get raw module pointer |

### Vertex

Represents a graph node (vertex).

| Method | Return Type | Description |
|--------|-------------|-------------|
| `id()` | `i64` | Returns vertex's unique identifier |
| `labels_count()` | `Result<u64>` | Returns number of labels |
| `label_at(index)` | `Result<CString>` | Get label at index |
| `has_label(name)` | `Result<bool>` | Check if vertex has label |
| `property(name)` | `Result<Property>` | Get property by name |
| `properties()` | `Result<PropertiesIterator>` | Iterator over properties |
| `in_edges()` | `Result<EdgesIterator>` | Incoming edges iterator |
| `out_edges()` | `Result<EdgesIterator>` | Outgoing edges iterator |

### Edge

Represents a relationship (edge) between vertices.

| Method | Return Type | Description |
|--------|-------------|-------------|
| `id()` | `i64` | Returns edge's unique identifier |
| `edge_type()` | `Result<CString>` | Returns relationship type |
| `from_vertex()` | `Result<Vertex>` | Returns source vertex |
| `to_vertex()` | `Result<Vertex>` | Returns destination vertex |
| `property(name)` | `Result<Property>` | Get property by name |
| `properties()` | `Result<PropertiesIterator>` | Iterator over properties |
| `copy()` | `Result<Edge>` | Create copy of edge |

### Path

Represents a path through the graph.

| Method | Return Type | Description |
|--------|-------------|-------------|
| `size()` | `u64` | Number of edges in path |
| `vertex_at(index)` | `Result<Vertex>` | Vertex at position index |
| `edge_at(index)` | `Result<Edge>` | Edge at position index |
| `make_with_start(vertex, memgraph)` | `Result<Path>` | Create path from start vertex |
| `expand(edge)` | `Result<()>` | Extend path with edge |

### Value

Generic value enum for any supported type.

```rust
pub enum Value {
    Null,
    Bool(bool),
    Int(i64),
    Float(f64),
    String(CString),
    Vertex(Vertex),
    Edge(Edge),
    Path(Path),
    List(List),
    Map(Map),
    Date(NaiveDate),
    LocalTime(NaiveTime),
    LocalDateTime(NaiveDateTime),
    Duration(chrono::Duration),
}
```

| Method | Return Type | Description |
|--------|-------------|-------------|
| `to_mgp_value(&memgraph)` | `Result<MgpValue>` | Convert to MgpValue |

### List

List container for values.

| Method | Return Type | Description |
|--------|-------------|-------------|
| `make_empty(capacity, memgraph)` | `Result<List>` | Create empty list with capacity |
| `copy()` | `Result<List>` | Create copy of list |
| `size()` | `u64` | Number of elements |
| `capacity()` | `u64` | Current capacity |
| `value_at(index)` | `Result<Value>` | Get value at index |
| `append(value)` | `Result<()>` | Append value (must have space) |
| `append_extend(value)` | `Result<()>` | Append value, extend if needed |
| `iter()` | `Result<ListIterator>` | Get iterator |

### Map

Key-value map container.

| Method | Return Type | Description |
|--------|-------------|-------------|
| `make_empty(memgraph)` | `Result<Map>` | Create empty map |
| `size()` | `u64` | Number of entries |
| `at(key)` | `Result<Value>` | Get value at key |
| `insert(key, value)` | `Result<()>` | Insert key-value pair |
| `iter()` | `Result<MapIterator>` | Get iterator |

### MapItem

Represents an item in a Map.

```rust
pub struct MapItem {
    pub key: CString,
    pub value: Value,
}
```

### Property

Represents a property with name and value.

```rust
pub struct Property {
    pub name: CString,
    pub value: Value,
}
```

### MgpValue

Low-level value wrapper for interacting with Memgraph C API.

| Method | Return Type | Description |
|--------|-------------|-------------|
| `to_value()` | `Result<Value>` | Convert to Value enum |
| `make_null(memgraph)` | `Result<MgpValue>` | Create null value |
| `make_bool(value, memgraph)` | `Result<MgpValue>` | Create bool value |
| `make_int(value, memgraph)` | `Result<MgpValue>` | Create int value |
| `make_double(value, memgraph)` | `Result<MgpValue>` | Create double value |
| `make_string(value, memgraph)` | `Result<MgpValue>` | Create string value |
| `make_list(list, memgraph)` | `Result<MgpValue>` | Create list value |
| `make_map(map, memgraph)` | `Result<MgpValue>` | Create map value |
| `make_vertex(vertex, memgraph)` | `Result<MgpValue>` | Create vertex value |
| `make_edge(edge, memgraph)` | `Result<MgpValue>` | Create edge value |
| `make_path(path, memgraph)` | `Result<MgpValue>` | Create path value |
| `make_date(date, memgraph)` | `Result<MgpValue>` | Create date value |
| `make_local_time(time, memgraph)` | `Result<MgpValue>` | Create local time value |
| `make_local_date_time(datetime, memgraph)` | `Result<MgpValue>` | Create local datetime |
| `make_duration(duration, memgraph)` | `Result<MgpValue>` | Create duration value |
| `is_null()` | `bool` | Check if null |
| `is_bool()` | `bool` | Check if bool |
| `is_int()` | `bool` | Check if int |
| `is_double()` | `bool` | Check if double |
| `is_string()` | `bool` | Check if string |
| `is_list()` | `bool` | Check if list |
| `is_map()` | `bool` | Check if map |
| `is_vertex()` | `bool` | Check if vertex |
| `is_edge()` | `bool` | Check if edge |
| `is_path()` | `bool` | Check if path |
| `is_date()` | `bool` | Check if date |
| `is_local_time()` | `bool` | Check if local time |
| `is_local_date_time()` | `bool` | Check if local datetime |
| `is_duration()` | `bool` | Check if duration |

### ResultRecord

Used to insert result fields.

| Method | Return Type | Description |
|--------|-------------|-------------|
| `create(memgraph)` | `Result<ResultRecord>` | Create new result record |
| `insert_mgp_value(field, value)` | `Result<()>` | Insert MgpValue |
| `insert_null(field)` | `Result<()>` | Insert null value |
| `insert_bool(field, value)` | `Result<()>` | Insert bool value |
| `insert_int(field, value)` | `Result<()>` | Insert int value |
| `insert_double(field, value)` | `Result<()>` | Insert double value |
| `insert_string(field, value)` | `Result<()>` | Insert string value |
| `insert_list(field, value)` | `Result<()>` | Insert list value |
| `insert_map(field, value)` | `Result<()>` | Insert map value |
| `insert_vertex(field, value)` | `Result<()>` | Insert vertex value |
| `insert_edge(field, value)` | `Result<()>` | Insert edge value |
| `insert_path(field, value)` | `Result<()>` | Insert path value |
| `insert_date(field, value)` | `Result<()>` | Insert date value |
| `insert_local_time(field, value)` | `Result<()>` | Insert local time |
| `insert_local_date_time(field, value)` | `Result<()>` | Insert local datetime |
| `insert_duration(field, value)` | `Result<()>` | Insert duration |

## Iterators

### VerticesIterator

Iterator over all vertices in the graph.

```rust
for vertex in memgraph.vertices_iter()? {
    // Process vertex
}
```

### EdgesIterator

Iterator over edges (incoming or outgoing).

```rust
for edge in vertex.out_edges()? {
    // Process edge
}
```

### PropertiesIterator

Iterator over properties of a vertex or edge.

```rust
for property in vertex.properties()? {
    println!("Property: {} = {:?}", property.name.to_str().unwrap(), property.value);
}
```

### ListIterator

Iterator over list elements.

```rust
for item in list.iter()? {
    // Process item
}
```

### MapIterator

Iterator over map entries.

```rust
for item in map.iter()? {
    println!("Key: {}, Value: {:?}", item.key.to_str().unwrap(), item.value);
}
```

## Type Enum

Used for procedure parameter and return type definitions.

| Type | Description |
|------|-------------|
| `Type::Null` | Null value |
| `Type::Bool` | Boolean |
| `Type::Int` | 64-bit integer |
| `Type::Double` | Double-precision float |
| `Type::String` | String |
| `Type::List` | List of values |
| `Type::Map` | Map of key-value pairs |
| `Type::Node` | Graph node (vertex) |
| `Type::Relationship` | Graph relationship (edge) |
| `Type::Path` | Graph path |
| `Type::Date` | Date |
| `Type::LocalTime` | Local time |
| `Type::LocalDateTime` | Local date-time |
| `Type::Duration` | Duration |
| `Type::Any` | Any type |

## Registration Macros

### init_module!

Initializes the module and registers procedures.

```rust
init_module!(|memgraph: &Memgraph| -> Result<()> {
    memgraph.add_read_procedure(
        procedure_fn,           // Function identifier
        c_str!("proc_name"),    // Procedure name
        &[/* required params */],
        &[/* optional params */],
        &[/* return fields */],
    )?;
    Ok(())
});
```

### define_procedure!

Defines a procedure implementation.

```rust
define_procedure!(my_procedure, |memgraph: &Memgraph| -> Result<()> {
    let args = memgraph.args()?;
    let result = memgraph.result_record()?;
    
    // Procedure logic here
    
    Ok(())
});
```

### close_module!

Cleanup when module is unloaded.

```rust
close_module!(|| -> Result<()> { Ok(()) });
```

### define_type!

Define a parameter or return type.

```rust
define_type!("param_name", Type::String)
define_type!("return_field", Type::Int)
```

### define_optional_type!

Define an optional parameter with default value.

```rust
define_optional_type!(
    "optional_param",
    &MgpValue::make_int(10, &memgraph)?,  // default value
    Type::Int
)
```

## add_read_procedure

Signature for registering a read procedure:

```rust
pub fn add_read_procedure(
    &self,
    proc_ptr: extern "C" fn(*mut mgp_list, *mut mgp_graph, *mut mgp_result, *mut mgp_memory),
    name: &CStr,
    required_arg_types: &[NamedType],
    optional_arg_types: &[OptionalNamedType],
    result_field_types: &[NamedType],
) -> Result<()>
```

## Error Handling

### MgpError

Low-level errors from Memgraph C API.

```rust
#[derive(Debug, PartialEq)]
pub enum MgpError {
    UnknownError,
    UnableToAllocate,
    InsufficientError,
    OutOfRange,
    LogicError,
    DeletedObject,
    InvalidArgument,
    KeyAlreadyExists,
    ImmutableObject,
    ValueConversion,
    SerializationError,
}
```

### Error

High-level Rust errors.

```rust
pub enum Error {
    UnableToCreateDateFromNaiveDate,
    UnableToCreateDurationFromChronoDuration,
    UnableToCopyEdge,
    UnableToReturnEdgePropertyValueAllocationError,
    UnableToReturnEdgePropertyValueCreationError,
    UnableToReturnEdgePropertyNameAllocationError,
    UnableToReturnEdgePropertyDeletedObjectError,
    UnableToReturnEdgePropertiesIterator,
    UnableToCreateEmptyList,
    UnableToCopyList,
    UnableToAppendListValue,
    UnableToAppendExtendListValue,
    UnableToAccessListValueByIndex,
    UnableToCreateLocalTimeFromNaiveTime,
    UnableToCreateLocalDateTimeFromNaiveDateTime,
    UnableToCopyMap,
    UnableToCreateEmptyMap,
    UnableToInsertMapValue,
    UnableToAccessMapValue,
    UnableToCreateMapIterator,
    UnableToCreateGraphVerticesIterator,
    UnableToFindVertexById,
    UnableToRegisterReadProcedure,
    UnableToAddRequiredArguments,
    UnableToAddOptionalArguments,
    UnableToAddReturnType,
    UnableToAddDeprecatedReturnType,
    UnableToCopyPath,
    OutOfBoundPathVertexIndex,
    OutOfBoundPathEdgeIndex,
    UnableToCreatePathWithStartVertex,
    UnableToExpandPath,
    UnableToCreateResultRecord,
    UnableToInsertResultValue,
    UnableToCreateCString,
    UnableToMakeNullValue,
    UnableToMakeBoolValue,
    UnableToMakeIntegerValue,
    UnableToMakeDoubleValue,
    UnableToMakeMemgraphStringValue,
    UnableToMakeListValue,
    UnableToMakeMapValue,
    UnableToMakeVertexValue,
    UnableToMakeEdgeValue,
    UnableToMakePathValue,
    UnableToMakeValueString,
    UnableToMakeDateValue,
    UnableToMakeLocalTimeValue,
    UnableToMakeLocalDateTimeValue,
    UnableToMakeDurationValue,
    UnableToCopyVertex,
    OutOfBoundLabelIndexError,
    UnableToGetVertexProperty,
    UnableToReturnVertexPropertyMakeNameEror,
    UnableToReturnVertexPropertiesIterator,
    UnableToReturnVertexInEdgesIterator,
    UnableToReturnVertexOutEdgesIterator,
    UnableToReturnVertexLabelsCountDeletedObjectError,
    UnableToReturnVertexLabelDeletedObjectError,
    UnableToCheckVertexHasLabel,
}
```

### Result Type

```rust
pub type Result<T, E = Error> = std::result::Result<T, E>;
```

## Date/Time Types

Uses the `chrono` crate for date/time handling.

### Date

```rust
use rsmgp_sys::date::Date;
use chrono::NaiveDate;

// Create from NaiveDate
let naive_date = NaiveDate::from_ymd(2024, 1, 15);
let date = Date::from_naive_date(&naive_date, &memgraph)?;

// Access components
let year = date.year();   // i32
let month = date.month(); // u32
let day = date.day();     // u32

// Convert back to NaiveDate
let naive = date.to_naive_date();
```

### LocalTime

```rust
use rsmgp_sys::local_time::LocalTime;
use chrono::NaiveTime;

// Create from NaiveTime
let naive_time = NaiveTime::from_hms(14, 30, 0);
let time = LocalTime::from_naive_time(&naive_time, &memgraph)?;

// Access components
let hour = time.hour();           // u32
let minute = time.minute();       // u32
let second = time.second();       // u32
let millisecond = time.millisecond(); // u32
let microsecond = time.microsecond(); // u32
let timestamp = time.timestamp(); // i64

// Convert back to NaiveTime
let naive = time.to_naive_time();
```

### LocalDateTime

```rust
use rsmgp_sys::local_date_time::LocalDateTime;
use chrono::NaiveDateTime;

// Create from NaiveDateTime
let datetime = LocalDateTime::from_naive_date_time(&naive_datetime, &memgraph)?;

// Access components
let year = datetime.year();
let month = datetime.month();
let day = datetime.day();
let hour = datetime.hour();
let minute = datetime.minute();
let second = datetime.second();
let millisecond = datetime.millisecond();
let microsecond = datetime.microsecond();

// Convert back
let naive = datetime.to_naive_date_time();
```

### Duration

```rust
use rsmgp_sys::duration::Duration;
use chrono::Duration as ChronoDuration;

// Create from chrono::Duration
let chrono_dur = ChronoDuration::hours(2) + ChronoDuration::minutes(30);
let duration = Duration::from_chrono_duration(&chrono_dur, &memgraph)?;

// Convert back
let chrono = duration.to_chrono_duration();
```

## File Structure

| Path | Description |
|------|-------------|
| `/mage/rust/` | Rust modules source directory |
| `/mage/rust/rsmgp-sys/` | Memgraph Rust bindings crate |
| `/mage/rust/rsmgp-example/` | Example module template |
| `/mage/dist/` | Built module output |
| `/usr/lib/memgraph/query_modules/` | Module installation directory |

## Cypher Commands

```cypher
CALL mg.load_all();                              -- Load all modules
CALL mg.load("module_name");                     -- Load specific module
CALL mg.procedures() YIELD *;                    -- List procedures
CALL module_name.procedure_name(args) YIELD f1;  -- Call procedure
```

---

## Examples

### Degree Distribution Analysis

```rust
use c_str_macro::c_str;
use rsmgp_sys::memgraph::*;
use rsmgp_sys::mgp::*;
use rsmgp_sys::result::*;
use rsmgp_sys::rsmgp::*;
use rsmgp_sys::value::*;
use rsmgp_sys::{close_module, define_procedure, define_type, init_module};
use std::collections::HashMap;

init_module!(|memgraph: &Memgraph| -> Result<()> {
    memgraph.add_read_procedure(
        degree_distribution,
        c_str!("degree_distribution"),
        &[],
        &[],
        &[
            define_type!("degree", Type::Int),
            define_type!("count", Type::Int),
        ],
    )?;
    Ok(())
});

define_procedure!(degree_distribution, |memgraph: &Memgraph| -> Result<()> {
    let mut distribution: HashMap<i64, i64> = HashMap::new();
    
    for vertex in memgraph.vertices_iter()? {
        let mut degree: i64 = 0;
        for _ in vertex.in_edges()? {
            degree += 1;
        }
        for _ in vertex.out_edges()? {
            degree += 1;
        }
        *distribution.entry(degree).or_insert(0) += 1;
    }
    
    let mut sorted: Vec<_> = distribution.into_iter().collect();
    sorted.sort_by_key(|&(degree, _)| degree);
    
    for (degree, count) in sorted {
        let result = memgraph.result_record()?;
        result.insert_int(c_str!("degree"), degree)?;
        result.insert_int(c_str!("count"), count)?;
    }
    
    Ok(())
});

close_module!(|| -> Result<()> { Ok(()) });
```

### Find Shortest Path (BFS)

```rust
use std::collections::{HashMap, HashSet, VecDeque};

define_procedure!(bfs_path, |memgraph: &Memgraph| -> Result<()> {
    let args = memgraph.args()?;
    let result = memgraph.result_record()?;
    
    let start_id = if let Value::Int(id) = args.value_at(0)? { id } else { return Ok(()); };
    let end_id = if let Value::Int(id) = args.value_at(1)? { id } else { return Ok(()); };
    
    let start = memgraph.vertex_by_id(start_id)?;
    
    let mut visited: HashSet<i64> = HashSet::new();
    let mut parent: HashMap<i64, i64> = HashMap::new();
    let mut queue: VecDeque<i64> = VecDeque::new();
    
    queue.push_back(start_id);
    visited.insert(start_id);
    
    while let Some(current_id) = queue.pop_front() {
        if current_id == end_id {
            // Reconstruct path length
            let mut path_len: i64 = 0;
            let mut curr = end_id;
            while curr != start_id {
                if let Some(&p) = parent.get(&curr) {
                    curr = p;
                    path_len += 1;
                } else {
                    break;
                }
            }
            result.insert_int(c_str!("path_length"), path_len)?;
            return Ok(());
        }
        
        let current = memgraph.vertex_by_id(current_id)?;
        for edge in current.out_edges()? {
            let neighbor = edge.to_vertex()?;
            let neighbor_id = neighbor.id();
            if !visited.contains(&neighbor_id) {
                visited.insert(neighbor_id);
                parent.insert(neighbor_id, current_id);
                queue.push_back(neighbor_id);
            }
        }
    }
    
    result.insert_int(c_str!("path_length"), -1)?;  // Not found
    Ok(())
});
```

### PageRank Algorithm

```rust
use std::collections::HashMap;

define_procedure!(pagerank, |memgraph: &Memgraph| -> Result<()> {
    let args = memgraph.args()?;
    
    let damping = if let Value::Float(d) = args.value_at(0)? { d } else { 0.85 };
    let iterations = if let Value::Int(i) = args.value_at(1)? { i } else { 10 };
    
    // Build graph structure
    let mut nodes: Vec<i64> = Vec::new();
    let mut out_edges: HashMap<i64, Vec<i64>> = HashMap::new();
    let mut in_edges: HashMap<i64, Vec<i64>> = HashMap::new();
    
    for vertex in memgraph.vertices_iter()? {
        let id = vertex.id();
        nodes.push(id);
        out_edges.entry(id).or_insert_with(Vec::new);
        in_edges.entry(id).or_insert_with(Vec::new);
        
        for edge in vertex.out_edges()? {
            let target = edge.to_vertex()?.id();
            out_edges.entry(id).or_insert_with(Vec::new).push(target);
            in_edges.entry(target).or_insert_with(Vec::new).push(id);
        }
    }
    
    let n = nodes.len() as f64;
    let mut ranks: HashMap<i64, f64> = nodes.iter().map(|&id| (id, 1.0 / n)).collect();
    
    // Iterate
    for _ in 0..iterations {
        let mut new_ranks: HashMap<i64, f64> = HashMap::new();
        
        for &node in &nodes {
            let mut rank = (1.0 - damping) / n;
            
            if let Some(incoming) = in_edges.get(&node) {
                for &src in incoming {
                    let out_degree = out_edges.get(&src).map(|v| v.len()).unwrap_or(1) as f64;
                    rank += damping * ranks.get(&src).unwrap_or(&0.0) / out_degree;
                }
            }
            
            new_ranks.insert(node, rank);
        }
        
        ranks = new_ranks;
    }
    
    // Output results
    for (node_id, rank) in ranks {
        let result = memgraph.result_record()?;
        result.insert_int(c_str!("node_id"), node_id)?;
        result.insert_double(c_str!("rank"), rank)?;
    }
    
    Ok(())
});
```

# Full Rust API

For the complete Rust API documentation, visit:
- [Rust API Documentation](https://memgraph.com/docs/custom-query-modules/rust/rust-api)
- [Rust Example](https://memgraph.com/docs/custom-query-modules/rust/rust-example)
- [MAGE GitHub - Rust](https://github.com/memgraph/mage/tree/main/rust)
