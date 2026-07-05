#!/usr/bin/env python3
"""Publish generated Gittensor impact SVGs as stable GitHub release assets."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        sys.stderr.write(f"command failed: {' '.join(cmd)}\n{result.stderr}\n")
        sys.exit(result.returncode)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="owner/name repository slug")
    parser.add_argument("--tag", required=True, help="stable release tag")
    parser.add_argument("--title", default="Gittensor Impact Assets")
    parser.add_argument(
        "--notes",
        default="Generated SVG assets for the Gittensor repository impact card.",
    )
    parser.add_argument("assets", nargs="+", type=Path)
    args = parser.parse_args()

    missing = [str(path) for path in args.assets if not path.exists()]
    if missing:
        sys.exit(f"missing asset(s): {', '.join(missing)}")

    view = run(["gh", "release", "view", args.tag, "--repo", args.repo], check=False)
    if view.returncode != 0:
        run([
            "gh",
            "release",
            "create",
            args.tag,
            "--repo",
            args.repo,
            "--title",
            args.title,
            "--notes",
            args.notes,
            "--latest=false",
        ])

    run([
        "gh",
        "release",
        "upload",
        args.tag,
        *[str(path) for path in args.assets],
        "--repo",
        args.repo,
        "--clobber",
    ])

    base = f"https://github.com/{args.repo}/releases/download/{args.tag}"
    for asset in args.assets:
        print(f"{base}/{asset.name}")


if __name__ == "__main__":
    main()
