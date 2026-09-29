"""
check_chatmode_alignment.py
B-005 / B-017 support — verifies every .chatmode.md file has a corresponding
*-agent/ folder and vice-versa.

Usage (standalone):
    python -m scripts.check_chatmode_alignment [--root <workspace_root>] [--allowlist master-agent,...]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _agent_name_from_chatmode(chatmode_file: Path) -> str:
    """'inventory-scout.chatmode.md' → 'inventory-scout'."""
    return chatmode_file.name.replace(".chatmode.md", "")


def _agent_name_from_folder(folder: Path) -> str:
    """'inventory-scout-agent' → 'inventory-scout'."""
    return folder.name.replace("-agent", "")


def find_mismatches(
    root: Path,
    allowlist: set[str],
) -> tuple[list[str], list[str]]:
    """Return (missing_folders, orphan_folders).

    missing_folders: agent names that have a chatmode but no *-agent/ directory,
                     excluding the allowlist.
    orphan_folders:  agent names that have a *-agent/ directory but no chatmode.
    """
    chatmode_dir = root / ".github" / "agents"
    chatmode_names: set[str] = set()
    if chatmode_dir.exists():
        for f in chatmode_dir.glob("*.chatmode.md"):
            chatmode_names.add(_agent_name_from_chatmode(f))

    agent_folders: set[str] = set()
    for folder in root.iterdir():
        if folder.is_dir() and folder.name.endswith("-agent"):
            agent_folders.add(_agent_name_from_folder(folder))

    missing_folders = sorted(
        (chatmode_names - agent_folders) - allowlist
    )
    orphan_folders = sorted(
        [f"{name}-agent" for name in (agent_folders - chatmode_names)]
    )
    return missing_folders, orphan_folders


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check chatmode ↔ agent-folder alignment")
    parser.add_argument("--root", default=".", help="Workspace root (default: .)")
    parser.add_argument(
        "--allowlist",
        default="master-agent",
        help="Comma-separated chatmode names allowed without an agent folder",
    )
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    allowlist = {a.strip() for a in args.allowlist.split(",") if a.strip()}

    missing, orphans = find_mismatches(root, allowlist=allowlist)

    ok = True
    if missing:
        print("ERROR: chatmodes without an agent folder:")
        for name in missing:
            print(f"  - {name}.chatmode.md  (expected: {name}-agent/)")
        ok = False
    if orphans:
        print("WARNING: agent folders without a chatmode:")
        for name in orphans:
            print(f"  - {name}/  (expected: {name.replace('-agent', '')}.chatmode.md)")

    if ok and not orphans:
        print("OK: all chatmodes and agent folders are aligned.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
