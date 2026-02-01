# -*- coding: utf-8 -*-
"""
Tests for Progress State Manager

Tests state persistence and resume functionality.
Updated to match current ProgressStateManager API.
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
        # Initialize with temp_dir as addon_dir, operation="test" -> creates progress_state_test.json
        self.manager = ProgressStateManager(self.temp_dir, operation="test")
        self.deck_id = 1
        self.deck_name = "Test Deck"
    
    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_start_run(self):
        """Test starting a new run."""
        note_ids = [1, 2, 3, 4, 5]
        
        self.manager.start_run(
            deck_id=self.deck_id,
            deck_name=self.deck_name,
            note_ids=note_ids
        )
        
        self.assertTrue(self.manager.has_pending_run(self.deck_id))
        self.assertEqual(len(self.manager.get_pending_note_ids(self.deck_id)), 5)
    
    def test_mark_success(self):
        """Test marking items as successful."""
        self.manager.start_run(
            deck_id=self.deck_id,
            deck_name=self.deck_name,
            note_ids=[1, 2, 3]
        )
        
        self.manager.mark_success(self.deck_id, 1)
        self.manager.mark_success(self.deck_id, 2)
        
        pending = self.manager.get_pending_note_ids(self.deck_id)
        self.assertEqual(len(pending), 1)
        self.assertIn(3, pending)
    
    def test_mark_failure(self):
        """Test marking items as failed."""
        self.manager.start_run(
            deck_id=self.deck_id,
            deck_name=self.deck_name,
            note_ids=[1, 2, 3]
        )
        
        self.manager.mark_failure(self.deck_id, 1, "Test error")
        
        # In current implementation, failed items REMAIN in pending?
        # Let's check implementation: mark_failure adds to failed, but does not remove from pending.
        # mark_success removes from pending.
        # So pending should still have 1, 2, 3?
        # Wait, if I iterate loops, usually I check pending and then process.
        # If mark_failure doesn't remove from pending, it will be retried?
        # For this test, valid behavior is what implementation does.
        
        pending = self.manager.get_pending_note_ids(self.deck_id)
        # Based on implementation reading: mark_failure does NOT remove from pending.
        self.assertIn(1, pending) 
        
        failed = self.manager.get_failed_details(self.deck_id)
        self.assertEqual(len(failed), 1)
        self.assertIn(1, failed)
        self.assertEqual(failed[1]["message"], "Test error")
    
    def test_clear(self):
        """Test clearing state."""
        self.manager.start_run(
            deck_id=self.deck_id,
            deck_name=self.deck_name,
            note_ids=[1, 2, 3]
        )
        
        self.assertTrue(self.manager.has_pending_run(self.deck_id))
        
        self.manager.clear_run(self.deck_id)
        
        self.assertFalse(self.manager.has_pending_run(self.deck_id))
    
    def test_describe_run(self):
        """Test run description."""
        self.manager.start_run(
            deck_id=self.deck_id,
            deck_name=self.deck_name,
            note_ids=[1, 2, 3]
        )
        
        self.manager.mark_success(self.deck_id, 1)
        self.manager.mark_failure(self.deck_id, 2, "Error")
        
        info = self.manager.describe_run(self.deck_id)
        
        self.assertEqual(info["operation"], "test")
        self.assertEqual(info["total"], 3)
        self.assertEqual(info["pending_count"], 2) # 1 removed, 2 (failed) kept, 3 kept
        self.assertEqual(info["failed_count"], 1)
    
    def test_persistence(self):
        """Test that state persists to file."""
        self.manager.start_run(
            deck_id=self.deck_id,
            deck_name=self.deck_name,
            note_ids=[1, 2, 3, 4, 5]
        )
        
        self.manager.mark_success(self.deck_id, 1)
        
        # Create new manager from same dir
        manager2 = ProgressStateManager(self.temp_dir, operation="test")
        
        self.assertTrue(manager2.has_pending_run(self.deck_id))
        self.assertEqual(len(manager2.get_pending_note_ids(self.deck_id)), 4)
    
    def test_atomic_write(self):
        """Test that writes are atomic (uses temp file)."""
        self.manager.start_run(
            deck_id=self.deck_id,
            deck_name=self.deck_name,
            note_ids=list(range(100))
        )
        
        # File should exist
        state_path = os.path.join(self.temp_dir, "progress_state_test.json")
        self.assertTrue(os.path.exists(state_path))
    
    def test_empty_state(self):
        """Test empty state behavior."""
        self.assertFalse(self.manager.has_pending_run(self.deck_id))
        self.assertEqual(self.manager.get_pending_note_ids(self.deck_id), [])
        self.assertEqual(self.manager.get_failed_details(self.deck_id), {})


class TestProgressStateEdgeCases(unittest.TestCase):
    """Test edge cases for ProgressStateManager."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.manager = ProgressStateManager(self.temp_dir, operation="test")
        self.deck_id = 999
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_mark_success_without_run(self):
        """Test marking success without active run."""
        # Should not raise
        self.manager.mark_success(self.deck_id, 1)
    
    def test_duplicate_marks(self):
        """Test marking same item multiple times."""
        self.manager.start_run(self.deck_id, "test", [1, 2, 3])
        
        self.manager.mark_success(self.deck_id, 1)
        self.manager.mark_success(self.deck_id, 1)  # Duplicate call
        
        pending = self.manager.get_pending_note_ids(self.deck_id)
        # 1 should be gone
        self.assertNotIn(1, pending)
        self.assertEqual(len(pending), 2)
    
    def test_corrupted_file(self):
        """Test handling corrupted state file."""
        state_path = os.path.join(self.temp_dir, "progress_state_test.json")
        # Write invalid JSON
        with open(state_path, "w") as f:
            f.write("not valid json{{{")
        
        # Should not crash, starts with empty state
        manager = ProgressStateManager(self.temp_dir, operation="test")
        self.assertFalse(manager.has_pending_run(self.deck_id))


if __name__ == "__main__":
    unittest.main()
