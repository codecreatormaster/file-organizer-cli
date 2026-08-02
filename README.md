# File Organizer & Report Generator

A command-line tool that automatically organizes messy folders (like Downloads)
by file type or date, with a dry-run mode and a JSON report of every action taken.

## Why I built this

Manually sorting downloaded files is a repetitive task that's perfect for
automation. This project applies core scripting and automation concepts —
CLI design, file-system operations, logging, and error handling — to a
real, everyday problem.

## Features

- **Two organization modes:** by file extension (Images, Documents, Spreadsheets,
  Code, Archives, Audio/Video) or by last-modified date (`YYYY-MM` folders)
- **Dry-run mode** — preview exactly what would happen before touching any files
- **JSON reports** — every run generates a structured summary of files moved,
  skipped, and any errors encountered
- **Logging** — timestamped, leveled logs for visibility into what the script is doing
- **Unit tested** — 8 tests covering the core logic and edge cases (missing
  directories, unknown file types, dry-run behavior)

## Usage

```bash
# Preview what would happen (no files are moved)
python file_organizer.py --source ~/Downloads --mode extension --dry-run

# Actually organize files by type
python file_organizer.py --source ~/Downloads --mode extension

# Organize by the month files were last modified
python file_organizer.py --source ~/Downloads --mode date

# Save the report to a custom location
python file_organizer.py --source ~/Downloads --mode extension --report ~/reports/organize.json
```

## Example report output

```json
{
  "source_directory": "/home/user/Downloads",
  "mode": "extension",
  "dry_run": false,
  "timestamp": "2026-08-01T10:15:00",
  "moved": [
    {"file": "invoice.pdf", "destination": "DOCUMENTS"},
    {"file": "vacation.jpg", "destination": "IMAGES"}
  ],
  "skipped": [],
  "errors": []
}
```

## Running the tests

```bash
python -m unittest test_file_organizer.py -v
```

## Tech used

Python 3, `argparse`, `pathlib`, `shutil`, `logging`, `unittest` — all standard
library, no external dependencies required.

## Possible next steps

- Add a `--undo` flag that reverses the last run using the saved report
- Support recursive organizing through subdirectories
- Add a config file for custom category-to-extension mappings
