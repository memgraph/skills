# C++ Query Modules Reference

## mgp.hpp Types

### mgp::Node

Represents a graph node (vertex).

| Method | Return Type | Description |
|--------|-------------|-------------|
| `Id()` | `mgp::Id` | Returns the node's unique identifier |
| `Labels()` | `Labels` | Returns iterable of node labels |
| `HasLabel(label)` | `bool` | Check if node has label |
| `Properties()` | `unordered_map` | Returns all properties |
| `GetProperty(key)` | `Value` | Get property value |
| `SetProperty(key, value)` | `void` | Set property (write proc only) |
| `RemoveProperty(key)` | `void` | Remove property (write proc only) |
| `AddLabel(label)` | `void` | Add label (write proc only) |
| `RemoveLabel(label)` | `void` | Remove label (write proc only) |
| `InRelationships()` | `Relationships` | Incoming edges |
| `OutRelationships()` | `Relationships` | Outgoing edges |
| `InDegree()` | `size_t` | Incoming edge count |
| `OutDegree()` | `size_t` | Outgoing edge count |
| `ToString()` | `std::string` | String representation |

### mgp::Relationship

Represents an edge between nodes.

| Method | Return Type | Description |
|--------|-------------|-------------|
| `Id()` | `mgp::Id` | Returns relationship's unique identifier |
| `Type()` | `std::string_view` | Returns relationship type |
| `From()` | `Node` | Returns source node |
| `To()` | `Node` | Returns destination node |
| `Properties()` | `unordered_map` | Returns all properties |
| `GetProperty(key)` | `Value` | Get property value |
| `SetProperty(key, value)` | `void` | Set property (write proc only) |
| `RemoveProperty(key)` | `void` | Remove property (write proc only) |
| `ToString()` | `std::string` | String representation |

### mgp::Path

Represents a path through the graph.

| Method | Return Type | Description |
|--------|-------------|-------------|
| `Length()` | `size_t` | Number of relationships in path |
| `GetNodeAt(index)` | `Node` | Node at position index |
| `GetRelationshipAt(index)` | `Relationship` | Relationship at position index |
| `Expand(rel)` | `void` | Extend path with relationship |
| `Pop()` | `void` | Remove last node and relationship |
| `ToString()` | `std::string` | String representation |

### mgp::Value

Generic value container for any supported type.

| Method | Return Type | Description |
|--------|-------------|-------------|
| `Type()` | `mgp::Type` | Get the value's type enum |
| `IsNull()` | `bool` | Check if null |
| `IsBool()` | `bool` | Check if bool |
| `IsInt()` | `bool` | Check if int |
| `IsDouble()` | `bool` | Check if double |
| `IsString()` | `bool` | Check if string |
| `IsNode()` | `bool` | Check if node |
| `IsRelationship()` | `bool` | Check if relationship |
| `IsPath()` | `bool` | Check if path |
| `IsList()` | `bool` | Check if list |
| `IsMap()` | `bool` | Check if map |
| `ValueBool()` | `bool` | Get bool value |
| `ValueInt()` | `int64_t` | Get int value |
| `ValueDouble()` | `double` | Get double value |
| `ValueString()` | `std::string_view` | Get string value |
| `ValueNode()` | `Node` | Get node value |
| `ValueRelationship()` | `Relationship` | Get relationship value |
| `ValuePath()` | `Path` | Get path value |
| `ValueList()` | `List` | Get list value |
| `ValueMap()` | `Map` | Get map value |
| `ToString()` | `std::string` | String representation |

### mgp::Graph

Access to the Memgraph graph.

