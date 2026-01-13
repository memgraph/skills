---
name: memgraph-python-query-modules
description: Develop custom query modules in Python for Memgraph graph database. Use when creating custom graph algorithms, procedures (@mgp.read_proc, @mgp.write_proc), or functions (@mgp.function) for Memgraph. Covers the mgp Python API, graph traversal, data transformations, and module deployment.
compatibility: Requires Memgraph instance (Docker recommended), Python 3.5+
metadata:
  version: "1.0.0"
  author: memgraph
---

# Memgraph Python Query Modules

Develop custom query modules in Python for Memgraph graph database.

## When to Use

- Create custom graph algorithms not available in MAGE library
- Implement business-specific logic that runs directly in the database
- Build read-only procedures (`@mgp.read_proc`) for data analysis
- Build write procedures (`@mgp.write_proc`) for data modification
- Create user-defined functions (`@mgp.function`) for use in Cypher queries
- Integrate external Python libraries with graph processing

## Prerequisites

- Memgraph instance running (preferably `memgraph/memgraph-mage` Docker image)
- Python 3.5.0+
- Install mgp locally for development: `pip install mgp`

## Quick Reference

| Feature | Procedures | Functions |
|---------|------------|-----------|
| Decorator | `@mgp.read_proc` / `@mgp.write_proc` | `@mgp.function` |
| Cypher | `CALL module.proc() YIELD ...` | `RETURN module.func()` |
| Return Type | `mgp.Record` | Any supported type |
| Modify Graph | Yes (with `@mgp.write_proc`) | No |

### Key Types

| Type | Description |
|------|-------------|
| `mgp.Vertex` | Graph node with properties, labels, edges |
| `mgp.Edge` | Relationship with type and properties |
| `mgp.Path` | Sequence of vertices and edges |
| `mgp.Record` | Return type for procedures |
| `mgp.ProcCtx` | Procedure context with graph access |
| `mgp.FuncCtx` | Function context |

## Basic Patterns

### Read Procedure

```python
import mgp

@mgp.read_proc
def hello_world(
    context: mgp.ProcCtx,
    name: str
) -> mgp.Record(message=str):
    """A simple hello world procedure."""
    return mgp.Record(message=f"Hello, {name}!")
```

```cypher
CALL module_name.hello_world("Memgraph") YIELD message;
```

### Read Procedure with Graph Access

```python
import mgp

@mgp.read_proc
def count_nodes_by_label(
    context: mgp.ProcCtx,
    label_name: str
) -> mgp.Record(count=int):
    """Count nodes with a specific label."""
    count = 0
    for vertex in context.graph.vertices:
        for label in vertex.labels:
            if label.name == label_name:
                count += 1
                break
    return mgp.Record(count=count)
```

### Write Procedure

```python
import mgp

@mgp.write_proc
def create_person(
    context: mgp.ProcCtx,
    name: str,
    age: mgp.Nullable[int] = None
) -> mgp.Record(vertex=mgp.Vertex):
    """Create a new Person node."""
    vertex = context.graph.create_vertex()
    vertex.add_label("Person")
    vertex.properties["name"] = name
    if age is not None:
        vertex.properties["age"] = age
    return mgp.Record(vertex=vertex)
```

### User-Defined Function

```python
import mgp

@mgp.function
def full_name(
    context: mgp.FuncCtx,
    first_name: str,
    last_name: str
) -> str:
    """Concatenate first and last name."""
    return f"{first_name} {last_name}"
```

```cypher
MATCH (p:Person)
RETURN module_name.full_name(p.first_name, p.last_name) AS name;
```

### Returning Multiple Records

```python
import mgp

@mgp.read_proc
def get_neighbors(
    context: mgp.ProcCtx,
    node: mgp.Vertex
) -> mgp.Record(neighbor=mgp.Vertex, edge_type=str):
    """Get all neighbors of a node."""
    results = []
    for edge in node.out_edges:
        results.append(mgp.Record(
            neighbor=edge.to_vertex,
            edge_type=edge.type.name
        ))
    for edge in node.in_edges:
        results.append(mgp.Record(
            neighbor=edge.from_vertex,
            edge_type=edge.type.name
        ))
    return results
```

## Working with Graph Elements

### Vertex Operations

