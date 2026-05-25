---
name: memgraph-rust-query-modules
description: Develop custom query modules in Rust for Memgraph graph database. Use when user asks to create Rust procedures, implement graph algorithms in Rust, build high-performance query modules, or work with the rsmgp-sys Rust API. Covers module structure, compilation with Cargo, graph traversal, vertex/edge operations, and deployment to Memgraph.
compatibility: "Requires Memgraph instance. Build with memgraph/mgbuild container with toolchain v7 (Rust 1.80 pre-installed)."
metadata:
  author: memgraph
  version: "0.0.1"
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

- Docker with `memgraph/mgbuild:v7_ubuntu-24.04` image
- Toolchain v7: Clang 20.1.7, GCC 15.1.0, CMake 4.0.3, Rust 1.80 (pre-installed)
- Memgraph instance for deployment (`memgraph/memgraph-mage` Docker image)

## Quick Reference

| Feature | Description |
|---------|-------------|
| Crate | `rsmgp-sys` |
| Init Macro | `init_module!` |
| Procedure Macro | `define_procedure!` |
| Close Macro | `close_module!` |
| Build Command | `cargo build --release` |

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

Use `define_optional_type!` macro with a default value:

```rust
memgraph.add_read_procedure(
    my_proc,
    c_str!("my_proc"),
    &[define_type!("required_param", Type::String)],
    &[define_optional_type!(
        "optional_count",
        &MgpValue::make_int(10, &memgraph)?,  // default value
        Type::Int
    )],
    &[define_type!("result", Type::Int)],
)?;
```

### Iterating Over Graph Vertices

```rust
let mut count: i64 = 0;
for vertex in memgraph.vertices_iter()? {
    count += 1;
}
result.insert_int(c_str!("count"), count)?;
```

### Accessing Vertex Properties and Labels

```rust
if let Value::Vertex(vertex) = args.value_at(0)? {
    let vertex_id = vertex.id();
    let label_count = vertex.labels_count()?;
    let first_label = vertex.label_at(0)?;
    let name_prop = vertex.property(c_str!("name"))?;
    
    result.insert_int(c_str!("id"), vertex_id)?;
    result.insert_string(c_str!("first_label"), &first_label)?;
}
```

### Working with Edges

```rust
if let Value::Vertex(vertex) = args.value_at(0)? {
    // Outgoing edges
    for edge in vertex.out_edges()? {
        let neighbor = edge.to_vertex()?;
        let edge_type = edge.edge_type()?;
        result.insert_vertex(c_str!("neighbor"), &neighbor)?;
    }
    // Incoming edges
    for edge in vertex.in_edges()? {
        let neighbor = edge.from_vertex()?;
    }
}
```

### Returning Multiple Records

```rust
for vertex in memgraph.vertices_iter()? {
    let result = memgraph.result_record()?;  // New record per iteration
    result.insert_vertex(c_str!("node"), &vertex)?;
}
```

### Working with Lists

```rust
if let Value::List(input_list) = args.value_at(0)? {
    let output_list = List::make_empty(input_list.size(), &memgraph)?;
    for i in 0..input_list.size() {
        let value = input_list.value_at(i)?;
        output_list.append_extend(&value.to_mgp_value(&memgraph)?)?;
    }
    result.insert_list(c_str!("processed"), &output_list)?;
}
```

### Working with Maps

```rust
let map = Map::make_empty(&memgraph)?;
map.insert(c_str!("key1"), &MgpValue::make_string(c_str!("value1"), &memgraph)?)?;
map.insert(c_str!("key2"), &MgpValue::make_int(42, &memgraph)?)?;
result.insert_map(c_str!("data"), &map)?;
```

### Long-Running with Abort Check

```rust
for vertex in memgraph.vertices_iter()? {
    if memgraph.must_abort() {
        break;  // Graceful termination
    }
    // Expensive computation...
}
```

### Working with Paths

```rust
if let Value::Vertex(start_vertex) = args.value_at(0)? {
    let path = Path::make_with_start(&start_vertex, &memgraph)?;
    for edge in start_vertex.out_edges()? {
        path.expand(&edge)?;
        break;  // Add first edge
    }
    result.insert_path(c_str!("path"), &path)?;
}
```

