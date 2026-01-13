# Python Query Modules Examples

## Complete Graph Analytics Module

```python
"""
graph_analytics.py - Custom graph analytics procedures for Memgraph
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

**Cypher Usage:**
```cypher
-- Get degree distribution
CALL graph_analytics.degree_distribution() 
YIELD degree, count
RETURN degree, count ORDER BY degree;

-- Find hubs
CALL graph_analytics.find_hubs(5) 
YIELD vertex, connections
RETURN vertex.name, connections;

-- Shortest path
MATCH (a:Person {name: 'Alice'}), (b:Person {name: 'Bob'})
CALL graph_analytics.shortest_path_length(a, b) 
YIELD length, found
RETURN length, found;

-- Use function
MATCH (p:Person)
RETURN p.name, graph_analytics.vertex_degree(p) AS degree;
```

---

## Random Walk Procedure

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

---

## PageRank with NetworkX

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

---

## Batch Processing Example

```python
import mgp

vertices_iter = None
current_batch = 0

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
    global vertices_iter
    results = []
    
    for _ in range(batch_size):
        try:
            vertex = next(vertices_iter)
            # Process vertex...
            results.append(mgp.Record(vertex_id=vertex.id, processed=True))
        except StopIteration:
            break
    
    return results if results else None

mgp.add_batch_read_proc(process_batch, init_batch, cleanup_batch)
```

---

## Procedure with Logging

```python
import mgp

@mgp.read_proc
def procedure_with_logging(
    context: mgp.ProcCtx
) -> mgp.Record(status=str):
    """Procedure that logs its progress."""
    logger = mgp.Logger()
    
    logger.info("Starting procedure execution")
    
    try:
        count = 0
        for vertex in context.graph.vertices:
            count += 1
            if count % 1000 == 0:
                logger.debug(f"Processed {count} vertices")
        
        logger.info(f"Procedure completed: processed {count} vertices")
        return mgp.Record(status="success")
    except Exception as e:
        logger.error(f"Procedure failed: {e}")
        raise
```

---

## Long-Running Procedure with Abort Check

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
            if context.check_must_abort():
                break
            # Expensive computation...
            count += 1
    except mgp.AbortError:
        pass
    
    return mgp.Record(result=count)
```

---

## Error Handling Example

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

---

## Testing with Mock API

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

---

## Community Detection Example

```python
import mgp
from collections import defaultdict

@mgp.read_proc
def label_propagation(
    context: mgp.ProcCtx,
    max_iterations: int = 10
) -> mgp.Record(vertex=mgp.Vertex, community=int):
    """Simple label propagation community detection."""
    # Initialize each node with its own community
    communities = {v.id: v.id for v in context.graph.vertices}
    vertices = list(context.graph.vertices)
    
    for _ in range(max_iterations):
        changed = False
        
        for vertex in vertices:
            if context.check_must_abort():
                break
            
            # Count neighbor communities
            neighbor_communities = defaultdict(int)
            for edge in vertex.out_edges:
                neighbor_communities[communities[edge.to_vertex.id]] += 1
            for edge in vertex.in_edges:
                neighbor_communities[communities[edge.from_vertex.id]] += 1
            
            if neighbor_communities:
                # Assign most common neighbor community
                best_community = max(neighbor_communities, 
                                     key=neighbor_communities.get)
                if communities[vertex.id] != best_community:
                    communities[vertex.id] = best_community
                    changed = True
        
        if not changed:
            break
    
    return [mgp.Record(vertex=v, community=communities[v.id]) 
            for v in vertices]
```
