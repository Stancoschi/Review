"""Delete files older than N days. Shows what it would do unless --apply is given.

Usage:  python clean_old_files.py <folder> <days> [--apply]
"""

import sys
import time
from pathlib import Path


def main():
    if len(sys.argv) < 3:
        print("usage: python clean_old_files.py <folder> <days> [--apply]")
        return 2
    folder, apply = Path(sys.argv[1]), "--apply" in sys.argv
    try:
        days = int(sys.argv[2])
    except ValueError:
        print("days must be a number")
        return 2
    if not folder.is_dir():
        print(f"not a folder: {folder}")
        return 2

    limit = time.time() - days * 86400
    old = [p for p in folder.rglob("*") if p.is_file() and p.stat().st_mtime < limit]
    failed = 0
    for path in old:
        if not apply:
            print(f"would delete {path}")
            continue
        try:
            path.unlink()
            print(f"deleted {path}")
        except OSError as err:                    # keep going with the others
            print(f"could not delete {path}: {err}")
            failed += 1

    print(f"{len(old)} old file(s), {failed} failed" + ("" if apply else " (dry run)"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
