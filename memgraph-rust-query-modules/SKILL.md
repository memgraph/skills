---
name: memgraph-rust-query-modules
description: Develop custom query modules in Rust for Memgraph graph database. Use when user asks to create Rust procedures, implement graph algorithms in Rust, build high-performance query modules, or work with the rsmgp-sys Rust API. Covers module structure, compilation with Cargo, graph traversal, vertex/edge operations, and deployment to Memgraph.
compatibility: Requires Memgraph instance (memgraph/memgraph-mage Docker image recommended). Rust/Cargo toolchain installed inside container.
metadata:
  author: memgraph
  version: "1.0.0"
---

# Memgraph Rust Query Modules

Develop high-performance custom query modules in Rust for Memgraph graph database.

## When to Use

- User asks to create a Rust query module or procedure for Memgraph
- User needs high-performance graph algorithms with Rust's safety guarantees
- User wants to implement computationally intensive procedures requiring native performance
- User mentions `rsmgp-sys`, Rust bindings for Memgraph, or Rust graph procedures
- User needs to build read-only procedures for data analysis in Rust

## Prerequisites

- Memgraph instance (`memgraph/memgraph-mage` Docker image)
- Rust toolchain (cargo) - installed inside container
- Access to `/mage/rust` directory with `rsmgp-sys` crate

## Quick Reference

| Feature | Description |
|---------|-------------|
| Crate | `rsmgp-sys` |
| Init Macro | `init_module!` |
| Procedure Macro | `define_procedure!` |
| Close Macro | `close_module!` |
| Build Command | `python3 setup build -p /usr/lib/memgraph/query_modules/` |

### Key Types

| Type | Description |
|------|-------------|
| `Memgraph` | Main context for graph operations |
| `Vertex` | Graph node with properties and labels |
| `Edge` | Relationship with type and properties |
| `Path` | Sequence of vertices and edges |
| `List` | List container for values |
| `Map` | Key-value map container |
| `Value` | Generic value enum for all types |
| `ResultRecord` | Return record for procedures |
| `MgpValue` | Low-level value wrapper |

For detailed API types and methods, see [references/REFERENCE.md](references/REFERENCE.md).

## Module Structure

Every Rust query module requires this file structure:

```
my_rust_module/
├── Cargo.toml
└── src/
    └── lib.rs
```

### Cargo.toml

```toml
[package]
name = "my-rust-query-module"
version = "0.1.0"
edition = "2018"

[dependencies]
c_str_macro = "1.0.2"
rsmgp-sys = { path = "../rsmgp-sys" }

[lib]
name = "my_rust_module"
crate-type = ["cdylib"]
```

### Basic lib.rs Structure

```rust
use c_str_macro::c_str;
use rsmgp_sys::list::*;
use rsmgp_sys::memgraph::*;
use rsmgp_sys::mgp::*;
use rsmgp_sys::property::*;
use rsmgp_sys::result::*;
use rsmgp_sys::rsmgp::*;
use rsmgp_sys::value::*;
use rsmgp_sys::{close_module, define_optional_type, define_procedure, define_type, init_module};
use std::ffi::CString;
use std::os::raw::c_int;
use std::panic;

// Module initialization - register procedures
init_module!(|memgraph: &Memgraph| -> Result<()> {
    memgraph.add_read_procedure(
        my_procedure,
        c_str!("my_procedure"),
        &[define_type!("input_param", Type::String)],
        &[],  // optional parameters
        &[define_type!("output_field", Type::String)],
    )?;
    
    Ok(())
});

// Procedure implementation
define_procedure!(my_procedure, |memgraph: &Memgraph| -> Result<()> {
    let result = memgraph.result_record()?;
    let args = memgraph.args()?;
    
    let input_value = args.value_at(0)?;
    
    result.insert_mgp_value(
        c_str!("output_field"),
        &input_value.to_mgp_value(&memgraph)?,
    )?;
    
    Ok(())
});

// Module cleanup
close_module!(|| -> Result<()> { Ok(()) });
```

## Basic Patterns

### Read Procedure with String Parameter