## Procedure Types

See [references/REFERENCE.md](references/REFERENCE.md) for the complete `Value` enum and `Type` definitions.

## Building

Use Memgraph's official MgBuild toolchain for production-grade builds with ABI compatibility.

### Setup Module Directory

```
my_rust_module/
├── Cargo.toml
├── rsmgp-sys/          # Copied from Memgraph monorepo
└── src/
    └── lib.rs
```

### Clone rsmgp-sys Bindings

The MgBuild container does NOT include rsmgp-sys. Clone from the Memgraph monorepo:

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/memgraph/memgraph.git
cd memgraph && git sparse-checkout set mage/rust/rsmgp-sys && cd ..
cp -r memgraph/mage/rust/rsmgp-sys my_rust_module/
```

### Cargo.toml

```toml
[package]
name = "my-rust-module-package"
version = "0.1.0"
edition = "2018"

[dependencies]
c_str_macro = "1.0.2"
rsmgp-sys = { path = "./rsmgp-sys" }

[lib]
name = "my_rust_module"
crate-type = ["cdylib"]
```

### Build with MgBuild Container

```bash
# Pull image (use -arm suffix for Apple Silicon)
docker pull memgraph/mgbuild:v7_ubuntu-24.04      # AMD64
docker pull memgraph/mgbuild:v7_ubuntu-24.04-arm  # ARM64

# Build (one-liner)
docker run --rm --entrypoint /bin/bash \
  -v $(pwd)/my_rust_module:/home/mg/my_rust_module \
  -v $(pwd)/output:/home/mg/output \
  memgraph/mgbuild:v7_ubuntu-24.04-arm -c "
    source /opt/toolchain-v7/activate
    source ~/.cargo/env
    cd /home/mg/my_rust_module
    cargo build --release
    cp target/release/libmy_rust_module.so /home/mg/output/
  "
```

> **Note:** The MgBuild container has Rust 1.80 pre-installed. To use a different version, run `rustup install 1.85 && rustup default 1.85` before building.

### Toolchain Versions

| Toolchain | Clang | GCC | CMake | Rust | Supported OS |
|-----------|-------|-----|-------|------|---------------|
| v7 | 20.1.7 | 15.1.0 | 4.0.3 | 1.80 | Ubuntu 24.04, Debian 12, Fedora 41 |
| v6 | 18.1.8 | 13.2.0 | 3.27.7 | 1.80 | Ubuntu 22.04, Debian 11/12 |
| v5 | 17.0.2 | 13.2.0 | 3.27.7 | 1.80 | Ubuntu 20.04/22.04, Debian 10/11 |

> **ARM64:** For Apple Silicon or ARM servers, append `-arm` to image tag.

### Load Modules

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
# Copy module to Memgraph container
docker cp output/libmy_rust_module.so memgraph:/usr/lib/memgraph/query_modules/

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

Use the `Result<T>` type and `?` operator throughout:

```rust
define_procedure!(safe_procedure, |memgraph: &Memgraph| -> Result<()> {
    let args = memgraph.args()?;
    let result = memgraph.result_record()?;
    
    // Use ? operator to propagate errors
    let value = args.value_at(0)?;
    
    // Or handle errors explicitly
    match memgraph.vertex_by_id(12345) {
        Ok(vertex) => result.insert_vertex(c_str!("found"), &vertex)?,
        Err(_) => result.insert_null(c_str!("found"))?,
    }
    
    Ok(())
});
```

See [references/REFERENCE.md](references/REFERENCE.md) for the complete `Error` enum.

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
| Cargo not found | Run `source ~/.cargo/env` |
| Build fails | Check `Cargo.toml` path to `rsmgp-sys` |
| Procedure not found | Run `CALL mg.load_all();` |
| Library linking errors | Use mgbuild toolchain for production builds |

## Additional Resources

For detailed API documentation, type references, and more examples, see [references/REFERENCE.md](references/REFERENCE.md).