| Method | Return Type | Description |
|--------|-------------|-------------|
| `Order()` | `int64_t` | Number of nodes |
| `Size()` | `int64_t` | Number of relationships |
| `Nodes()` | `GraphNodes` | Iterable of all nodes |
| `Relationships()` | `GraphRelationships` | Iterable of all relationships |
| `GetNodeById(id)` | `Node` | Get node by ID |
| `ContainsNode(node)` | `bool` | Check if node exists |
| `ContainsRelationship(rel)` | `bool` | Check if relationship exists |
| `IsMutable()` | `bool` | Check if graph is mutable |
| `CreateNode()` | `Node` | Create node (write proc only) |
| `DeleteNode(node)` | `void` | Delete node (write proc only) |
| `DetachDeleteNode(node)` | `void` | Delete node and edges (write proc only) |
| `CreateRelationship(from, to, type)` | `Relationship` | Create relationship (write proc only) |
| `DeleteRelationship(rel)` | `void` | Delete relationship (write proc only) |
| `CheckMustAbort()` | `void` | Throws if termination requested |

### mgp::List

List container for values.

| Method | Return Type | Description |
|--------|-------------|-------------|
| `Size()` | `size_t` | Number of elements |
| `Empty()` | `bool` | Check if empty |
| `Append(value)` | `void` | Append value |
| `AppendExtend(value)` | `void` | Extend and append value |
| `operator[](index)` | `Value` | Get value at index |
| `begin()` / `end()` | `Iterator` | Iteration support |

### mgp::Map

Key-value map container.

| Method | Return Type | Description |
|--------|-------------|-------------|
| `Size()` | `size_t` | Number of entries |
| `Empty()` | `bool` | Check if empty |
| `At(key)` | `Value` | Get value at key |
| `Insert(key, value)` | `void` | Insert key-value pair |
| `Update(key, value)` | `void` | Insert or update value |
| `Erase(key)` | `void` | Remove key |
| `KeyExists(key)` | `bool` | Check if key exists |
| `operator[](key)` | `Value` | Get value at key |
| `begin()` / `end()` | `Iterator` | Iteration support |

### mgp::Type Enum

| Type | Description |
|------|-------------|
| `Type::Null` | Null value |
| `Type::Bool` | Boolean |
| `Type::Int` | 64-bit integer |
| `Type::Double` | Double-precision float |
| `Type::String` | String |
| `Type::List` | List of values |
| `Type::Map` | Map of key-value pairs |
| `Type::Node` | Graph node |
| `Type::Relationship` | Graph relationship |
| `Type::Path` | Graph path |
| `Type::Date` | Date |
| `Type::LocalTime` | Local time |
| `Type::LocalDateTime` | Local date-time |
| `Type::ZonedDateTime` | Zoned date-time |
| `Type::Duration` | Duration |

## Registration API

### mgp::AddProcedure

```cpp
void AddProcedure(
    callback,                      // Procedure function
    std::string_view name,         // Procedure name
    ProcedureType proc_type,       // Read or Write
    std::vector<Parameter> params, // Input parameters
    std::vector<Return> returns,   // Output fields
    mgp_module *module,
    mgp_memory *memory
);
```

### mgp::AddFunction

```cpp
void AddFunction(
    callback,                      // Function callback
    std::string_view name,         // Function name
    std::vector<Parameter> params, // Input parameters
    mgp_module *module,
    mgp_memory *memory
);
```

### mgp::Parameter

```cpp
// Required parameter
Parameter(std::string_view name, Type type)

// Optional with default
Parameter(std::string_view name, Type type, bool default_value)
Parameter(std::string_view name, Type type, int64_t default_value)
Parameter(std::string_view name, Type type, double default_value)
Parameter(std::string_view name, Type type, std::string_view default_value)

// List parameter
Parameter(std::string_view name, std::pair<Type, Type> list_type)
```

### mgp::Return

```cpp
Return(std::string_view name, Type type)
Return(std::string_view name, std::pair<Type, Type> list_type)  // List return
```

### mgp::ProcedureType

| Value | Description |
|-------|-------------|
| `ProcedureType::Read` | Read-only procedure |
| `ProcedureType::Write` | Procedure that can modify graph |

### mgp::RecordFactory

| Method | Description |
|--------|-------------|
| `NewRecord()` | Create new result record |
| `SetErrorMessage(msg)` | Set error message |

### mgp::Record

| Method | Description |
|--------|-------------|
| `Insert(field_name, value)` | Insert field value |