```rust
use c_str_macro::c_str;
use rsmgp_sys::memgraph::*;
use rsmgp_sys::mgp::*;
use rsmgp_sys::result::*;
use rsmgp_sys::rsmgp::*;
use rsmgp_sys::value::*;
use rsmgp_sys::{close_module, define_procedure, define_type, init_module};

init_module!(|memgraph: &Memgraph| -> Result<()> {
    memgraph.add_read_procedure(
        hello_world,
        c_str!("hello_world"),
        &[define_type!("name", Type::String)],
        &[],
        &[define_type!("message", Type::String)],
    )?;
    Ok(())
});

define_procedure!(hello_world, |memgraph: &Memgraph| -> Result<()> {
    let result = memgraph.result_record()?;
    let args = memgraph.args()?;
    
    let name = args.value_at(0)?;
    if let Value::String(name_str) = name {
        let message = format!("Hello, {}!", name_str.to_str().unwrap_or("World"));
        let message_cstr = std::ffi::CString::new(message).unwrap();
        result.insert_string(c_str!("message"), &message_cstr)?;
    }
    
    Ok(())
});

close_module!(|| -> Result<()> { Ok(()) });
```

**Cypher:**
```cypher
CALL my_module.hello_world("Memgraph") YIELD message;
```

### Procedure with Optional Parameters

```rust
use rsmgp_sys::{define_optional_type, define_type};

init_module!(|memgraph: &Memgraph| -> Result<()> {
    memgraph.add_read_procedure(
        procedure_with_optional,
        c_str!("procedure_with_optional"),
        &[define_type!("required_param", Type::String)],
        &[define_optional_type!(
            "optional_count",
            &MgpValue::make_int(10, &memgraph)?,  // default value
            Type::Int
        )],
        &[
            define_type!("result_string", Type::String),
            define_type!("result_int", Type::Int),
        ],
    )?;
    Ok(())
});

define_procedure!(procedure_with_optional, |memgraph: &Memgraph| -> Result<()> {
    let result = memgraph.result_record()?;
    let args = memgraph.args()?;
    
    let string_value = args.value_at(0)?;
    let int_value = args.value_at(1)?;
    
    result.insert_mgp_value(c_str!("result_string"), &string_value.to_mgp_value(&memgraph)?)?;
    result.insert_mgp_value(c_str!("result_int"), &int_value.to_mgp_value(&memgraph)?)?;
    
    Ok(())
});
```

### Iterating Over Graph Vertices

```rust
define_procedure!(count_nodes, |memgraph: &Memgraph| -> Result<()> {
    let result = memgraph.result_record()?;
    
    let mut count: i64 = 0;
    for _vertex in memgraph.vertices_iter()? {
        count += 1;
    }
    
    result.insert_int(c_str!("count"), count)?;
    
    Ok(())
});
```

### Accessing Vertex Properties and Labels

```rust
define_procedure!(vertex_info, |memgraph: &Memgraph| -> Result<()> {
    let args = memgraph.args()?;
    
    if let Value::Vertex(vertex) = args.value_at(0)? {
        let result = memgraph.result_record()?;
        
        // Get vertex ID
        let vertex_id = vertex.id();
        result.insert_int(c_str!("id"), vertex_id)?;
        
        // Get labels count
        let label_count = vertex.labels_count()?;
        result.insert_int(c_str!("label_count"), label_count as i64)?;
        
        // Get first label if exists
        if label_count > 0 {
            let label = vertex.label_at(0)?;
            result.insert_string(c_str!("first_label"), &label)?;
        }
        
        // Get property
        let name_prop = vertex.property(c_str!("name"))?;
        result.insert_mgp_value(c_str!("name"), &name_prop.value.to_mgp_value(&memgraph)?)?;
    }
    
    Ok(())
});
```

### Working with Edges

