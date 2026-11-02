#!/usr/bin/env bash
# Usage: wait-ready.sh [CONTAINER] [SECONDS]
# Waits until Memgraph in CONTAINER (default: memgraph) answers a query, for at
# most SECONDS (default: 120). On timeout, prints the container status and its
# last log lines and exits 1.
name=${1:-memgraph}
limit=${2:-120}
start=$(date +%s)
while true; do
  if echo 'RETURN 1;' | docker exec -i "$name" mgconsole >/dev/null 2>&1; then
    echo "ready after $(( $(date +%s) - start ))s"
    exit 0
  fi
  if [ $(( $(date +%s) - start )) -ge "$limit" ]; then
    echo "not ready after ${limit}s"
    docker ps -a --filter "name=^${name}$" --format '{{.Names}} {{.Status}}'
    docker logs --tail 20 "$name" 2>&1
    exit 1
  fi
  sleep 2
done
