#!/usr/bin/env python3
"""Explicitly provision the fixed NAIF kernel set recorded in the manifest."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
from urllib.request import Request, urlopen

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DESTINATION = PROJECT_ROOT / "data" / "kernels"
MANIFEST = DESTINATION / "manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def provision(entry: dict[str, str]) -> None:
    filename = entry["filename"]
    destination = DESTINATION / filename
    expected = entry["sha256"].lower()
    if destination.exists():
        actual = sha256(destination)
        if actual == expected:
            print(f"OK already provisioned: {filename}")
            return
        raise RuntimeError(
            f"Refusing to overwrite existing {filename}: SHA-256 {actual}, expected {expected}. "
            "Move the file aside manually after investigating it."
        )

    request = Request(entry["url"], headers={"User-Agent": "ashuraslight-kernel-provisioner/1.0"})
    temporary: Path | None = None
    try:
        with urlopen(request, timeout=60) as response, tempfile.NamedTemporaryFile(
            mode="wb", dir=DESTINATION, prefix=f".{filename}.", delete=False
        ) as output:
            temporary = Path(output.name)
            digest = hashlib.sha256()
            while True:
                block = response.read(1024 * 1024)
                if not block:
                    break
                output.write(block)
                digest.update(block)
        actual = digest.hexdigest()
        if actual != expected:
            raise RuntimeError(
                f"Downloaded {filename} SHA-256 mismatch: got {actual}, expected {expected}."
            )
        # Use a non-overwriting hard link so a concurrent/pre-existing file is preserved.
        os.link(temporary, destination)
        print(f"Downloaded and verified: {filename} ({actual})")
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main() -> int:
    if not MANIFEST.is_file():
        print(f"Missing manifest: {MANIFEST}", file=sys.stderr)
        return 2
    DESTINATION.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    try:
        for entry in manifest["kernels"]:
            provision(entry)
    except Exception as exc:
        print(f"Kernel provisioning stopped: {exc}", file=sys.stderr)
        return 1
    print(f"All manifest assets are present and verified in {DESTINATION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