```rust
define_procedure!(get_neighbors, |memgraph: &Memgraph| -> Result<()> {
    let args = memgraph.args()?;
    
    if let Value::Vertex(vertex) = args.value_at(0)? {
        // Iterate outgoing edges
        for edge in vertex.out_edges()? {
            let result = memgraph.result_record()?;
            
            let neighbor = edge.to_vertex()?;
            let edge_type = edge.edge_type()?;
            
            result.insert_vertex(c_str!("neighbor"), &neighbor)?;
            result.insert_string(c_str!("edge_type"), &edge_type)?;
        }
        
        // Iterate incoming edges
        for edge in vertex.in_edges()? {
            let result = memgraph.result_record()?;
            
            let neighbor = edge.from_vertex()?;
            let edge_type = edge.edge_type()?;
            
            result.insert_vertex(c_str!("neighbor"), &neighbor)?;
            result.insert_string(c_str!("edge_type"), &edge_type)?;
        }
    }
    
    Ok(())
});
```

### Returning Multiple Records

```rust
define_procedure!(all_vertices, |memgraph: &Memgraph| -> Result<()> {
    for vertex in memgraph.vertices_iter()? {
        let result = memgraph.result_record()?;
        result.insert_vertex(c_str!("node"), &vertex)?;
        result.insert_int(c_str!("id"), vertex.id())?;
    }
    
    Ok(())
});
```

### Working with Lists

```rust
define_procedure!(process_list, |memgraph: &Memgraph| -> Result<()> {
    let args = memgraph.args()?;
    let result = memgraph.result_record()?;
    
    if let Value::List(input_list) = args.value_at(0)? {
        // Create output list
        let output_list = List::make_empty(input_list.size(), &memgraph)?;
        
        for i in 0..input_list.size() {
            let value = input_list.value_at(i)?;
            // Process value and append to output
            output_list.append_extend(&value.to_mgp_value(&memgraph)?)?;
        }
        
        result.insert_list(c_str!("processed"), &output_list)?;
    }
    
    Ok(())
});
```

### Working with Maps

```rust
define_procedure!(create_map, |memgraph: &Memgraph| -> Result<()> {
    let result = memgraph.result_record()?;
    
    let map = Map::make_empty(&memgraph)?;
    
    let key1 = MgpValue::make_string(c_str!("value1"), &memgraph)?;
    let key2 = MgpValue::make_int(42, &memgraph)?;
    
    map.insert(c_str!("key1"), &key1)?;
    map.insert(c_str!("key2"), &key2)?;
    
    result.insert_map(c_str!("data"), &map)?;
    
    Ok(())
});
```

### Long-Running with Abort Check

```rust
define_procedure!(long_running, |memgraph: &Memgraph| -> Result<()> {
    let result = memgraph.result_record()?;
    let mut count: i64 = 0;
    
    for vertex in memgraph.vertices_iter()? {
        // Check if procedure should abort
        if memgraph.must_abort() {
            break;
        }
        
        // Expensive computation...
        count += 1;
    }
    
    result.insert_int(c_str!("processed"), count)?;
    
    Ok(())
});
```

### Working with Paths

```rust
define_procedure!(build_path, |memgraph: &Memgraph| -> Result<()> {
    let args = memgraph.args()?;
    let result = memgraph.result_record()?;
    
    if let Value::Vertex(start_vertex) = args.value_at(0)? {
        // Create path starting with vertex
        let path = Path::make_with_start(&start_vertex, &memgraph)?;
        
        // Expand path with edges
        for edge in start_vertex.out_edges()? {
            path.expand(&edge)?;
            break;  // Just add first edge for example
        }
        
        result.insert_path(c_str!("path"), &path)?;
        result.insert_int(c_str!("length"), path.size() as i64)?;
    }
    
    Ok(())
});
```

## Value Types

The `Value` enum represents all possible Memgraph types:

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

### Type Matching

```rust
let value = args.value_at(0)?;
match value {
    Value::Null => { /* handle null */ },
    Value::Bool(b) => { /* handle bool */ },
    Value::Int(i) => { /* handle int */ },
    Value::Float(f) => { /* handle float */ },
    Value::String(s) => { /* handle string */ },
    Value::Vertex(v) => { /* handle vertex */ },
    Value::Edge(e) => { /* handle edge */ },
    Value::Path(p) => { /* handle path */ },
    Value::List(l) => { /* handle list */ },
    Value::Map(m) => { /* handle map */ },
    Value::Date(d) => { /* handle date */ },
    Value::LocalTime(t) => { /* handle time */ },
    Value::LocalDateTime(dt) => { /* handle datetime */ },
    Value::Duration(dur) => { /* handle duration */ },
}
```

