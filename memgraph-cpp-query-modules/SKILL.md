---
name: memgraph-cpp-query-modules
description: Develop custom query modules in C++ for Memgraph graph database. Use when creating high-performance graph algorithms, procedures (ProcedureType::Read/Write), or functions using the mgp.hpp C++ API. Covers compilation, memory management, graph traversal, and module deployment.
compatibility: Requires Memgraph instance, clang++ 17.0.2+, CMake 3.10+, C++20
metadata:
  version: "1.0.0"
  author: memgraph
---

# Memgraph C++ Query Modules

Develop high-performance custom query modules in C++ for Memgraph graph database.

## When to Use

- Create high-performance custom graph algorithms
- Implement computationally intensive procedures requiring native performance
- Build read-only procedures (`ProcedureType::Read`) for data analysis
- Build write procedures (`ProcedureType::Write`) for graph modification
- Create user-defined functions for use in Cypher queries
- Develop algorithms with strict latency requirements

## Prerequisites

- Memgraph instance running (preferably `memgraph/memgraph-mage` Docker image)
- C++20 compatible compiler (clang++ 17.0.2 recommended)
- CMake 3.10.0+
- Header: `/usr/include/memgraph/mgp.hpp`

## Quick Reference

| Feature | Procedures | Functions |
|---------|------------|-----------|
| Registration | `mgp::AddProcedure()` | `mgp::AddFunction()` |
| Type | `ProcedureType::Read/Write` | Read-only |
| Cypher | `CALL module.proc() YIELD ...` | `RETURN module.func()` |
| Return | `Record` via `RecordFactory` | `Result::SetValue()` |

### Key Types

| Type | Description |
|------|-------------|
| `mgp::Node` | Graph node with properties, labels |
| `mgp::Relationship` | Edge with type and properties |
| `mgp::Path` | Sequence of nodes and relationships |
| `mgp::Value` | Generic value container |
| `mgp::Graph` | Graph access wrapper |
| `mgp::RecordFactory` | Creates result records |
| `mgp::Result` | Function return value |

## Module Structure

```cpp
#include <memgraph/mgp.hpp>
#include <memgraph/mg_exceptions.hpp>

// Procedure implementation
void MyProcedure(mgp_list *args, mgp_graph *memgraph_graph, 
                 mgp_result *result, mgp_memory *memory) {
    mgp::MemoryDispatcherGuard guard(memory);  // REQUIRED
    // Implementation
}

// Module initialization
extern "C" int mgp_init_module(struct mgp_module *module, 
                                struct mgp_memory *memory) {
    mgp::MemoryDispatcherGuard guard(memory);
    // Register procedures and functions
    return 0;  // 0 = success
}

extern "C" int mgp_shutdown_module() { return 0; }
```

## Basic Patterns

### Read Procedure

```cpp
void HelloWorld(mgp_list *args, mgp_graph *memgraph_graph,
                mgp_result *result, mgp_memory *memory) {
    mgp::MemoryDispatcherGuard guard(memory);
    
    const auto arguments = mgp::List(args);
    const auto record_factory = mgp::RecordFactory(result);
    
    try {
        const auto name = arguments[0].ValueString();
        auto record = record_factory.NewRecord();
        record.Insert("message", std::string("Hello, ") + std::string(name) + "!");
    } catch (const std::exception &e) {
        record_factory.SetErrorMessage(e.what());
    }
}

extern "C" int mgp_init_module(struct mgp_module *module, 
                                struct mgp_memory *memory) {
    mgp::MemoryDispatcherGuard guard(memory);
    
    try {
        mgp::AddProcedure(
            HelloWorld, "hello_world",
            mgp::ProcedureType::Read,
            {mgp::Parameter("name", mgp::Type::String)},
            {mgp::Return("message", mgp::Type::String)},
            module, memory
        );
    } catch (const std::exception &e) { return 1; }
    return 0;
}

extern "C" int mgp_shutdown_module() { return 0; }
```

### Read Procedure with Graph Access

```cpp
void CountNodesByLabel(mgp_list *args, mgp_graph *memgraph_graph,
                       mgp_result *result, mgp_memory *memory) {
    mgp::MemoryDispatcherGuard guard(memory);
    
    const auto arguments = mgp::List(args);
    const auto record_factory = mgp::RecordFactory(result);
    const mgp::Graph graph(memgraph_graph);
    
    try {
        const auto label_name = std::string(arguments[0].ValueString());
        int64_t count = 0;
        
        for (const auto &node : graph.Nodes()) {
            for (const auto &label : node.Labels()) {
                if (std::string(label) == label_name) {
                    count++;
                    break;
                }
            }
        }
        
        auto record = record_factory.NewRecord();
        record.Insert("count", count);
    } catch (const std::exception &e) {
        record_factory.SetErrorMessage(e.what());
    }
}
```