### mgp::Result (Functions)

| Method | Description |
|--------|-------------|
| `SetValue(value)` | Set function return value |
| `SetErrorMessage(msg)` | Set error message |

## Logging

```cpp
mgp_log(mgp_log_level::MGP_LOG_LEVEL_INFO, "Message");
mgp_log(mgp_log_level::MGP_LOG_LEVEL_DEBUG, "Debug");
mgp_log(mgp_log_level::MGP_LOG_LEVEL_ERROR, "Error");
```

## Exceptions

| Exception | Description |
|-----------|-------------|
| `mgp::NotFoundException` | Node/Relationship not found |
| `mgp::NotEnoughMemoryException` | Memory allocation failed |
| `mgp::InvalidArgumentException` | Invalid argument |
| `mgp::MustAbortException` | Procedure terminated |
| `mgp::KeyAlreadyExistsException` | Duplicate key |
| `mgp::ImmutableObjectException` | Read-only object modification |
| `mgp::ValueConversionException` | Type conversion error |
| `mgp::SerializationException` | Serialization error |

## Module Locations

| Path | Description |
|------|-------------|
| `/usr/lib/memgraph/query_modules/` | System modules (.so files) |
| `/usr/include/memgraph/mgp.hpp` | C++ API header |

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

```cpp
#include <memgraph/mgp.hpp>
#include <memgraph/mg_exceptions.hpp>

void DegreeDistribution(mgp_list *args, mgp_graph *memgraph_graph,
                        mgp_result *result, mgp_memory *memory) {
    mgp::MemoryDispatcherGuard guard(memory);
    const auto record_factory = mgp::RecordFactory(result);
    const mgp::Graph graph(memgraph_graph);
    
    try {
        std::unordered_map<int64_t, int64_t> distribution;
        
        for (const auto &node : graph.Nodes()) {
            int64_t degree = node.InDegree() + node.OutDegree();
            distribution[degree]++;
        }
        
        for (const auto &[degree, count] : distribution) {
            auto record = record_factory.NewRecord();
            record.Insert("degree", degree);
            record.Insert("count", count);
        }
    } catch (const std::exception &e) {
        record_factory.SetErrorMessage(e.what());
    }
}

extern "C" int mgp_init_module(struct mgp_module *module,
                                struct mgp_memory *memory) {
    mgp::MemoryDispatcherGuard guard(memory);
    try {
        mgp::AddProcedure(
            DegreeDistribution, "degree_distribution",
            mgp::ProcedureType::Read, {},
            {mgp::Return("degree", mgp::Type::Int),
             mgp::Return("count", mgp::Type::Int)},
            module, memory);
    } catch (const std::exception &e) { return 1; }
    return 0;
}

extern "C" int mgp_shutdown_module() { return 0; }
```

```cypher
CALL module.degree_distribution() YIELD degree, count
RETURN degree, count ORDER BY degree;
```

### Write Procedure

```cpp
void AddComputedProperty(mgp_list *args, mgp_graph *memgraph_graph,
                         mgp_result *result, mgp_memory *memory) {
    mgp::MemoryDispatcherGuard guard(memory);
    const auto arguments = mgp::List(args);
    const auto record_factory = mgp::RecordFactory(result);
    mgp::Graph graph(memgraph_graph);
    
    try {
        const auto property_name = std::string(arguments[0].ValueString());
        int64_t count = 0;
        
        for (const auto &node : graph.Nodes()) {
            int64_t degree = node.InDegree() + node.OutDegree();
            // Note: SetProperty requires std::string, not string_view
            const_cast<mgp::Node&>(node).SetProperty(
                property_name, mgp::Value(degree));
            count++;
        }
        
        auto record = record_factory.NewRecord();
        record.Insert("updated_count", count);
    } catch (const std::exception &e) {
        record_factory.SetErrorMessage(e.what());
    }
}

// Register with ProcedureType::Write
mgp::AddProcedure(
    AddComputedProperty, "add_computed_property",
    mgp::ProcedureType::Write,
    {mgp::Parameter("property_name", mgp::Type::String)},
    {mgp::Return("updated_count", mgp::Type::Int)},
    module, memory);
```

