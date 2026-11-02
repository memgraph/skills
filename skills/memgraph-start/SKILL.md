---
name: memgraph-start
description: >-
  Get a new user from nothing to a working Memgraph in a few minutes: start
  Memgraph with MAGE and Memgraph Lab in Docker, load a sample dataset the user
  picks, run a first query and a graph algorithm, then point to the docs guide
  for what the user is building and offer optional AI memory. Use when the user asks to get started with Memgraph, set up
  or try Memgraph locally, run Memgraph in Docker for the first time, or load a
  sample graph dataset.
compatibility: Docker and curl on macOS or Linux. Uses the Memgraph docs MCP and Memgraph MCP servers when they are connected.
metadata:
  version: "0.0.1"
  author: memgraph
---

# Getting started with Memgraph

Walk the user through these steps in order. Keep each step short: say what you
are about to do, show the command, run it once the user agrees, and report the
result in one or two lines.

Rules for every step:

- Ask before any command that starts containers or loads data. If your agent
  already asks the user to approve each command, that approval is the ask:
  explain the command in one line and run it, without asking again in chat.
- Never stop, restart, reuse or change a Memgraph container or database the user
  already has. Only touch the containers you start in this flow.
- If a step fails, show the error, explain it in one sentence, and stop. Don't
  try alternatives on your own.

## 1. Check Docker

```shell
docker info --format '{{.ServerVersion}}'
```

If this fails:

- "Cannot connect to the Docker daemon" or similar: ask the user to start Docker
  (Docker Desktop on macOS, the Docker service on Linux).
- "permission denied" on the Docker socket while you run in a sandbox (Codex
  and other agents sandbox commands by default): the sandbox blocks Docker, and
  the later `curl` download needs network access too. Run this and the later
  `docker` and `curl` commands outside the sandbox, which needs the user's
  approval, instead of stopping.
- "permission denied" on Linux outside a sandbox: Docker is running, but the
  user can't use it without `sudo`. Ask them to add themselves to the `docker`
  group (then log out and in) or to run the commands with `sudo`.

Then run it again.

## 2. Choose the ports

The Memgraph MCP server connects to `bolt://localhost:7687` unless
`MEMGRAPH_URL` is set, so use port `7687` whenever it's free. Check the Bolt
port (`7687`), the log port (`7444`) and the Lab port (`3000`) with the
`scripts/check-ports.sh` script in this skill's folder. It prints the container
that holds a port, or "in use" for anything else:

```shell
bash <this skill's folder>/scripts/check-ports.sh 7687 7444 3000
```

- **All free:** use `7687`, `7444` and `3000`.
- **`7687` in use:** another Memgraph (or another service) is already running.
  Tell the user what holds it, and ask which they want:
  1. **Use the existing Memgraph on `7687`.** Only if it's a Memgraph the user
     wants to try things on. If the container is `context-graph-memgraph`,
     that's their AI Memory store: say so and recommend option 2. In this path:
     skip step 4; don't load a dataset unless the user explicitly says that
     database can be changed; ask for its container name before running any
     `docker exec`, or use the Memgraph MCP server instead; and if
     `SHOW SCHEMA INFO` fails (the server wasn't started with
     `--schema-info-enabled`), use the Memgraph MCP server's schema tools or
     `CALL schema.node_type_properties()` instead.
  2. **Start a new Memgraph on free ports**, e.g. `7688` and `7445` (check them
     the same way). Then find out where the Memgraph MCP server points; it
     reads the same `MEMGRAPH_URL` your shell commands see:

     ```shell
     printenv MEMGRAPH_URL || echo "not set"
     ```

     - If it's the new Bolt port (e.g. `bolt://localhost:7688`), the MCP
       server already points at the new Memgraph. Say so and use it.
     - If it's not set or a different URL, the MCP server points at `7687` (or
       that URL), not at the new Memgraph. Tell the user that to use it with the
       new Memgraph, they run `export MEMGRAPH_URL=bolt://localhost:7688` and
       start the agent again from that same shell. Until then, run queries with
       `mgconsole` inside the container (see step 5).
- **Only `3000` or `7444` in use:** pick the next free port (`3001`, `7445`, …)
  and tell the user.

Use the chosen ports in every command below. The examples use `7687`, `7444`
and `3000`.

## 3. Choose a dataset

If you can't show a question form, ask this together with any open question
from step 2 in one short message with numbered options, and wait for the answer
before running anything else.

Offer exactly four choices: the three datasets below and "See the other
datasets" (there are more than 30 others). Some question tools allow only four
options, so don't add more. Don't refer to how your question interface looks,
such as an "Other" option; the user can also name any dataset in their own
words:

| Dataset | Slug | Size | Good for |
| --- | --- | --- | --- |
| Capital cities and borders (default) | `country-capitals` | 212 nodes, 369 relationships | Paths between cities, PageRank, a map in Lab |
| Game of Thrones deaths | `game-of-thrones-deaths` | 2,677 nodes, 11,967 relationships | Who killed whom, centrality |
| The Pandora Papers | `icij-pandora-papers` | 389 nodes, 740 relationships | Following officials to offshore companies in a few hops |