### Write Procedure

```cpp
void CreatePerson(mgp_list *args, mgp_graph *memgraph_graph,
                  mgp_result *result, mgp_memory *memory) {
    mgp::MemoryDispatcherGuard guard(memory);
    
    const auto arguments = mgp::List(args);
    const auto record_factory = mgp::RecordFactory(result);
    mgp::Graph graph(memgraph_graph);
    
    try {
        const auto name = arguments[0].ValueString();
        const auto age = arguments[1].ValueInt();
        
        auto node = graph.CreateNode();
        node.AddLabel("Person");
        node.SetProperty("name", mgp::Value(name));
        node.SetProperty("age", mgp::Value(age));
        
        auto record = record_factory.NewRecord();
        record.Insert("node", node);
    } catch (const std::exception &e) {
        record_factory.SetErrorMessage(e.what());
    }
}

// Register with ProcedureType::Write
mgp::AddProcedure(CreatePerson, "create_person",
    mgp::ProcedureType::Write,
    {mgp::Parameter("name", mgp::Type::String),
     mgp::Parameter("age", mgp::Type::Int)},
    {mgp::Return("node", mgp::Type::Node)},
    module, memory);
```

### User-Defined Function

```cpp
void Multiply(mgp_list *args, mgp_func_context *ctx, 
              mgp_func_result *res, mgp_memory *memory) {
    mgp::MemoryDispatcherGuard guard(memory);
    
    const auto arguments = mgp::List(args);
    auto result = mgp::Result(res);
    
    auto first = arguments[0].ValueInt();
    auto second = arguments[1].ValueInt();
    
    result.SetValue(first * second);
}

// Register function
mgp::AddFunction(Multiply, "multiply",
    {mgp::Parameter("a", mgp::Type::Int),
     mgp::Parameter("b", mgp::Type::Int)},
    module, memory);
```

### Returning Multiple Records

```cpp
void GetNeighbors(mgp_list *args, mgp_graph *memgraph_graph,
                  mgp_result *result, mgp_memory *memory) {
    mgp::MemoryDispatcherGuard guard(memory);
    
    const auto arguments = mgp::List(args);
    const auto record_factory = mgp::RecordFactory(result);
    
    try {
        const auto start_node = arguments[0].ValueNode();
        
        for (const auto &rel : start_node.OutRelationships()) {
            auto record = record_factory.NewRecord();
            record.Insert("neighbor", rel.To());
            record.Insert("edge_type", std::string(rel.Type()));
        }
        for (const auto &rel : start_node.InRelationships()) {
            auto record = record_factory.NewRecord();
            record.Insert("neighbor", rel.From());
            record.Insert("edge_type", std::string(rel.Type()));
        }
    } catch (const std::exception &e) {
        record_factory.SetErrorMessage(e.what());
    }
}
```

## Working with Graph Elements

### Node Operations

```cpp
node.Id().AsInt()           // Get node ID
node.Labels()               // Iterate labels
node.HasLabel("Label")      // Check label
node.Properties()           // Get all properties
node.GetProperty("key")     // Get property value
node.InDegree()             // Incoming edge count
node.OutDegree()            // Outgoing edge count
node.InRelationships()      // Incoming edges
node.OutRelationships()     // Outgoing edges

// Write operations
node.AddLabel("Label")
node.RemoveLabel("Label")
node.SetProperty("key", mgp::Value(value))
```

### Relationship Operations

```cpp
rel.Id().AsInt()            // Get relationship ID
rel.Type()                  // Get type name
rel.From()                  // Source node
rel.To()                    // Target node
rel.Properties()            // Get all properties
rel.GetProperty("key")      // Get property value
```

### Value Type Checking

```cpp
value.Type()                // Get mgp::Type enum
value.IsNull()              // Check if null
value.IsBool()              // Check if bool
value.IsInt()               // Check if int
value.IsDouble()            // Check if double
value.IsString()            // Check if string
value.IsNode()              // Check if node
value.ValueBool()           // Get bool value
value.ValueInt()            // Get int64_t value
value.ValueDouble()         // Get double value
value.ValueString()         // Get string_view value
value.ValueNode()           // Get Node value
```

## Parameters with Defaults

```cpp
mgp::Parameter("name", mgp::Type::String)                    // Required
mgp::Parameter("count", mgp::Type::Int, 10)                  // Default int
mgp::Parameter("enabled", mgp::Type::Bool, true)             // Default bool
mgp::Parameter("ratio", mgp::Type::Double, 0.85)             // Default double
mgp::Parameter("label", mgp::Type::String, "Node")           // Default string
mgp::Parameter("items", {mgp::Type::List, mgp::Type::String}) // List parameter
```

## Long-Running with Abort Check

