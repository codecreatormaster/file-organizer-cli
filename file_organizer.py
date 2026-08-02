#!/usr/bin/env python3
"""
File Organizer & Report Generator
-----------------------------------
A command-line tool that automatically organizes files in a directory
by file extension or by last-modified date, and generates a JSON report
summarizing what was done.

Why this project exists:
    Manually sorting downloads, screenshots, and documents is a repetitive
    task perfect for automation. This script demonstrates core IT
    automation skills: file-system operations, CLI design, logging,
    error handling, and generating structured reports.

Usage:
    python file_organizer.py --source ~/Downloads --mode extension
    python file_organizer.py --source ~/Downloads --mode date --dry-run
    python file_organizer.py --source ~/Downloads --mode extension --report report.json

Author: (your name here)
"""

import argparse
import json
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Configure and return a logger for the script."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger("file_organizer")


def get_destination_folder(file_path: Path, mode: str) -> str:
    """
    Determine which subfolder a file should be moved into.

    mode="extension" -> group by file type, e.g. "PDF", "IMAGES", "OTHER"
    mode="date"       -> group by year-month of last modification, e.g. "2026-08"
    """
    if mode == "extension":
        ext = file_path.suffix.lower().lstrip(".")
        category_map = {
            "images": {"jpg", "jpeg", "png", "gif", "webp", "svg", "heic"},
            "documents": {"pdf", "doc", "docx", "txt", "md", "rtf"},
            "spreadsheets": {"xls", "xlsx", "csv"},
            "code": {"py", "js", "html", "css", "json", "java", "cpp", "sql"},
            "archives": {"zip", "rar", "7z", "tar", "gz"},
            "audio_video": {"mp3", "mp4", "mov", "wav", "avi"},
        }
        for category, extensions in category_map.items():
            if ext in extensions:
                return category.upper()
        return "OTHER" if ext else "NO_EXTENSION"

    elif mode == "date":
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        return mtime.strftime("%Y-%m")

    else:
        raise ValueError(f"Unknown mode: {mode}")


def organize_files(
    source_dir: Path, mode: str, dry_run: bool, logger: logging.Logger
) -> Dict:
    """
    Walk through source_dir (non-recursively) and move each file into a
    subfolder determined by get_destination_folder(). Returns a summary
    report dict.
    """
    report = {
        "source_directory": str(source_dir),
        "mode": mode,
        "dry_run": dry_run,
        "timestamp": datetime.now().isoformat(),
        "moved": [],
        "skipped": [],
        "errors": [],
    }

    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory does not exist: {source_dir}")

    files = [f for f in source_dir.iterdir() if f.is_file()]
    logger.info("Found %d file(s) in %s", len(files), source_dir)

    for file_path in files:
        try:
            destination_folder_name = get_destination_folder(file_path, mode)
            destination_folder = source_dir / destination_folder_name
            destination_path = destination_folder / file_path.name

            if destination_path.exists():
                logger.warning("Skipping (already exists): %s", file_path.name)
                report["skipped"].append(file_path.name)
                continue

            if dry_run:
                logger.info(
                    "[DRY RUN] Would move %s -> %s/",
                    file_path.name,
                    destination_folder_name,
                )
            else:
                destination_folder.mkdir(exist_ok=True)
                shutil.move(str(file_path), str(destination_path))
                logger.info("Moved %s -> %s/", file_path.name, destination_folder_name)

            report["moved"].append(
                {"file": file_path.name, "destination": destination_folder_name}
            )

        except Exception as exc:  # noqa: BLE001 - report all errors, don't crash
            logger.error("Error processing %s: %s", file_path.name, exc)
            report["errors"].append({"file": file_path.name, "error": str(exc)})

    return report


def save_report(report: Dict, report_path: Path, logger: logging.Logger) -> None:
    """Write the report dict to a JSON file."""
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    logger.info("Report saved to %s", report_path)


def parse_args(argv: List[str] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Organize files in a directory by extension or date."
    )
    parser.add_argument(
        "--source", required=True, type=Path, help="Directory to organize"
    )
    parser.add_argument(
        "--mode",
        choices=["extension", "date"],
        default="extension",
        help="How to group files (default: extension)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without moving any files",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("organize_report.json"),
        help="Path to save the JSON summary report",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable debug-level logging"
    )
    return parser.parse_args(argv)


def main(argv: List[str] = None) -> int:
    args = parse_args(argv)
    logger = setup_logging(args.verbose)

    try:
        report = organize_files(args.source, args.mode, args.dry_run, logger)
        save_report(report, args.report, logger)
    except Exception as exc:  # noqa: BLE001
        logger.error("Fatal error: %s", exc)
        return 1

    logger.info(
        "Done. Moved: %d | Skipped: %d | Errors: %d",
        len(report["moved"]),
        len(report["skipped"]),
        len(report["errors"]),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
