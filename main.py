"""Gauge test runner — thin wrapper around `gauge run` CLI."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(specs: str = "", tags: str = "", parallel: bool = False, env: str = "default") -> None:
    """Invoke `gauge run` with the project-configured defaults."""
    cmd = ["gauge", "run"]

    if specs:
        cmd.append(specs)
    if tags:
        cmd.extend(["--tags", tags])
    if parallel:
        cmd.extend(["--parallel", "-n", str(parallel) if isinstance(parallel, int) else "4"])
    if env:
        cmd.extend(["--env", env])

    cmd.extend(["--log-level", "error"])

    print(f"[run] {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(ROOT))
    sys.exit(result.returncode)


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Gauge test runner for USM V9")
    p.add_argument("specs", nargs="?", default="",
                   help="spec file/dir to run (relative to project root), e.g. specs/user")
    p.add_argument("-t", "--tags", default="",
                   help="filter specs by tags, e.g. 'P1 & asset'")
    p.add_argument("-p", "--parallel", action="store_true",
                   help="run specs in parallel (default: serial)")
    p.add_argument("-n", "--parallel-nodes", type=int, default=4,
                   help="parallel node count (default: 4)")
    p.add_argument("-e", "--env", default="default",
                   help="gauge env name (default: default)")
    args = p.parse_args()

    parallel = args.parallel_nodes if args.parallel else False
    run(specs=args.specs, tags=args.tags, parallel=parallel, env=args.env)
