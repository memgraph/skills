---
name: memgraph-cpp-query-modules
description: Develop custom query modules in C++ for Memgraph graph database. Use when creating high-performance graph algorithms, procedures (ProcedureType::Read/Write), or functions using the mgp.hpp C++ API. Covers compilation, memory management, graph traversal, and module deployment.
compatibility: "Requires Memgraph instance. Quick dev: Clang, CMake Production: memgraph/mgbuild container with toolchain v7. C++20 required."
metadata:
  version: "0.0.1"
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

## Prerequisites

**For Quick Development:**
- Memgraph instance (`memgraph/memgraph-mage` Docker image)
- C++20 compatible compiler (clang++ 20.1.7+ recommended)
- CMake 4.0.3+

**For Production Builds:**
- Docker with `memgraph/mgbuild:v7_ubuntu-24.04` image
- Toolchain v7: Clang 20.1.7, GCC 15.1.0, CMake 4.0.3
- See [Production Build with MgBuild](#option-2-production-build-with-mgbuild-toolchain)

## Quick Reference

| Feature | Procedures | Functions |
|---------|------------|-----------|
| Registration | `mgp::AddProcedure()` | `mgp::AddFunction()` |
| Type | `ProcedureType::Read/Write` | Read-only |
| Cypher | `CALL module.proc() YIELD ...` | `RETURN module.func()` |
| Return | `Record` via `RecordFactory` | `Result::SetValue()` |

For detailed API types and methods, see [references/REFERENCE.md](references/REFERENCE.md).

## Module Structure

Every C++ query module requires this structure:

```cpp
#include <memgraph/mgp.hpp>
#include <memgraph/mg_exceptions.hpp>

// Procedure implementation
void MyProcedure(mgp_list *args, mgp_graph *memgraph_graph, 
                 mgp_result *result, mgp_memory *memory) {
    mgp::MemoryDispatcherGuard guard(memory);  // REQUIRED first line
    const auto arguments = mgp::List(args);
    const auto record_factory = mgp::RecordFactory(result);
    
    try {
        // Your logic here
        auto record = record_factory.NewRecord();
        record.Insert("field_name", value);
    } catch (const std::exception &e) {
        record_factory.SetErrorMessage(e.what());
    }
}

// Module initialization - register procedures and functions
extern "C" int mgp_init_module(struct mgp_module *module, 
                                struct mgp_memory *memory) {
    mgp::MemoryDispatcherGuard guard(memory);
    try {
        mgp::AddProcedure(MyProcedure, "my_procedure",
            mgp::ProcedureType::Read,
            {mgp::Parameter("param", mgp::Type::String)},
            {mgp::Return("field_name", mgp::Type::String)},
            module, memory);
    } catch (const std::exception &e) { return 1; }
    return 0;
}

extern "C" int mgp_shutdown_module() { return 0; }
```

## Basic Patterns

### Read Procedure

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
            if (node.HasLabel(label_name)) count++;
        }
        
        auto record = record_factory.NewRecord();
        record.Insert("count", count);
    } catch (const std::exception &e) {
        record_factory.SetErrorMessage(e.what());
    }
}

// Register in mgp_init_module:
mgp::AddProcedure(CountNodesByLabel, "count_by_label",
    mgp::ProcedureType::Read,
    {mgp::Parameter("label", mgp::Type::String)},
    {mgp::Return("count", mgp::Type::Int)},
    module, memory);
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
        auto node = graph.CreateNode();
        node.AddLabel("Person");
        node.SetProperty("name", mgp::Value(arguments[0].ValueString()));
        
        auto record = record_factory.NewRecord();
        record.Insert("node", node);
    } catch (const std::exception &e) {
        record_factory.SetErrorMessage(e.what());
    }
}

// Register with ProcedureType::Write
mgp::AddProcedure(CreatePerson, "create_person",
    mgp::ProcedureType::Write,
    {mgp::Parameter("name", mgp::Type::String)},
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
    
    result.SetValue(arguments[0].ValueInt() * arguments[1].ValueInt());
}

// Register in mgp_init_module:
mgp::AddFunction(Multiply, "multiply",
    {mgp::Parameter("a", mgp::Type::Int),
     mgp::Parameter("b", mgp::Type::Int)},
    module, memory);
```

### Returning Multiple Records

```cpp
for (const auto &rel : start_node.OutRelationships()) {
    auto record = record_factory.NewRecord();
    record.Insert("neighbor", rel.To());
    record.Insert("edge_type", std::string(rel.Type()));
}
```

### Long-Running with Abort Check

```cpp
for (const auto &node : graph.Nodes()) {
    graph.CheckMustAbort();  // Throws mgp::MustAbortException if terminated
    // Process node...
}
```

## Building

### Option 1: Quick Development Build

For rapid prototyping inside the memgraph-mage container:

```bash
# Start container and install tools
docker run -p 7687:7687 --name memgraph memgraph/memgraph-mage
docker exec -it memgraph bash
apt update -y && apt install -y cmake clang

# Direct compilation
clang++ -std=c++20 -shared -fPIC \
    -o /usr/lib/memgraph/query_modules/libmodule.so module.cpp
```

Or use CMake:

```cmake
cmake_minimum_required(VERSION 3.10.0)
project(my_query_module)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_COMPILER "clang++")

