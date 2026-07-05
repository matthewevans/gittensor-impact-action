#!/usr/bin/env python3
"""Publish generated Gittensor impact SVGs to a dedicated Git branch."""

from __future__ import annotations

import argparse
import base64
import os
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], cwd: Path | None = None, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)
    if result.returncode != 0:
        sys.stderr.write(f"command failed: {' '.join(cmd)}\n{result.stderr}\n")
        sys.exit(result.returncode)
    return result.stdout


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="owner/name repository slug")
    parser.add_argument("--branch", required=True, help="asset branch to update")
    parser.add_argument("--message", default="chore: update Gittensor impact assets")
    parser.add_argument("--workdir", required=True, type=Path)
    parser.add_argument("assets", nargs="+", type=Path)
    args = parser.parse_args()

    missing = [str(path) for path in args.assets if not path.exists()]
    if missing:
        sys.exit(f"missing asset(s): {', '.join(missing)}")

    if args.workdir.exists():
        shutil.rmtree(args.workdir)
    args.workdir.mkdir(parents=True)

    run(["git", "init", "-b", args.branch], args.workdir)
    run(["git", "remote", "add", "origin", f"https://github.com/{args.repo}.git"], args.workdir)
    run(["git", "config", "user.name", "github-actions[bot]"], args.workdir)
    run([
        "git",
        "config",
        "user.email",
        "41898282+github-actions[bot]@users.noreply.github.com",
    ], args.workdir)

    for asset in args.assets:
        shutil.copy2(asset, args.workdir / asset.name)

    run(["git", "add", "."], args.workdir)
    diff = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=args.workdir,
        capture_output=True,
        text=True,
    )
    if diff.returncode == 0:
        print("No asset changes to publish.")
        return

    run(["git", "commit", "-m", args.message], args.workdir)
    env = os.environ.copy()
    token = env.get("GH_TOKEN")
    if token:
        auth = base64.b64encode(f"x-access-token:{token}".encode()).decode()
        env["GIT_CONFIG_COUNT"] = "1"
        env["GIT_CONFIG_KEY_0"] = "http.https://github.com/.extraheader"
        env["GIT_CONFIG_VALUE_0"] = f"AUTHORIZATION: basic {auth}"
    run(["git", "push", "--force", "origin", f"HEAD:{args.branch}"], args.workdir, env)

    base = f"https://raw.githubusercontent.com/{args.repo}/{args.branch}"
    for asset in args.assets:
        print(f"{base}/{asset.name}")


if __name__ == "__main__":
    main()
