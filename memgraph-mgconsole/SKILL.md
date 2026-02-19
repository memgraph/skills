---
name: memgraph-mgconsole
description: Guide to using Memgraph's mgconsole CLI for connecting to Memgraph, running Cypher, configuring output, and using interactive or non-interactive modes. Use when the user asks how to install, connect, or run queries with mgconsole.
compatibility: Requires access to a running Memgraph instance. Docker recommended for mgconsole.
metadata:
  author: memgraph
  version: "0.0.1"
---

# Memgraph mgconsole CLI

Use mgconsole to connect to Memgraph and execute Cypher queries from the command line.

## When to Use

- User asks how to install or start mgconsole
- User needs to connect to Memgraph from a terminal
- User wants to run Cypher queries non-interactively (scripts or CI)
- User needs to change output format, history, or verbose execution info

## Prerequisites

- A running Memgraph instance (local or remote)
- Docker available for mgconsole image (recommended)
- Optional: mgconsole binary for macOS or Windows

## Quick Start

### Start mgconsole via Docker

- Local Memgraph on Linux:

```bash
docker run -it memgraph/mgconsole:latest
```

- Local Memgraph on macOS/Windows (use host.docker.internal):

```bash
docker run -it memgraph/mgconsole:latest --host host.docker.internal
```

- Remote Memgraph:

```bash
docker run -it memgraph/mgconsole:latest --host <HOST> --port 7687
```

### Start mgconsole binary (macOS/Windows)

Install from Memgraph downloads, then run:

```bash
mgconsole --host 127.0.0.1 --port 7687
```

## Interactive Usage

After launch, you should see a prompt similar to:

```
mgconsole X.X
Connected to 'memgraph://127.0.0.1:7687'
Type :help for shell usage
Quit the shell by typing Ctrl-D(eof) or :quit
memgraph>
```

Run Cypher queries at the `memgraph>` prompt:

```cypher
MATCH (n) RETURN n LIMIT 10;
```

Tips:
- Use `TAB` for autocomplete.
- Use `:help` to list shell commands.
- Exit with `:quit` or Ctrl-D.

## Non-Interactive Usage (Pipelines)

Run a single query with stdin:

```bash
echo "MATCH (n:Person) RETURN n;" | docker run -i memgraph/mgconsole:latest
```

Save results to a file:

```bash
echo "MATCH (n:Person) RETURN n;" | docker run -i memgraph/mgconsole:latest > results.txt
```

## Common Flags

Use flags to configure connection and output:

- `--host` or `-host`: Memgraph host (default `127.0.0.1`)
- `--port` or `-port`: Memgraph port (default `7687`)
- `--username` / `--password`: Credentials (empty by default)
- `--output_format`: `tabular` (default), `csv`, or `cypherl`
- `--fit_to_screen`: Fit output to terminal width
- `--history`: Directory for history (default `~/.memgraph`)
- `--no_history`: Disable history persistence
- `--term_colors`: Enable terminal colors
- `--use_ssl`: Enable SSL
- `--verbose_execution_info`: Show cost, parsing, planning, execution times

## Query Execution Time Details

Enable verbose execution info to get a breakdown:

```bash
mgconsole --verbose_execution_info
```

This adds:
- COST estimate
- PARSING time
- PLANNING time
- PLAN EXECUTION time

## Reference: Full Flag List

### Connection

- `-host` (string): Server address. Default `127.0.0.1`.
- `-port` (int): Server port. Default `7687`.
- `-username` (string): Database username. Default empty.
- `-password` (string): Database password. Default empty.
- `-use_ssl` (bool): Use SSL. Default `false`.

### Output

- `-output_format` (string): `tabular` (default), `csv`, or `cypherl`.
- `-fit_to_screen` (bool): Fit output width to terminal width. Default `false`.
- `-term_colors` (bool): Enable terminal colors. Default `false`.

### History

- `-history` (string): Directory for history. Default `~/.memgraph`.
- `-no_history` (bool): Disable history persistence. Default `false`.

### Execution Details

- `-verbose_execution_info` (bool): Show cost, parsing, planning, and execution times. Default `false`.

### CSV Formatting

- `-csv_delimiter` (string): Field separator. Default ",".
- `-csv_doublequote` (bool): Use double-quoting for quotes inside fields. Default `true`.
- `-csv_escapechar` (string): Escape character when `-csv_doublequote` is `false`.

### Help and Flags

- `-help` or `-helpfull`: Show all flags.
- `-helpshort`: Show main flags only.
- `-version`: Show version and build info.
- `-flagfile`: Load flags from a file.
- `-fromenv` / `-tryfromenv`: Set flags from environment variables.

### Non-Interactive Mode

- Pipe Cypher to stdin:

```bash
echo "MATCH (n) RETURN n;" | docker run -i memgraph/mgconsole:latest
```

### Notes for macOS/Windows

- When connecting from Docker to a Memgraph instance running on the host, use:

```bash
docker run -it memgraph/mgconsole:latest --host host.docker.internal
```

## Troubleshooting

- Connection refused: verify Memgraph is running and the port is open
- Docker on macOS/Windows: use `host.docker.internal`
- Auth failures: confirm username/password and server auth settings
- No output formatting: set `--output_format tabular`

## References

- Memgraph CLI docs: https://memgraph.com/docs/getting-started/cli
