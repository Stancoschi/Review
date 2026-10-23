"""Count log lines by level and service, and show the most common errors.

Usage:  python log_report.py data/app.log [ERROR]
"""

import re
import sys
from collections import Counter

LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
LINE = re.compile(r"^(\S+ \S+) (DEBUG|INFO|WARNING|ERROR|CRITICAL) \[(\w+)\] (.*)$")


def main():
    if len(sys.argv) < 2:
        print("usage: python log_report.py <logfile> [min_level]")
        return 2
    path = sys.argv[1]
    min_level = sys.argv[2] if len(sys.argv) > 2 else "ERROR"
    if min_level not in LEVELS:
        print(f"unknown level {min_level}, use one of {LEVELS}")
        return 2

    levels, services, messages = Counter(), Counter(), Counter()
    skipped = 0
    try:
        with open(path, encoding="utf-8") as log:
            for line in log:
                match = LINE.match(line.strip())
                if not match:
                    skipped += 1                  # broken line: count it, go on
                    continue
                _, level, service, message = match.groups()
                levels[level] += 1
                if LEVELS.index(level) >= LEVELS.index(min_level):
                    services[service] += 1
                    messages[message] += 1
    except OSError as err:
        print(f"cannot read {path}: {err}")
        return 2

    print(f"skipped broken lines: {skipped}\n")
    print("Lines per level:")
    for level in LEVELS:
        print(f"  {level:<9}{levels[level]:>4}")
    print(f"\n{min_level} and above, per service:")
    for service, count in services.most_common():
        print(f"  {service:<9}{count:>4}")
    print("\nMost common messages:")
    for message, count in messages.most_common(3):
        print(f"  {count} x {message}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