The full catalog, with each dataset's description, graph model, sample queries
and download link, is at `https://download.memgraph.com/datasets/items.v1.json`
(the `datasets` list; each item has `slug`, `title`, `description`, `counts`,
`graphModel.description`, `sampleQueries` and `formats.cypherl.url`). If the
user wants to see the others, read it and list every dataset as its title, its
`description` and its size, so they can choose by name. Also read it for the
graph model and sample queries of the chosen dataset.

## 4. Start Memgraph and Memgraph Lab

Start both on their own Docker network, so Lab reaches Memgraph by container
name on any OS. If the names `memgraph` or `memgraph-lab` are taken, add a
suffix (`memgraph-2`) and use it everywhere below.

```shell
docker network create memgraph-start 2>/dev/null || true
docker run -d --name memgraph --network memgraph-start \
  -p 7687:7687 -p 7444:7444 \
  memgraph/memgraph-mage:3.14.0 --schema-info-enabled=true
docker run -d --name memgraph-lab --network memgraph-start -p 3000:3000 \
  -e QUICK_CONNECT_MG_HOST=memgraph -e QUICK_CONNECT_MG_PORT=7687 \
  memgraph/lab:3.14.1
```

Keep the image tags as written: they're the versions this skill is tested with.
`QUICK_CONNECT_MG_PORT` is the port inside the network, so it stays `7687` even
when the published port is different.

Wait until Memgraph accepts queries (about 20 seconds; the port opens before
Memgraph is ready) with the `scripts/wait-ready.sh` script in this skill's
folder, passing the container name:

```shell
bash <this skill's folder>/scripts/wait-ready.sh memgraph
```

It prints `ready after Ns`, or after two minutes the container status and its
last log lines. In that case, show them to the user and stop.

While Memgraph starts, the Memgraph MCP server answers "Could not connect …
ensure the URL is correct". That only means "not ready yet": wait and retry,
don't change the URL.

These containers have no volume, so the data is gone when the `memgraph`
container is removed. That's fine for trying Memgraph; for persistent data, see
`https://memgraph.com/docs/getting-started/install-memgraph/docker.md`.

## 5. Load the dataset

Loading writes to the new database, so ask first. Use the dataset's
`formats.cypherl.url` from the catalog, or this pattern:

```shell
curl -fsSL https://download.memgraph.com/datasets/country-capitals/cypherl/dataset.cypherl.gz \
  | gunzip | docker exec -i memgraph mgconsole
```

Then check the counts:

```shell
echo 'MATCH (n) RETURN count(n) AS nodes;' | docker exec -i memgraph mgconsole
```

They should match the dataset's `counts`.

## 6. Run a first query and an algorithm

Use the Memgraph MCP server if it points at this Memgraph (see step 2):
`7687` when you started Memgraph there, otherwise when `MEMGRAPH_URL` is the new
port. Before the first query, confirm it with the node count from the MCP
server: it should match the counts from step 5. If it doesn't, the MCP server
is talking to another Memgraph, so stop using it and pipe the queries into
`mgconsole` as above.

1. **Look at the schema** with the Memgraph MCP server, or with
   `SHOW SCHEMA INFO;`.
2. **Run one of the dataset's `sampleQueries`** and show the result.
3. **Run PageRank** from MAGE (see the `memgraph-run-mage-algorithms` skill) and
   show the top five, using a property that names the nodes (`name` for
   capital cities):

   ```cypher
   CALL pagerank.get() YIELD node, rank
   RETURN node.name AS name, rank
   ORDER BY rank DESC LIMIT 5;
   ```

4. Point the user to Memgraph Lab at `http://localhost:3000` (use the Lab port
   you chose): they click **Connect now**, paste a query into the Cypher
   editor and click **Run query**. Give them the exact query to paste, one that
   returns nodes, relationships or paths (not a table), so the **Graph
   results** tab can draw it. Use the dataset's sample query as written in the
   catalog; if you changed it to get a table above, give the original. For
   capital cities, Lab draws the cities on a world map because every city has
   `lat` and `lng`.

## 7. Point to the next guide

Ask what the user is building and in which language. Search the Memgraph docs
MCP server for the guide that fits (for example, the client library for their
language, importing their data, or GraphRAG), and give them that page with a
one-line summary. If the docs MCP isn't connected, read the docs as Markdown by
adding `.md` to a `https://memgraph.com/docs/` URL.

## 8. Offer AI memory (optional)

Ask once: "Want your coding agents to remember across sessions? Memgraph AI
Memory stores sessions and memories in Memgraph." Only on yes, show the
installer command and run it once the user agrees:

```shell
curl -fsSL https://raw.githubusercontent.com/memgraph/ai-toolkit/main/context-graph/scripts/install.sh | bash
```

The installer sets up the CLI and the agent plugins, and by default starts its
own Memgraph with a volume, so memories survive restarts. Recommend that over
the onboarding Memgraph, which has no volume. The user restarts the agent after
installing.

## 9. Wrap up

Summarize in a few lines: what's running and on which ports, which dataset is
loaded, how to stop everything, and two next steps that fit what the user said
they're building. Say that the data is gone once the `memgraph` container is
removed, and link
`https://memgraph.com/docs/getting-started/install-memgraph/docker` for keeping
it.

To stop everything, give the command with the names this flow actually started
(by default `docker rm -f memgraph memgraph-lab && docker network rm memgraph-start`).
Never include a container this flow didn't start.

If the user installed this as a Claude Code or Codex plugin, mention that
plugin updates arrive only when they update the marketplace or turn on
auto-update for it.
