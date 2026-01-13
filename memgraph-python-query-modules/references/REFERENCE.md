# Python Query Modules Reference

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

### mgp.Label / mgp.EdgeType

| Property | Type | Description |
|----------|------|-------------|
| `name` | `str` | Label or edge type name |

### mgp.Record

Return type for procedures.

```python
mgp.Record(field1=type1, field2=type2, ...)  # Define fields
mgp.Record(field1=value1, field2=value2, ...) # Create instance
```

### mgp.ProcCtx / mgp.FuncCtx

| Property/Method | Type | Description |
|-----------------|------|-------------|
| `graph` | `Graph` | Access to graph |
| `check_must_abort()` | `bool` | Check if procedure should terminate (ProcCtx only) |

### mgp.Graph

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

| Decorator | Description |
|-----------|-------------|
| `@mgp.read_proc` | Register read-only procedure |
| `@mgp.write_proc` | Register procedure that can modify graph |
| `@mgp.function` | Register user-defined function |

## Logging

```python
logger = mgp.Logger()
logger.info("Info message")
logger.debug("Debug message")
logger.error("Error message")
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

## Cypher Commands

```cypher
CALL mg.load_all();                              -- Load all modules
CALL mg.load("module_name");                     -- Load specific module
CALL mg.procedures() YIELD *;                    -- List procedures
CALL mg.functions() YIELD *;                     -- List functions
CALL module_name.procedure_name(args) YIELD f1;  -- Call procedure
RETURN module_name.function_name(args);          -- Use function
```

---

## Examples

### Read Procedure with Graph Traversal

```python
import mgp
from typing import Dict

@mgp.read_proc
def degree_distribution(
    context: mgp.ProcCtx
) -> mgp.Record(degree=int, count=int):
    """Calculate the degree distribution of the graph."""
    distribution: Dict[int, int] = {}
    
    for vertex in context.graph.vertices:
        degree = len(list(vertex.in_edges)) + len(list(vertex.out_edges))
        distribution[degree] = distribution.get(degree, 0) + 1
    
    return [mgp.Record(degree=d, count=c) 
            for d, c in sorted(distribution.items())]
```

```cypher
CALL module.degree_distribution() YIELD degree, count
RETURN degree, count ORDER BY degree;
```

### Write Procedure

```python
import mgp

@mgp.write_proc
def add_computed_property(
    context: mgp.ProcCtx,
    property_name: str
) -> mgp.Record(updated_count=int):
    """Add a computed degree property to all vertices."""
    count = 0
    for vertex in context.graph.vertices:
        degree = len(list(vertex.in_edges)) + len(list(vertex.out_edges))
        vertex.properties[property_name] = degree
        count += 1
    return mgp.Record(updated_count=count)
```

### User-Defined Function

```python
import mgp

@mgp.function
def vertex_degree(context: mgp.FuncCtx, vertex: mgp.Vertex) -> int:
    """Calculate the total degree of a vertex."""
    return len(list(vertex.in_edges)) + len(list(vertex.out_edges))
```

```cypher
MATCH (p:Person)
RETURN p.name, module.vertex_degree(p) AS degree;
```

### Path Building (Random Walk)

```python
import mgp
import random

@mgp.read_proc
def random_walk(
    context: mgp.ProcCtx,
    start: mgp.Vertex,
    length: int = 10
) -> mgp.Record(path=mgp.Path):
    """Generate a random walk path from start vertex."""
    path = mgp.Path(start)
    vertex = start
    
    for _ in range(length):
        edges = list(vertex.out_edges)
        if not edges:
            break
        edge = random.choice(edges)
        path.expand(edge)
        vertex = edge.to_vertex
    
    return mgp.Record(path=path)
```

### Error Handling

```python
import mgp

@mgp.read_proc
def safe_procedure(
    context: mgp.ProcCtx,
    vertex_id: int
) -> mgp.Record(result=str):
    """Procedure with proper error handling."""
    try:
        vertex = context.graph.get_vertex_by_id(vertex_id)
        return mgp.Record(result=f"Found vertex: {vertex.id}")
    except IndexError:
        raise Exception(f"Vertex with ID {vertex_id} not found")
    except mgp.InvalidContextError:
        raise Exception("Invalid context")
```

### Long-Running with Abort Check

```python
import mgp

@mgp.read_proc
def long_running_analysis(context: mgp.ProcCtx) -> mgp.Record(result=int):
    """A procedure that can be terminated."""
    count = 0
    for vertex in context.graph.vertices:
        if context.check_must_abort():
            break
        count += 1
    return mgp.Record(result=count)
```
