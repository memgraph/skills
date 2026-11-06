"""Bump the version pins in this repo to the latest releases.

Pins:
- memgraph/memgraph-mage:X.Y.Z and memgraph/lab:X.Y.Z (Docker Hub), in skills
- mcp-memgraph==X.Y.Z (PyPI), in the plugin manifests

When any pin changes, the plugin's patch version is bumped too, so plugin users
receive the update. Prints a Markdown summary of the changes.
"""

import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

PLAIN = re.compile(r"^\d+\.\d+\.\d+$")
MANIFESTS = [Path(".claude-plugin/plugin.json"), Path(".codex-plugin/plugin.json"), Path("plugin.json")]


def get_json(url):
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.load(response)


def latest_docker_tag(repo):
    data = get_json(f"https://hub.docker.com/v2/repositories/{repo}/tags?page_size=100&ordering=last_updated")
    tags = [t["name"] for t in data["results"] if PLAIN.match(t["name"])]
    return max(tags, key=lambda v: tuple(map(int, v.split("."))))


def latest_pypi(package):
    return get_json(f"https://pypi.org/pypi/{package}/json")["info"]["version"]


def tracked_files():
    out = subprocess.run(["git", "ls-files"], capture_output=True, text=True, check=True).stdout
    return [Path(p) for p in out.splitlines() if p.endswith((".md", ".json", ".sh", ".yml", ".yaml"))]


def main():
    pins = {
        r"memgraph/memgraph-mage:(\d+\.\d+\.\d+)\b": ("memgraph/memgraph-mage:{}", latest_docker_tag("memgraph/memgraph-mage")),
        r"memgraph/lab:(\d+\.\d+\.\d+)\b": ("memgraph/lab:{}", latest_docker_tag("memgraph/lab")),
        r"mcp-memgraph==(\d+\.\d+\.\d+)\b": ("mcp-memgraph=={}", latest_pypi("mcp-memgraph")),
    }
    changes = []
    for path in tracked_files():
        text = path.read_text()
        new = text
        for pattern, (template, latest) in pins.items():
            for old in set(re.findall(pattern, new)):
                if old != latest:
                    new = new.replace(template.format(old), template.format(latest))
                    changes.append(f"- `{path}`: `{template.format(old)}` → `{template.format(latest)}`")
        if new != text:
            path.write_text(new)

    if not changes:
        print("All pins are up to date.", file=sys.stderr)
        return

    for manifest in MANIFESTS:
        if not manifest.exists():
            continue
        text = manifest.read_text()
        match = re.search(r'"version": "(\d+)\.(\d+)\.(\d+)"', text)
        if match:
            major, minor, patch = match.groups()
            bumped = f"{major}.{minor}.{int(patch) + 1}"
            manifest.write_text(text.replace(match.group(0), f'"version": "{bumped}"', 1))
            changes.append(f"- `{manifest}`: plugin version {major}.{minor}.{patch} → {bumped}")

    print("Bumps the version pins to the latest releases:\n")
    print("\n".join(sorted(set(changes))))
    print("\nRun the `memgraph-start` skill once against the new images before merging.")


if __name__ == "__main__":
    main()
