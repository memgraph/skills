# Python Query Modules API Reference

## mgp Module Types

### mgp.Vertex

Represents a graph node (vertex).

| Property/Method | Type | Description |
|-----------------|------|-------------|
| `id` | `int` | Unique vertex identifier |
| `labels` | `Iterable[Label]` | Vertex labels |
| `properties` | `Properties` | Vertex properties (dict-like) |
| `in_edges` | `Iterable[Edge]` | Incoming edges |
| `out_edges` | `Iterable[Edge]` | Outgoing edges |
| `add_label(name)` | `None` | Add a label (write proc only) |
| `remove_label(name)` | `None` | Remove a label (write proc only) |

### mgp.Edge

Represents a relationship (edge) between vertices.

| Property/Method | Type | Description |
|-----------------|------|-------------|
| `id` | `int` | Unique edge identifier |
| `type` | `EdgeType` | Edge type/relationship type |
| `from_vertex` | `Vertex` | Source vertex |
| `to_vertex` | `Vertex` | Target vertex |
| `properties` | `Properties` | Edge properties (dict-like) |

### mgp.Path

Represents a path through the graph.

| Property/Method | Type | Description |
|-----------------|------|-------------|
| `vertices` | `List[Vertex]` | Vertices in path |
| `edges` | `List[Edge]` | Edges in path |
| `expand(edge)` | `None` | Extend path with edge |

### mgp.Properties

Dict-like collection of properties.

| Method | Description |
|--------|-------------|
| `get(key, default=None)` | Get property value |
| `items()` | Iterate key-value pairs |
| `keys()` | Iterate keys |
| `values()` | Iterate values |
| `__getitem__(key)` | Get property by key |
| `__setitem__(key, value)` | Set property (write proc only) |
| `__contains__(key)` | Check if key exists |

### mgp.Label

Represents a vertex label.

| Property | Type | Description |
|----------|------|-------------|
| `name` | `str` | Label name |

### mgp.EdgeType

Represents a relationship type.

| Property | Type | Description |
|----------|------|-------------|
| `name` | `str` | Type name |

### mgp.Record

Return type for procedures. Created with field specifications.

```python
# Define return fields
mgp.Record(field1=type1, field2=type2, ...)

# Create instance with values
mgp.Record(field1=value1, field2=value2, ...)
```

### mgp.ProcCtx

Procedure execution context.

| Property/Method | Type | Description |
|-----------------|------|-------------|
| `graph` | `Graph` | Access to graph |
| `check_must_abort()` | `bool` | Check if procedure should terminate |

### mgp.FuncCtx

Function execution context.

| Property | Type | Description |
|----------|------|-------------|
| `graph` | `Graph` | Read-only graph access |

### mgp.Graph

Graph access object.

| Property/Method | Type | Description |
|-----------------|------|-------------|
| `vertices` | `Iterable[Vertex]` | All vertices |
| `edges` | `Iterable[Edge]` | All edges |
| `get_vertex_by_id(id)` | `Vertex` | Get vertex by ID |
| `create_vertex()` | `Vertex` | Create new vertex (write proc only) |
| `create_edge(from, to, type)` | `Edge` | Create edge (write proc only) |
| `delete_vertex(vertex)` | `None` | Delete vertex (write proc only) |
| `delete_edge(edge)` | `None` | Delete edge (write proc only) |

## Type Annotations

| Type | Description |
|------|-------------|
| `mgp.Any` | Any supported Cypher type |
| `mgp.Nullable[T]` | Optional type (can be null) |
| `mgp.List[T]` | List of type T |
| `mgp.Map` | Dictionary/map type |
| `mgp.Number` | Numeric type (int or float) |

## Decorators

### @mgp.read_proc

Register a read-only procedure.

```python
@mgp.read_proc
def my_procedure(
    context: mgp.ProcCtx,
    param1: type1,
    param2: type2 = default
) -> mgp.Record(field1=type1, field2=type2):
    ...
```

### @mgp.write_proc

Register a procedure that can modify the graph.

```python
@mgp.write_proc
def my_procedure(
    context: mgp.ProcCtx,
    param1: type1
) -> mgp.Record(result=type):
    ...
```

### @mgp.function

Register a user-defined function.

```python
@mgp.function
def my_function(
    context: mgp.FuncCtx,
    param1: type1
) -> return_type:
    ...
```

## Batch Procedures

```python
def init_func(context: mgp.ProcCtx, ...):
    """Called once before batch processing."""
    pass

def cleanup_func():
    """Called once after batch processing."""
    pass

@mgp.read_proc
def batch_proc(context: mgp.ProcCtx, ...) -> mgp.Record(...):
    """Called repeatedly for each batch."""
    pass

# Register batch procedure
mgp.add_batch_read_proc(batch_proc, init_func, cleanup_func)
```

## Logging

```python
logger = mgp.Logger()

logger.trace("Trace message")
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

## Exceptions

| Exception | Description |
|-----------|-------------|
| `mgp.AbortError` | Procedure was terminated |
| `mgp.InvalidContextError` | Invalid execution context |
| `IndexError` | Vertex/edge not found by ID |

## Module Locations

| Path | Description |
|------|-------------|
| `/usr/lib/memgraph/query_modules/` | System modules |
| `/var/lib/memgraph/internal_modules/` | User modules (Memgraph Lab) |
| `/usr/lib/memgraph/python_support/` | mgp module location |

## Cypher Commands

```cypher
-- Load all modules
CALL mg.load_all();

-- Load specific module
CALL mg.load("module_name");

-- List all procedures
CALL mg.procedures() YIELD *;

-- List all functions  
CALL mg.functions() YIELD *;

-- Call a procedure
CALL module_name.procedure_name(args) YIELD field1, field2;

-- Use a function
RETURN module_name.function_name(args);
```
