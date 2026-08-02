"""
Unit tests for file_organizer.py

Run with:
    python -m unittest test_file_organizer.py -v
"""

import shutil
import tempfile
import unittest
from pathlib import Path

from file_organizer import get_destination_folder, organize_files, setup_logging


class TestGetDestinationFolder(unittest.TestCase):
    def test_extension_mode_groups_images(self):
        result = get_destination_folder(Path("photo.jpg"), mode="extension")
        self.assertEqual(result, "IMAGES")

    def test_extension_mode_groups_documents(self):
        result = get_destination_folder(Path("resume.pdf"), mode="extension")
        self.assertEqual(result, "DOCUMENTS")

    def test_extension_mode_unknown_extension_goes_to_other(self):
        result = get_destination_folder(Path("mystery.xyz"), mode="extension")
        self.assertEqual(result, "OTHER")

    def test_extension_mode_no_extension(self):
        result = get_destination_folder(Path("README"), mode="extension")
        self.assertEqual(result, "NO_EXTENSION")

    def test_invalid_mode_raises(self):
        with self.assertRaises(ValueError):
            get_destination_folder(Path("file.txt"), mode="not_a_real_mode")


class TestOrganizeFiles(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory with a few sample files
        self.temp_dir = Path(tempfile.mkdtemp())
        (self.temp_dir / "photo1.jpg").write_text("fake image data")
        (self.temp_dir / "notes.txt").write_text("fake text data")
        (self.temp_dir / "data.csv").write_text("col1,col2\n1,2")
        self.logger = setup_logging()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_dry_run_does_not_move_files(self):
        organize_files(self.temp_dir, mode="extension", dry_run=True, logger=self.logger)
        # Files should still be in the root, no subfolders created
        self.assertTrue((self.temp_dir / "photo1.jpg").exists())
        self.assertFalse((self.temp_dir / "IMAGES").exists())

    def test_real_run_moves_files_into_subfolders(self):
        report = organize_files(
            self.temp_dir, mode="extension", dry_run=False, logger=self.logger
        )
        self.assertTrue((self.temp_dir / "IMAGES" / "photo1.jpg").exists())
        self.assertTrue((self.temp_dir / "DOCUMENTS" / "notes.txt").exists())
        self.assertTrue((self.temp_dir / "SPREADSHEETS" / "data.csv").exists())
        self.assertEqual(len(report["moved"]), 3)
        self.assertEqual(len(report["errors"]), 0)

    def test_missing_source_directory_raises(self):
        fake_dir = self.temp_dir / "does_not_exist"
        with self.assertRaises(FileNotFoundError):
            organize_files(fake_dir, mode="extension", dry_run=False, logger=self.logger)


if __name__ == "__main__":
    unittest.main()