```python
# Access vertex properties
vertex.id                    # Unique identifier
vertex.labels               # Iterable of labels
vertex.properties           # Dict-like properties
vertex.in_edges             # Incoming edges
vertex.out_edges            # Outgoing edges

# Modify (write procedures only)
vertex.add_label("Label")
vertex.remove_label("Label")
vertex.properties["key"] = value
```

### Edge Operations

```python
edge.id                     # Unique identifier
edge.type                   # EdgeType object
edge.type.name              # Relationship type name
edge.from_vertex            # Source vertex
edge.to_vertex              # Target vertex
edge.properties             # Dict-like properties
```

### Path Operations

```python
path = mgp.Path(start_vertex)
path.expand(edge)           # Extend path
path.vertices               # List of vertices
path.edges                  # List of edges
```

## Advanced Patterns

### Long-Running Procedures with Abort Check

```python
@mgp.read_proc
def long_running_analysis(
    context: mgp.ProcCtx
) -> mgp.Record(result=int):
    """A procedure that can be terminated."""
    count = 0
    try:
        for vertex in context.graph.vertices:
            if context.check_must_abort():
                break
            # Expensive computation...
            count += 1
    except mgp.AbortError:
        pass
    return mgp.Record(result=count)
```

### Using External Libraries

```python
import mgp

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False

@mgp.read_proc
def pagerank(
    context: mgp.ProcCtx,
    damping: float = 0.85
) -> mgp.Record(node_id=int, rank=float):
    """Calculate PageRank using NetworkX."""
    if not HAS_NETWORKX:
        raise Exception("NetworkX not installed")
    
    G = nx.DiGraph()
    for vertex in context.graph.vertices:
        G.add_node(vertex.id)
    for vertex in context.graph.vertices:
        for edge in vertex.out_edges:
            G.add_edge(vertex.id, edge.to_vertex.id)
    
    ranks = nx.pagerank(G, alpha=damping)
    return [mgp.Record(node_id=nid, rank=rank) 
            for nid, rank in ranks.items()]
```

### Logging

```python
import mgp

logger = mgp.Logger()
logger.trace("Trace message")
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

## Deployment

### Module Locations

| Path | Description |
|------|-------------|
| `/usr/lib/memgraph/query_modules/` | System modules |
| `/var/lib/memgraph/internal_modules/` | User modules (Memgraph Lab) |

### Copy to Container

```bash
docker cp my_module.py memgraph:/usr/lib/memgraph/query_modules/
echo "CALL mg.load_all();" | docker exec -i memgraph mgconsole
```

### Volume Mount

```bash
docker run -d \
  -p 7687:7687 \
  -v $(pwd)/modules:/usr/lib/memgraph/query_modules \
  --name memgraph \
  memgraph/memgraph-mage
```

### Install External Libraries

```bash
docker exec -i -u memgraph memgraph bash -c "pip install pandas networkx"
echo "CALL mg.load_all();" | docker exec -i memgraph mgconsole
```

## Module Management (Cypher)

```cypher
CALL mg.load_all();              -- Load all modules
CALL mg.load("module_name");     -- Load specific module
CALL mg.procedures() YIELD *;    -- List procedures
CALL mg.functions() YIELD *;     -- List functions
```

## Error Handling

```python
import mgp

@mgp.read_proc
def safe_procedure(
    context: mgp.ProcCtx,
    vertex_id: int
) -> mgp.Record(result=str):
    try:
        vertex = context.graph.get_vertex_by_id(vertex_id)
        return mgp.Record(result=f"Found vertex: {vertex.id}")
    except IndexError:
        raise Exception(f"Vertex with ID {vertex_id} not found")
    except mgp.InvalidContextError:
        raise Exception("Invalid context")
```

## Best Practices

1. **Type Annotations**: Always fully annotate function signatures
2. **Documentation**: Use docstrings for all procedures and functions
3. **Error Handling**: Raise meaningful exceptions with clear messages
4. **Memory**: Don't store graph objects globally (they become invalid)
5. **Performance**: Use `context.check_must_abort()` in long-running procedures
6. **Testing**: Use the mock API for unit testing

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Module not found | Run `CALL mg.load_all();` |
| Import error | Install library in Memgraph container |
| InvalidContextError | Don't store graph objects globally |
| Type error | Ensure all parameters have type annotations |

## Additional Resources

For detailed API documentation, see [references/REFERENCE.md](references/REFERENCE.md).

For complete examples, see [references/EXAMPLES.md](references/EXAMPLES.md).
