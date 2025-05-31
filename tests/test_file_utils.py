"""
Test script for file_utils.py

This script tests the file utility functions in file_utils.py.
"""

import sys
import os
import unittest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.utilities.file_utils import (
    ensure_directory_exists,
    safe_read_file,
    safe_write_file,
    load_json,
    save_json,
    load_yaml,
    save_yaml,
    load_pickle,
    save_pickle,
    find_files,
    get_file_size,
    get_file_extension
)

class TestFileUtils(unittest.TestCase):
    """Test cases for file_utils.py functions."""
    
    @patch('modules.utilities.file_utils.Path')
    def test_ensure_directory_exists(self, mock_path):
        """Test ensure_directory_exists function."""
        # Setup mock
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        
        # Test with string path
        result = ensure_directory_exists("test/dir")
        mock_path.assert_called_with("test/dir")
        mock_path_instance.mkdir.assert_called_with(parents=True, exist_ok=True)
        self.assertEqual(result, mock_path_instance)
        
        # Test with Path object
        mock_path.reset_mock()
        path_obj = Path("test/dir")
        result = ensure_directory_exists(path_obj)
        mock_path.assert_not_called()  # Should not convert Path to Path
        self.assertEqual(result, path_obj)
    
    @patch('modules.utilities.file_utils.Path')
    @patch('builtins.open', new_callable=mock_open, read_data="file content")
    def test_safe_read_file(self, mock_file, mock_path):
        """Test safe_read_file function."""
        # Setup mock
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        
        # Test with existing file
        mock_path_instance.exists.return_value = True
        result = safe_read_file("test.txt")
        self.assertEqual(result, "file content")
        mock_file.assert_called_with(mock_path_instance, 'r')
        
        # Test with non-existing file
        mock_path_instance.exists.return_value = False
        result = safe_read_file("missing.txt", default="default content")
        self.assertEqual(result, "default content")
        
        # Test with exception
        mock_path_instance.exists.return_value = True
        mock_file.side_effect = Exception("Read error")
        result = safe_read_file("error.txt", default="error default")
        self.assertEqual(result, "error default")
    
    @patch('modules.utilities.file_utils.Path')
    @patch('builtins.open', new_callable=mock_open)
    def test_safe_write_file(self, mock_file, mock_path):
        """Test safe_write_file function."""
        # Setup mock
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_parent = MagicMock()
        mock_path_instance.parent = mock_parent
        
        # Test successful write
        result = safe_write_file("test.txt", "content to write")
        self.assertTrue(result)
        mock_parent.mkdir.assert_called_with(parents=True, exist_ok=True)
        mock_file.assert_called_with(mock_path_instance, 'w')
        mock_file().write.assert_called_with("content to write")
        
        # Test with create_dirs=False
        mock_parent.reset_mock()
        result = safe_write_file("test.txt", "content", create_dirs=False)
        self.assertTrue(result)
        mock_parent.mkdir.assert_not_called()
        
        # Test with exception
        mock_file.side_effect = Exception("Write error")
        result = safe_write_file("error.txt", "content")
        self.assertFalse(result)
    
    @patch('modules.utilities.file_utils.Path')
    @patch('modules.utilities.file_utils.json')
    @patch('builtins.open', new_callable=mock_open, read_data='{"key": "value"}')
    def test_load_json(self, mock_file, mock_json, mock_path):
        """Test load_json function."""
        # Setup mock
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_json.load.return_value = {"key": "value"}
        
        # Test with existing file
        mock_path_instance.exists.return_value = True
        result = load_json("test.json")
        self.assertEqual(result, {"key": "value"})
        mock_file.assert_called_with(mock_path_instance, 'r')
        mock_json.load.assert_called_with(mock_file())
        
        # Test with non-existing file
        mock_path_instance.exists.return_value = False
        result = load_json("missing.json", default={"default": "value"})
        self.assertEqual(result, {"default": "value"})
        
        # Test with exception
        mock_path_instance.exists.return_value = True
        mock_json.load.side_effect = Exception("JSON error")
        result = load_json("error.json", default={"error": "value"})
        self.assertEqual(result, {"error": "value"})
    
    @patch('modules.utilities.file_utils.Path')
    @patch('modules.utilities.file_utils.json')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_json(self, mock_file, mock_json, mock_path):
        """Test save_json function."""
        # Setup mock
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_parent = MagicMock()
        mock_path_instance.parent = mock_parent
        
        # Test successful save
        data = {"key": "value"}
        result = save_json("test.json", data)
        self.assertTrue(result)
        mock_parent.mkdir.assert_called_with(parents=True, exist_ok=True)
        mock_file.assert_called_with(mock_path_instance, 'w')
        mock_json.dump.assert_called_with(data, mock_file(), indent=2)
        
        # Test with create_dirs=False
        mock_parent.reset_mock()
        result = save_json("test.json", data, create_dirs=False)
        self.assertTrue(result)
        mock_parent.mkdir.assert_not_called()
        
        # Test with exception
        mock_json.dump.side_effect = Exception("JSON error")
        result = save_json("error.json", data)
        self.assertFalse(result)
    
    @patch('modules.utilities.file_utils.Path')
    @patch('modules.utilities.file_utils.yaml')
    @patch('builtins.open', new_callable=mock_open, read_data='key: value')
    def test_load_yaml(self, mock_file, mock_yaml, mock_path):
        """Test load_yaml function."""
        # Setup mock
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_yaml.safe_load.return_value = {"key": "value"}
        
        # Test with existing file
        mock_path_instance.exists.return_value = True
        result = load_yaml("test.yaml")
        self.assertEqual(result, {"key": "value"})
        mock_file.assert_called_with(mock_path_instance, 'r')
        mock_yaml.safe_load.assert_called_with(mock_file())
        
        # Test with non-existing file
        mock_path_instance.exists.return_value = False
        result = load_yaml("missing.yaml", default={"default": "value"})
        self.assertEqual(result, {"default": "value"})
        
        # Test with exception
        mock_path_instance.exists.return_value = True
        mock_yaml.safe_load.side_effect = Exception("YAML error")
        result = load_yaml("error.yaml", default={"error": "value"})
        self.assertEqual(result, {"error": "value"})
    
    @patch('modules.utilities.file_utils.Path')
    @patch('modules.utilities.file_utils.yaml')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_yaml(self, mock_file, mock_yaml, mock_path):
        """Test save_yaml function."""
        # Setup mock
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_parent = MagicMock()
        mock_path_instance.parent = mock_parent
        
        # Test successful save
        data = {"key": "value"}
        result = save_yaml("test.yaml", data)
        self.assertTrue(result)
        mock_parent.mkdir.assert_called_with(parents=True, exist_ok=True)
        mock_file.assert_called_with(mock_path_instance, 'w')
        mock_yaml.dump.assert_called_with(data, mock_file(), default_flow_style=False)
        
        # Test with create_dirs=False
        mock_parent.reset_mock()
        result = save_yaml("test.yaml", data, create_dirs=False)
        self.assertTrue(result)
        mock_parent.mkdir.assert_not_called()
        
        # Test with exception
        mock_yaml.dump.side_effect = Exception("YAML error")
        result = save_yaml("error.yaml", data)
        self.assertFalse(result)
    
    @patch('modules.utilities.file_utils.Path')
    @patch('modules.utilities.file_utils.pickle')
    @patch('builtins.open', new_callable=mock_open, read_data=b'pickled data')
    def test_load_pickle(self, mock_file, mock_pickle, mock_path):
        """Test load_pickle function."""
        # Setup mock
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_pickle.load.return_value = {"key": "value"}
        
        # Test with existing file
        mock_path_instance.exists.return_value = True
        result = load_pickle("test.pkl")
        self.assertEqual(result, {"key": "value"})
        mock_file.assert_called_with(mock_path_instance, 'rb')
        mock_pickle.load.assert_called_with(mock_file())
        
        # Test with non-existing file
        mock_path_instance.exists.return_value = False
        result = load_pickle("missing.pkl", default={"default": "value"})
        self.assertEqual(result, {"default": "value"})
        
        # Test with exception
        mock_path_instance.exists.return_value = True
        mock_pickle.load.side_effect = Exception("Pickle error")
        result = load_pickle("error.pkl", default={"error": "value"})
        self.assertEqual(result, {"error": "value"})
    
    @patch('modules.utilities.file_utils.Path')
    @patch('modules.utilities.file_utils.pickle')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_pickle(self, mock_file, mock_pickle, mock_path):
        """Test save_pickle function."""
        # Setup mock
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_parent = MagicMock()
        mock_path_instance.parent = mock_parent
        
        # Test successful save
        data = {"key": "value"}
        result = save_pickle("test.pkl", data)
        self.assertTrue(result)
        mock_parent.mkdir.assert_called_with(parents=True, exist_ok=True)
        mock_file.assert_called_with(mock_path_instance, 'wb')
        mock_pickle.dump.assert_called_with(data, mock_file())
        
        # Test with create_dirs=False
        mock_parent.reset_mock()
        result = save_pickle("test.pkl", data, create_dirs=False)
        self.assertTrue(result)
        mock_parent.mkdir.assert_not_called()
        
        # Test with exception
        mock_pickle.dump.side_effect = Exception("Pickle error")
        result = save_pickle("error.pkl", data)
        self.assertFalse(result)
    
    @patch('modules.utilities.file_utils.Path')
    def test_find_files(self, mock_path):
        """Test find_files function."""
        # Setup mock
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_path_instance.glob.return_value = [Path("file1.txt"), Path("file2.txt")]
        
        # Test with recursive=True
        result = find_files("test/dir", "*.txt")
        self.assertEqual(result, [Path("file1.txt"), Path("file2.txt")])
        mock_path_instance.glob.assert_called_with("**/*.txt")
        
        # Test with recursive=False
        result = find_files("test/dir", "*.txt", recursive=False)
        self.assertEqual(result, [Path("file1.txt"), Path("file2.txt")])
        mock_path_instance.glob.assert_called_with("*.txt")
    
    @patch('modules.utilities.file_utils.Path')
    def test_get_file_size(self, mock_path):
        """Test get_file_size function."""
        # Setup mock
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_stat = MagicMock()
        mock_stat.st_size = 1024
        mock_path_instance.stat.return_value = mock_stat
        
        # Test with existing file
        mock_path_instance.exists.return_value = True
        mock_path_instance.is_file.return_value = True
        result = get_file_size("test.txt")
        self.assertEqual(result, 1024)
        
        # Test with non-existing file
        mock_path_instance.exists.return_value = False
        result = get_file_size("missing.txt")
        self.assertEqual(result, 0)
        
        # Test with directory
        mock_path_instance.exists.return_value = True
        mock_path_instance.is_file.return_value = False
        result = get_file_size("dir")
        self.assertEqual(result, 0)
        
        # Test with exception
        mock_path_instance.exists.return_value = True
        mock_path_instance.is_file.return_value = True
        mock_path_instance.stat.side_effect = Exception("Stat error")
        result = get_file_size("error.txt")
        self.assertEqual(result, 0)
    
    @patch('modules.utilities.file_utils.Path')
    def test_get_file_extension(self, mock_path):
        """Test get_file_extension function."""
        # Setup mock
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        
        # Test with extension
        mock_path_instance.suffix = ".txt"
        result = get_file_extension("test.txt")
        self.assertEqual(result, "txt")
        
        # Test without extension
        mock_path_instance.suffix = ""
        result = get_file_extension("test")
        self.assertEqual(result, "")

if __name__ == "__main__":
    unittest.main()