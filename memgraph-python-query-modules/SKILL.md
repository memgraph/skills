---
name: memgraph-python-query-modules
version: 1.0.0
description: Develop custom query modules in Python for Memgraph graph database
category: database
tags:
  - database
  - graph-database
  - memgraph
  - python
  - query-modules
  - cypher
  - procedures
  - functions
author: Agent Skills
last_updated: 2026-01-12
---

# Memgraph Python Query Modules Skill

## Overview

This skill enables AI agents to develop custom query modules in Python for Memgraph. Query modules extend Memgraph's Cypher query language with user-defined procedures and functions that can perform complex graph algorithms, data transformations, and integrations with external systems.

## When to Use

Use this skill when you need to:
- Create custom graph algorithms not available in MAGE library
- Implement business-specific logic that runs directly in the database
- Build read-only procedures (`@mgp.read_proc`) for data analysis
- Build write procedures (`@mgp.write_proc`) for data modification
- Create user-defined functions (`@mgp.function`) for use in Cypher queries
- Integrate external Python libraries with graph processing
- Implement batch processing procedures for large datasets

## Prerequisites

- Memgraph instance running (preferably memgraph/memgraph-mage Docker image)
- Python 3.5.0 or above
- Basic understanding of Cypher query language
- Basic Python programming knowledge

## Python API Overview

The Python API is defined in the `mgp` module located at `/usr/lib/memgraph/python_support` in the Memgraph installation. Install it locally for development with:

```bash
pip install mgp
```

## Core Concepts

### 1. Procedures vs Functions

| Feature | Procedures | Functions |
|---------|------------|-----------|
| Decorator | `@mgp.read_proc` or `@mgp.write_proc` | `@mgp.function` |
| Cypher Usage | `CALL module.procedure() YIELD ...` | `RETURN module.function()` |
| Return Type | `mgp.Record` | Any supported type |
| Can Modify Graph | Yes (with `@mgp.write_proc`) | No |
| Multiple Results | Yes (iterable of Records) | Single value |

### 2. Key Data Types

| Type | Description |
|------|-------------|
| `mgp.Vertex` | Graph node with properties, labels, and edges |
| `mgp.Edge` | Relationship between vertices with type and properties |
| `mgp.Path` | Sequence of vertices and edges |
| `mgp.Record` | Return type for procedures |
| `mgp.ProcCtx` | Procedure execution context with graph access |
| `mgp.FuncCtx` | Function execution context |
| `mgp.Properties` | Collection of properties on vertex/edge |
| `mgp.Label` | Vertex label |
| `mgp.EdgeType` | Edge relationship type |

### 3. Type Annotations

```python
mgp.Any          # Any supported Cypher type
mgp.Nullable[T]  # Optional type (can be null)
mgp.List[T]      # List of type T
mgp.Map          # Dictionary/map type
```

## Creating Query Modules

### Basic Read Procedure

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

**Usage in Cypher:**
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

### Write Procedure (Modifies Graph)

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

**Usage in Cypher:**
```cypher
CALL module_name.create_person("Alice", 30) YIELD vertex
RETURN vertex;
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

**Usage in Cypher:**
```cypher
MATCH (p:Person)
RETURN module_name.full_name(p.first_name, p.last_name) AS name;
```

## Working with Graph Elements

### Vertex Operations

```python
import mgp

@mgp.read_proc
def analyze_vertex(
    context: mgp.ProcCtx,
    vertex: mgp.Vertex
) -> mgp.Record(
    id=int,
    labels=list,
    properties=dict,
    in_degree=int,
    out_degree=int
):
    """Analyze a vertex's structure."""
    return mgp.Record(
        id=vertex.id,
        labels=[label.name for label in vertex.labels],
        properties=dict(vertex.properties.items()),
        in_degree=len(list(vertex.in_edges)),
        out_degree=len(list(vertex.out_edges))
    )
```

### Edge Operations

```python
import mgp

@mgp.read_proc
def analyze_edge(
    context: mgp.ProcCtx,
    edge: mgp.Edge
) -> mgp.Record(
    id=int,
    type=str,
    from_id=int,
    to_id=int,
    properties=dict
):
    """Analyze an edge's structure."""
    return mgp.Record(
        id=edge.id,
        type=edge.type.name,
        from_id=edge.from_vertex.id,
        to_id=edge.to_vertex.id,
        properties=dict(edge.properties.items())
    )
