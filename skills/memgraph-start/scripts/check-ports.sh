#!/usr/bin/env bash
# Usage: check-ports.sh PORT...
# Prints one line per port: "PORT free", "PORT in use", or "PORT used by container NAME".
for p in "$@"; do
  c=$(docker ps --filter "publish=$p" --format '{{.Names}}' 2>/dev/null | paste -sd, -)
  if [ -n "$c" ]; then
    echo "$p used by container $c"
  elif (exec 3<>"/dev/tcp/127.0.0.1/$p") 2>/dev/null; then
    echo "$p in use"
  else
    echo "$p free"
  fi
done