```cpp
void LongRunningAnalysis(mgp_list *args, mgp_graph *memgraph_graph,
                         mgp_result *result, mgp_memory *memory) {
    mgp::MemoryDispatcherGuard guard(memory);
    const auto record_factory = mgp::RecordFactory(result);
    auto graph = mgp::Graph(memgraph_graph);
    
    int64_t count = 0;
    try {
        for (const auto &node : graph.Nodes()) {
            graph.CheckMustAbort();  // Throws if termination requested
            count++;
        }
        auto record = record_factory.NewRecord();
        record.Insert("count", count);
    } catch (const mgp::MustAbortException &e) {
        auto record = record_factory.NewRecord();
        record.Insert("count", count);
    } catch (const std::exception &e) {
        record_factory.SetErrorMessage(e.what());
    }
}
```

## Building

### CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.10.0)
project(my_query_module)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_COMPILER "clang++")

add_library(my_query_module SHARED my_query_module.cpp)

add_custom_command(TARGET my_query_module POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy 
    $<TARGET_FILE:my_query_module> 
    /usr/lib/memgraph/query_modules/libmy_query_module.so)
```

### Build Commands

```bash
# Inside Memgraph container
apt update -y && apt install -y cmake clang

# Build with CMake
mkdir build && cd build && cmake .. && make

# Or direct compilation
clang++ -std=c++20 -shared -fPIC \
    -o /usr/lib/memgraph/query_modules/libmodule.so module.cpp
```

## Deployment

### Develop Inside Container

```bash
docker run -p 7687:7687 --name memgraph memgraph/memgraph-mage
docker exec -it memgraph bash
apt update -y && apt install -y cmake clang
# Build and deploy...
```

### Volume Mount

```bash
docker run -d -p 7687:7687 \
  -v $(pwd)/modules:/usr/lib/memgraph/query_modules \
  --name memgraph memgraph/memgraph-mage
```

## Module Management (Cypher)

```cypher
CALL mg.load_all();              -- Load all modules
CALL mg.load("module_name");     -- Load specific module
CALL mg.procedures() YIELD *;    -- List procedures
CALL mg.functions() YIELD *;     -- List functions
```

## Debugging with Logging

Use `mgp_log` to add debug messages (does NOT support printf-style formatting):

```cpp
#include <mgp.hpp>

void MyProcedure(mgp_list *args, mgp_graph *graph,
                 mgp_result *result, mgp_memory *memory) {
    // Log entry point
    (void)mgp_log(mgp_log_level::MGP_LOG_LEVEL_INFO, "MyProcedure: Starting");
    
    // Log dynamic values by concatenating strings
    std::string value = "some_value";
    std::string msg = "MyProcedure: Processing value = " + value;
    (void)mgp_log(mgp_log_level::MGP_LOG_LEVEL_INFO, msg.c_str());
    
    // Log errors
    (void)mgp_log(mgp_log_level::MGP_LOG_LEVEL_ERROR, "MyProcedure: Error occurred");
}
```

**Start Memgraph with INFO log level** (default is WARNING):
```bash
docker run -d -p 7687:7687 --name memgraph memgraph/memgraph-mage --log-level=INFO
```

**View logs:**
```bash
docker exec memgraph cat /var/log/memgraph/memgraph_$(date +%Y-%m-%d).log | grep "MyProcedure"
```

**Log levels:** `MGP_LOG_LEVEL_TRACE`, `MGP_LOG_LEVEL_DEBUG`, `MGP_LOG_LEVEL_INFO`, `MGP_LOG_LEVEL_WARNING`, `MGP_LOG_LEVEL_ERROR`

## Error Handling

```cpp
try {
    // Procedure logic
} catch (const mgp::NotFoundException &e) {
    record_factory.SetErrorMessage("Node not found");
} catch (const mgp::InvalidArgumentException &e) {
    record_factory.SetErrorMessage("Invalid argument");
} catch (const mgp::MustAbortException &e) {
    // Handle termination
} catch (const std::exception &e) {
    record_factory.SetErrorMessage(e.what());
}
```

## Best Practices

1. **Memory Guard**: Always use `mgp::MemoryDispatcherGuard guard(memory)` first
2. **Exception Handling**: Never let exceptions escape module boundaries
3. **Error Messages**: Use `record_factory.SetErrorMessage()` for errors
4. **Thread Safety**: Avoid global state
5. **Performance**: Use `graph.CheckMustAbort()` in long loops
6. **Type Safety**: Check value types before conversion

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Module not loading | Check .so in `/usr/lib/memgraph/query_modules/` |
| Segmentation fault | Check null pointers, memory guard usage |
| Module crashes Memgraph | Handle all exceptions |
| Type errors | Use `Value.Is[TYPE]()` checks |
| Procedure not found | Run `CALL mg.load_all();` |

## Additional Resources

For detailed API documentation and examples, see [references/REFERENCE.md](references/REFERENCE.md).