add_library(my_query_module SHARED my_query_module.cpp)
```

```bash
mkdir build && cd build && cmake .. && make
cp libmy_query_module.so /usr/lib/memgraph/query_modules/
```

### Option 2: Production Build with MgBuild Toolchain

Use Memgraph's official toolchain for production-grade builds with ABI compatibility.

#### Setup Module Directory

```
my_module/
├── CMakeLists.txt
├── my_module.cpp
└── include/
    └── memgraph/
        ├── mgp.hpp
        ├── _mgp.hpp
        ├── mg_exceptions.hpp
        └── mg_procedure.h
```

#### Copy Headers from Memgraph

The MgBuild container does NOT include Memgraph headers:

```bash
mkdir -p my_module/include/memgraph
docker cp memgraph:/usr/include/memgraph/. my_module/include/memgraph/
```

#### CMakeLists.txt for MgBuild

```cmake
cmake_minimum_required(VERSION 3.14)
project(my_query_module LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Werror=switch -Werror=switch-bool")

include_directories(${CMAKE_SOURCE_DIR}/include)
add_library(my_query_module SHARED my_query_module.cpp)
```

#### Build with MgBuild Container

```bash
# Pull image (use -arm suffix for Apple Silicon)
docker pull memgraph/mgbuild:v7_ubuntu-24.04      # AMD64
docker pull memgraph/mgbuild:v7_ubuntu-24.04-arm  # ARM64

# Build (one-liner)
docker run --rm --entrypoint /bin/bash \
  -v $(pwd)/my_module:/home/mg/my_module \
  -v $(pwd)/output:/home/mg/output \
  memgraph/mgbuild:v7_ubuntu-24.04-arm -c "
    source /opt/toolchain-v7/activate
    cd /home/mg/my_module
    mkdir -p build && cd build
    cmake -DCMAKE_BUILD_TYPE=Release ..
    make
    cp libmy_query_module.so /home/mg/output/
  "
```

> **Note:** The MgBuild container requires `--entrypoint /bin/bash` due to its custom entrypoint.

#### Toolchain Versions

| Toolchain | Clang | GCC | CMake | Supported OS |
|-----------|-------|-----|-------|--------------|
| v7 | 20.1.7 | 15.1.0 | 4.0.3 | Ubuntu 24.04, Debian 12, Fedora 41 |
| v6 | 18.1.8 | 13.2.0 | 3.27.7 | Ubuntu 22.04, Debian 11/12 |
| v5 | 17.0.2 | 13.2.0 | 3.27.7 | Ubuntu 20.04/22.04, Debian 10/11 |

> **ARM64:** For Apple Silicon or ARM servers, append `-arm` to image tag.

## Deployment

### Deploy Built Module

```bash
# Copy module to Memgraph container
docker cp output/libmy_query_module.so memgraph:/usr/lib/memgraph/query_modules/

# Reload modules
docker exec memgraph bash -c "echo 'CALL mg.load_all();' | mgconsole"
```

### Volume Mount (Development)

```bash
docker run -d -p 7687:7687 \
  -v $(pwd)/modules:/usr/lib/memgraph/query_modules \
  --name memgraph memgraph/memgraph-mage
```

### Module Management (Cypher)

```cypher
CALL mg.load_all();              -- Load all modules
CALL mg.load("module_name");     -- Load specific module
CALL mg.procedures() YIELD *;    -- List procedures
CALL mg.functions() YIELD *;     -- List functions
```

## Debugging

### Logging

```cpp
#include <mgp.hpp>

// Inside procedure (no printf-style formatting)
(void)mgp_log(mgp_log_level::MGP_LOG_LEVEL_INFO, "Starting procedure");

std::string msg = "Value = " + std::to_string(value);
(void)mgp_log(mgp_log_level::MGP_LOG_LEVEL_INFO, msg.c_str());
```

Start Memgraph with INFO log level:
```bash
docker run -d -p 7687:7687 --name memgraph memgraph/memgraph-mage --log-level=INFO
```

View logs:
```bash
docker exec memgraph cat /var/log/memgraph/memgraph_$(date +%Y-%m-%d).log
```

### Error Handling

```cpp
try {
    // Procedure logic
} catch (const mgp::NotFoundException &e) {
    record_factory.SetErrorMessage("Node not found");
} catch (const mgp::MustAbortException &e) {
    // Handle graceful termination
} catch (const std::exception &e) {
    record_factory.SetErrorMessage(e.what());
}
```

## Best Practices

1. **Memory Guard**: Always use `mgp::MemoryDispatcherGuard guard(memory)` as first line
2. **Exception Handling**: Never let exceptions escape module boundaries
3. **Abort Check**: Use `graph.CheckMustAbort()` in long loops
4. **Type Safety**: Check value types with `value.IsInt()` etc. before conversion

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Module not loading | Check .so in `/usr/lib/memgraph/query_modules/` |
| Segmentation fault | Check null pointers, verify memory guard usage |
| Module crashes | Handle all exceptions, don't let them escape |
| Procedure not found | Run `CALL mg.load_all();` |

## Additional Resources

For detailed API documentation, type references, and more examples, see [references/REFERENCE.md](references/REFERENCE.md).
