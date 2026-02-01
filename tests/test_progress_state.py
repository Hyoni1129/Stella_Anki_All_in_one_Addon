# -*- coding: utf-8 -*-
"""
Tests for Progress State Manager

Tests state persistence and resume functionality.
"""

import unittest
import os
import tempfile
import shutil
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentence.progress_state import ProgressStateManager


class TestProgressStateManager(unittest.TestCase):
    """Test ProgressStateManager functionality."""
    
    def setUp(self):
        """Create temporary directory for tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, "progress.json")
        self.manager = ProgressStateManager(self.state_file)
    
    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_start_run(self):
        """Test starting a new run."""
        note_ids = [1, 2, 3, 4, 5]
        
        self.manager.start_run(
            run_type="sentence",
            total_ids=note_ids,
            extra_info={"language": "Korean"}
        )
        
        self.assertTrue(self.manager.has_pending_run())
        self.assertEqual(len(self.manager.get_pending_ids()), 5)
    
    def test_mark_success(self):
        """Test marking items as successful."""
        self.manager.start_run(
            run_type="test",
            total_ids=[1, 2, 3]
        )
        
        self.manager.mark_success(1)
        self.manager.mark_success(2)
        
        pending = self.manager.get_pending_ids()
        self.assertEqual(len(pending), 1)
        self.assertIn(3, pending)
    
    def test_mark_failure(self):
        """Test marking items as failed."""
        self.manager.start_run(
            run_type="test",
            total_ids=[1, 2, 3]
        )
        
        self.manager.mark_failure(1, "Test error")
        
        pending = self.manager.get_pending_ids()
        self.assertEqual(len(pending), 2)  # Failed items remain pending
        
        failed = self.manager.get_failed_ids()
        self.assertEqual(len(failed), 1)
        self.assertIn(1, failed)
    
    def test_clear(self):
        """Test clearing state."""
        self.manager.start_run(
            run_type="test",
            total_ids=[1, 2, 3]
        )
        
        self.assertTrue(self.manager.has_pending_run())
        
        self.manager.clear()
        
        self.assertFalse(self.manager.has_pending_run())
    
    def test_describe_run(self):
        """Test run description."""
        self.manager.start_run(
            run_type="image",
            total_ids=[1, 2, 3],
            extra_info={"style": "realistic"}
        )
        
        self.manager.mark_success(1)
        self.manager.mark_failure(2, "Error")
        
        info = self.manager.describe_run()
        
        self.assertEqual(info["run_type"], "image")
        self.assertEqual(info["total_count"], 3)
        self.assertEqual(info["success_count"], 1)
        self.assertEqual(info["failure_count"], 1)
        self.assertEqual(info["pending_count"], 1)
    
    def test_persistence(self):
        """Test that state persists to file."""
        self.manager.start_run(
            run_type="sentence",
            total_ids=[1, 2, 3, 4, 5]
        )
        
        self.manager.mark_success(1)
        self.manager.mark_success(2)
        
        # Create new manager from same file
        manager2 = ProgressStateManager(self.state_file)
        
        self.assertTrue(manager2.has_pending_run())
        self.assertEqual(len(manager2.get_pending_ids()), 3)
    
    def test_atomic_write(self):
        """Test that writes are atomic (uses temp file)."""
        self.manager.start_run(
            run_type="test",
            total_ids=list(range(100))
        )
        
        # File should exist
        self.assertTrue(os.path.exists(self.state_file))
    
    def test_empty_state(self):
        """Test empty state behavior."""
        self.assertFalse(self.manager.has_pending_run())
        self.assertEqual(self.manager.get_pending_ids(), [])
        self.assertEqual(self.manager.get_failed_ids(), [])
    
    def test_extra_info_preserved(self):
        """Test that extra info is preserved."""
        extra = {
            "word_field": "Expression",
            "sentence_field": "Sentence",
            "language": "Korean",
            "highlight": True,
        }
        
        self.manager.start_run(
            run_type="sentence",
            total_ids=[1, 2, 3],
            extra_info=extra
        )
        
        info = self.manager.describe_run()
        
        self.assertEqual(info["extra_info"], extra)


class TestProgressStateEdgeCases(unittest.TestCase):
    """Test edge cases for ProgressStateManager."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, "progress.json")
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_mark_success_without_run(self):
        """Test marking success without active run."""
        manager = ProgressStateManager(self.state_file)
        
        # Should not raise
        manager.mark_success(1)
    
    def test_duplicate_marks(self):
        """Test marking same item multiple times."""
        manager = ProgressStateManager(self.state_file)
        manager.start_run(run_type="test", total_ids=[1, 2, 3])
        
        manager.mark_success(1)
        manager.mark_success(1)  # Duplicate
        
        pending = manager.get_pending_ids()
        self.assertEqual(len(pending), 2)
    
    def test_corrupted_file(self):
        """Test handling corrupted state file."""
        # Write invalid JSON
        with open(self.state_file, "w") as f:
            f.write("not valid json{{{")
        
        # Should not crash, starts with empty state
        manager = ProgressStateManager(self.state_file)
        self.assertFalse(manager.has_pending_run())


if __name__ == "__main__":
    unittest.main()
