"""Copy the pre-rendered entry.png into /output/entry.png.

Runs on the scoring machine: Python 3.13, read-only filesystem,
/output is writable, 60 second limit, no Pillow. Standard library only.
"""

import hashlib
import os
import shutil
import sys
from pathlib import Path


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    src = Path(__file__).resolve().parent / "entry.png"
    dst = Path("/output/entry.png")

    try:
        os.makedirs("/output", exist_ok=True)
    except OSError as exc:
        print(f"ERROR: cannot create /output: {exc}")
        return 1

    if not src.is_file():
        print(f"ERROR: source image not found: {src}")
        return 1

    try:
        shutil.copyfile(src, dst)
    except OSError as exc:
        print(f"ERROR: copy failed: {exc}")
        return 1

    try:
        src_hash = sha256_of(src)
        dst_hash = sha256_of(dst)
    except OSError as exc:
        print(f"ERROR: cannot verify files: {exc}")
        return 1
    if src_hash != dst_hash:
        print(f"ERROR: sha256 mismatch: src={src_hash} dst={dst_hash}")
        return 1

    try:
        size = dst.stat().st_size
    except OSError as exc:
        print(f"ERROR: cannot stat output: {exc}")
        return 1
    if size == 0:
        print("ERROR: output file is empty")
        return 1
    print(f"OK: copied {size} bytes to {dst} (sha256 {dst_hash})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