```

### Path Operations

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

## Advanced Patterns

### Batch Processing

```python
import mgp

def init_batch(context: mgp.ProcCtx, batch_size: int):
    """Initialize batch processing."""
    global current_batch, vertices_iter
    current_batch = 0
    vertices_iter = iter(context.graph.vertices)

def cleanup_batch():
    """Cleanup after batch processing."""
    global current_batch, vertices_iter
    current_batch = None
    vertices_iter = None

@mgp.read_proc
def process_batch(
    context: mgp.ProcCtx,
    batch_size: int
) -> mgp.Record(vertex_id=int, processed=bool):
    """Process vertices in batches."""
    results = []
    for _ in range(batch_size):
        try:
            vertex = next(vertices_iter)
            # Process vertex...
            results.append(mgp.Record(vertex_id=vertex.id, processed=True))
        except StopIteration:
            break
    return results if results else None

# Register as batch procedure
mgp.add_batch_read_proc(process_batch, init_batch, cleanup_batch)
```

### Terminating Long-Running Procedures

```python
import mgp

@mgp.read_proc
def long_running_analysis(
    context: mgp.ProcCtx
) -> mgp.Record(result=int):
    """A procedure that can be terminated."""
    count = 0
    try:
        for vertex in context.graph.vertices:
            # Check if procedure should abort
            if context.check_must_abort():
                break
            # Expensive computation...
            count += 1
    except mgp.AbortError:
        return mgp.Record(result=count)
    
    return mgp.Record(result=count)
```

### Using External Libraries

```python
import mgp

# Import external libraries (must be installed in Memgraph container)
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
    
    # Build NetworkX graph
    G = nx.DiGraph()
    for vertex in context.graph.vertices:
        G.add_node(vertex.id)
    for vertex in context.graph.vertices:
        for edge in vertex.out_edges:
            G.add_edge(vertex.id, edge.to_vertex.id)
    
    # Calculate PageRank
    ranks = nx.pagerank(G, alpha=damping)
    
    return [mgp.Record(node_id=nid, rank=rank) 
            for nid, rank in ranks.items()]
```

### Logging

```python
import mgp

@mgp.read_proc
def procedure_with_logging(
    context: mgp.ProcCtx
) -> mgp.Record(status=str):
    """Procedure that logs its progress."""
    logger = mgp.Logger()
    
    logger.info("Starting procedure execution")
    logger.debug("Debug information")
    
    try:
        # Do work...
        logger.info("Procedure completed successfully")
        return mgp.Record(status="success")
    except Exception as e:
        logger.error(f"Procedure failed: {e}")
        raise
```

## Module File Structure

Query module files should be placed in:
- `/usr/lib/memgraph/query_modules/` - System modules
- `/var/lib/memgraph/internal_modules/` - User modules (via Memgraph Lab)

File naming convention:
- `my_module.py` → accessed as `my_module.procedure_name()`

## Deploying Query Modules

### Method 1: Copy to Container

```bash
# Copy module file to running container
docker cp my_module.py memgraph:/usr/lib/memgraph/query_modules/

# Reload modules in Memgraph
echo "CALL mg.load_all();" | docker exec -i memgraph mgconsole
```

### Method 2: Volume Mount

```bash
docker run -d \
  -p 7687:7687 \
  -v $(pwd)/modules:/usr/lib/memgraph/query_modules \
  --name memgraph \
  memgraph/memgraph-mage
```

### Method 3: Memgraph Lab

1. Open Memgraph Lab
2. Navigate to Query Modules
3. Click "New Module"
4. Write your Python code
5. Save and the module is automatically loaded

## Loading and Managing Modules

```cypher
-- Load all modules
CALL mg.load_all();

-- Load specific module
CALL mg.load("my_module");

-- List all procedures
CALL mg.procedures() YIELD *;

-- List all functions
CALL mg.functions() YIELD *;
```

## Installing External Python Libraries

```bash
# Install library in Memgraph container
docker exec -i -u memgraph memgraph bash -c "pip install pandas networkx"

# Reload modules to pick up new libraries
echo "CALL mg.load_all();" | docker exec -i memgraph mgconsole
```

## Complete Example: Graph Analytics Module

```python
"""
graph_analytics.py - Custom graph analytics procedures
"""
import mgp
from typing import List, Dict, Any

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