### User-Defined Function

```cpp
void VertexDegree(mgp_list *args, mgp_func_context *ctx,
                  mgp_func_result *res, mgp_memory *memory) {
    mgp::MemoryDispatcherGuard guard(memory);
    const auto arguments = mgp::List(args);
    auto result = mgp::Result(res);
    
    try {
        const auto node = arguments[0].ValueNode();
        int64_t degree = node.InDegree() + node.OutDegree();
        result.SetValue(degree);
    } catch (const std::exception &e) {
        result.SetErrorMessage(e.what());
    }
}

// Registration
mgp::AddFunction(VertexDegree, "vertex_degree",
    {mgp::Parameter("node", mgp::Type::Node)},
    module, memory);
```

```cypher
MATCH (p:Person)
RETURN p.name, module.vertex_degree(p) AS degree;
```

### Path Building (Random Walk)

```cpp
void RandomWalk(mgp_list *args, mgp_graph *memgraph_graph,
                mgp_result *result, mgp_memory *memory) {
    mgp::MemoryDispatcherGuard guard(memory);
    const auto arguments = mgp::List(args);
    const auto record_factory = mgp::RecordFactory(result);
    
    try {
        const auto start = arguments[0].ValueNode();
        const auto length = arguments[1].ValueInt();
        
        srand(time(NULL));
        auto path = mgp::Path(start);
        auto current = start;
        
        for (int64_t i = 0; i < length; i++) {
            auto out_edges = mgp::List();
            for (const auto &rel : current.OutRelationships()) {
                out_edges.AppendExtend(mgp::Value(rel));
            }
            
            if (out_edges.Empty()) break;
            
            auto next_rel = out_edges[rand() % out_edges.Size()].ValueRelationship();
            path.Expand(next_rel);
            current = next_rel.To();
        }
        
        auto record = record_factory.NewRecord();
        record.Insert("path", path);
    } catch (const std::exception &e) {
        record_factory.SetErrorMessage(e.what());
    }
}
```

### Error Handling

```cpp
void SafeProcedure(mgp_list *args, mgp_graph *memgraph_graph,
                   mgp_result *result, mgp_memory *memory) {
    mgp::MemoryDispatcherGuard guard(memory);
    const auto arguments = mgp::List(args);
    const auto record_factory = mgp::RecordFactory(result);
    const mgp::Graph graph(memgraph_graph);
    
    try {
        auto vertex_id = mgp::Id::FromInt(arguments[0].ValueInt());
        auto vertex = graph.GetNodeById(vertex_id);
        
        auto record = record_factory.NewRecord();
        record.Insert("result", "Found vertex: " + std::to_string(vertex.Id().AsInt()));
    } catch (const mgp::NotFoundException &e) {
        record_factory.SetErrorMessage("Vertex not found");
    } catch (const std::exception &e) {
        record_factory.SetErrorMessage(e.what());
    }
}
```

### Long-Running with Abort Check

```cpp
void LongRunningAnalysis(mgp_list *args, mgp_graph *memgraph_graph,
                         mgp_result *result, mgp_memory *memory) {
    mgp::MemoryDispatcherGuard guard(memory);
    const auto record_factory = mgp::RecordFactory(result);
    mgp::Graph graph(memgraph_graph);
    
    int64_t count = 0;
    try {
        for (const auto &node : graph.Nodes()) {
            graph.CheckMustAbort();  // Throws if termination requested
            count++;
        }
        auto record = record_factory.NewRecord();
        record.Insert("count", count);
    } catch (const mgp::MustAbortException &e) {
        // Handle graceful termination
        auto record = record_factory.NewRecord();
        record.Insert("count", count);
    } catch (const std::exception &e) {
        record_factory.SetErrorMessage(e.what());
    }
}
```

# Full C++ API

For complete API documentation, see the official Memgraph C++ API reference:
https://memgraph.com/docs/custom-query-modules/cpp/cpp-api
