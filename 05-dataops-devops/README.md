# Infrastructure scripts and data structures

## Files

- `log_report.py` - reads a log, skips broken lines, prints counts per level and service and the most common errors
- `clean_old_files.py` - deletes files older than N days; only shows what it would do unless I add `--apply`
- `structures.py` - stack, queue, hash table, binary search tree and binary search, each used on a small problem
- `data/app.log` - sample log with one broken line on purpose

## Run (Python 3.10+, nothing to install)

    python log_report.py data/app.log ERROR
    python clean_old_files.py /tmp/probe 30            # dry run
    python clean_old_files.py /tmp/probe 30 --apply
    python structures.py

## Error handling

Both scripts print a clear message and return exit code 2 for bad arguments, a missing file or a missing folder. A broken log line is counted and skipped. A file that cannot be deleted is reported and the script continues with the rest (exit code 1 at the end).