@mgp.read_proc
def find_hubs(
    context: mgp.ProcCtx,
    min_connections: int = 10
) -> mgp.Record(vertex=mgp.Vertex, connections=int):
    """Find vertices with high connectivity (hubs)."""
    results = []
    
    for vertex in context.graph.vertices:
        connections = len(list(vertex.in_edges)) + len(list(vertex.out_edges))
        if connections >= min_connections:
            results.append(mgp.Record(
                vertex=vertex,
                connections=connections
            ))
    
    # Sort by connections descending
    results.sort(key=lambda r: r.connections, reverse=True)
    return results


@mgp.read_proc
def shortest_path_length(
    context: mgp.ProcCtx,
    start: mgp.Vertex,
    end: mgp.Vertex
) -> mgp.Record(length=int, found=bool):
    """Find shortest path length using BFS."""
    if start.id == end.id:
        return mgp.Record(length=0, found=True)
    
    visited = {start.id}
    queue = [(start, 0)]
    
    while queue:
        current, distance = queue.pop(0)
        
        for edge in current.out_edges:
            neighbor = edge.to_vertex
            if neighbor.id == end.id:
                return mgp.Record(length=distance + 1, found=True)
            if neighbor.id not in visited:
                visited.add(neighbor.id)
                queue.append((neighbor, distance + 1))
    
    return mgp.Record(length=-1, found=False)


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


@mgp.function
def vertex_degree(
    context: mgp.FuncCtx,
    vertex: mgp.Vertex
) -> int:
    """Calculate the total degree of a vertex."""
    return len(list(vertex.in_edges)) + len(list(vertex.out_edges))
```

**Usage:**
```cypher
-- Get degree distribution
CALL graph_analytics.degree_distribution() 
YIELD degree, count
RETURN degree, count
ORDER BY degree;

-- Find hubs with at least 5 connections
CALL graph_analytics.find_hubs(5) 
YIELD vertex, connections
RETURN vertex.name, connections;

-- Find shortest path length
MATCH (a:Person {name: 'Alice'}), (b:Person {name: 'Bob'})
CALL graph_analytics.shortest_path_length(a, b) 
YIELD length, found
RETURN length, found;

-- Use function in query
MATCH (p:Person)
RETURN p.name, graph_analytics.vertex_degree(p) AS degree
ORDER BY degree DESC;
```

## Error Handling

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
        raise Exception("Invalid context - procedure called incorrectly")
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")
```

## Testing with Mock API

The mock Python API allows testing without a running Memgraph instance:

```python
import mgp
from mgp import mock_memgraph_db

# Create mock database
db = mock_memgraph_db.MockMemgraphDb()

# Add test data
db.execute("CREATE (a:Person {name: 'Alice'})-[:KNOWS]->(b:Person {name: 'Bob'})")

# Test your procedure
result = db.call_procedure("my_module.my_procedure", ["arg1", "arg2"])
print(result)
```

## Best Practices

1. **Type Annotations**: Always fully annotate function signatures
2. **Documentation**: Use docstrings for all procedures and functions
3. **Error Handling**: Raise meaningful exceptions with clear messages
4. **Memory Management**: Avoid storing graph objects globally (they become invalid)
5. **Performance**: Use `context.check_must_abort()` in long-running procedures
6. **Testing**: Use the mock API for unit testing
7. **Naming**: Use descriptive names for modules and procedures
8. **Modularity**: Keep procedures focused on single responsibilities

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Module not found | Run `CALL mg.load_all();` to reload modules |
| Import error | Install missing library in Memgraph container |
| InvalidContextError | Don't store graph objects globally |
| Type error | Ensure all parameters have type annotations |
| Permission denied | Check file permissions in query_modules directory |

## References

- [Memgraph Python API Documentation](https://memgraph.com/docs/custom-query-modules/python/python-api)
- [Mock Python API](https://memgraph.com/docs/custom-query-modules/python/mock-python-api)
- [Python Query Module Examples](https://memgraph.com/docs/custom-query-modules/python/python-example)
- [Managing Query Modules](https://memgraph.com/docs/custom-query-modules/manage-query-modules)
- [MAGE Library (existing algorithms)](https://github.com/memgraph/mage)