## Procedure Types

| Macro | Description |
|-------|-------------|
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

## Building

### Step 1: Start Memgraph MAGE Container

```bash
docker run -p 7687:7687 -p 7444:7444 --name mage memgraph/memgraph-mage
```

### Step 2: Enter Container Shell

```bash
docker exec -it -u root mage bash
```

### Step 3: Install Cargo

```bash
curl https://sh.rustup.rs -sSf | sh -s -- -y
export PATH="/root/.cargo/bin:${PATH}"
```

### Step 4: Create Module Structure

```bash
cd /mage/rust
cp -r rsmgp-example my_rust_module
cd my_rust_module
```

Update `Cargo.toml`:
```toml
[package]
name = "my-rust-module-package"
version = "0.1.0"
edition = "2018"

[dependencies]
c_str_macro = "1.0.2"
rsmgp-sys = { path = "../rsmgp-sys" }

[lib]
name = "my_rust_module"
crate-type = ["cdylib"]
```

### Step 5: Write Module Code

Edit `src/lib.rs` with your procedure implementations.

### Step 6: Build and Deploy

```bash
cd /mage
python3 setup build -p /usr/lib/memgraph/query_modules/
```

The Rust modules compile to `.so` files in `/mage/dist` and are copied to `/usr/lib/memgraph/query_modules/`.

### Step 7: Load Modules

From mgconsole or Memgraph Lab:
```cypher
CALL mg.load_all();
```

Verify module is loaded:
```cypher
CALL mg.procedures() YIELD *;
```

## Deployment

### Deploy Built Module

```bash
# Copy module from container
docker cp mage:/usr/lib/memgraph/query_modules/libmy_rust_module.so ./

# Copy to production container
docker cp libmy_rust_module.so memgraph:/usr/lib/memgraph/query_modules/

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
```

## Error Handling

The `Result<T>` type is used throughout the API. Common errors are defined in the `Error` enum:

```rust
pub enum Error {
    UnableToCreateEmptyList,
    UnableToCopyList,
    UnableToAppendListValue,
    UnableToAccessListValueByIndex,
    UnableToCreateEmptyMap,
    UnableToInsertMapValue,
    UnableToAccessMapValue,
    UnableToCreateGraphVerticesIterator,
    UnableToFindVertexById,
    UnableToRegisterReadProcedure,
    UnableToCreateResultRecord,
    UnableToInsertResultValue,
    UnableToCreateCString,
    // ... and more
}
```

### Handling Errors in Procedures

```rust
define_procedure!(safe_procedure, |memgraph: &Memgraph| -> Result<()> {
    let args = memgraph.args()?;
    let result = memgraph.result_record()?;
    
    // Use ? operator to propagate errors
    let value = args.value_at(0)?;
    
    // Or handle errors explicitly
    match memgraph.vertex_by_id(12345) {
        Ok(vertex) => {
            result.insert_vertex(c_str!("found"), &vertex)?;
        },
        Err(_) => {
            result.insert_null(c_str!("found"))?;
        }
    }
    
    Ok(())
});
```

## Best Practices

1. **Use Result Type**: Always use `?` operator or explicit error handling
2. **CString Usage**: Use `c_str!` macro for static strings
3. **Abort Check**: Use `memgraph.must_abort()` in long-running loops
4. **Type Matching**: Use pattern matching on `Value` enum for type safety
5. **Memory Safety**: Rust's ownership system handles memory automatically

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Module not loading | Check .so in `/usr/lib/memgraph/query_modules/` |
| Cargo not found | Run `export PATH="/root/.cargo/bin:${PATH}"` |
| Build fails | Check `Cargo.toml` path to `rsmgp-sys` |
| Procedure not found | Run `CALL mg.load_all();` |
| Library linking errors | Use matching memgraph-mage-dev version |

## Additional Resources

For detailed API documentation, type references, and more examples, see [references/REFERENCE.md](references/REFERENCE.md).
