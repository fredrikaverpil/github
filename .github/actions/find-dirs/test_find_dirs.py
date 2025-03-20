import unittest
import tempfile
import os
import shutil
from find_dirs import find_directories

class TestFindDirectories(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory structure for testing
        self.test_dir = tempfile.mkdtemp()
        
        # Create test directory structure
        os.makedirs(os.path.join(self.test_dir, "tools"))
        os.makedirs(os.path.join(self.test_dir, "src/tools"))
        os.makedirs(os.path.join(self.test_dir, "src/pkg/tools"))
        os.makedirs(os.path.join(self.test_dir, "pkg"))
        
        # Create test files
        with open(os.path.join(self.test_dir, "go.mod"), "w") as f:
            f.write("module root")
        with open(os.path.join(self.test_dir, "tools/go.mod"), "w") as f:
            f.write("module tools")
        with open(os.path.join(self.test_dir, "pkg/go.mod"), "w") as f:
            f.write("module pkg")
        with open(os.path.join(self.test_dir, "src/tools/go.mod"), "w") as f:
            f.write("module src/tools")
        
        # Save the original working directory
        self.original_dir = os.getcwd()
        
        # Change to the test directory
        os.chdir(self.test_dir)
    
    def tearDown(self):
        # Return to the original directory
        os.chdir(self.original_dir)
        
        # Clean up the test directory
        shutil.rmtree(self.test_dir)
    
    def test_find_all_directories(self):
        # No exclusions
        dirs = find_directories(["go.mod"])
        self.assertEqual(sorted(dirs), sorted([".", "pkg", "src/tools", "tools"]))
    
    def test_exclude_root_tools(self):
        # Exclude only the root tools directory
        dirs = find_directories(["go.mod"], ["/tools"])
        self.assertEqual(sorted(dirs), sorted([".", "pkg", "src/tools"]))
    
    def test_exclude_all_tools(self):
        # Exclude all directories named tools
        dirs = find_directories(["go.mod"], ["tools"])
        self.assertEqual(sorted(dirs), sorted([".", "pkg"]))
    
    def test_exclude_nested_tools(self):
        # Exclude tools directories under src
        dirs = find_directories(["go.mod"], ["src/*/go.mod"])
        self.assertEqual(sorted(dirs), sorted([".", "pkg", "tools"]))
    
    def test_multiple_patterns(self):
        # Test with multiple file patterns
        with open(os.path.join(self.test_dir, "src/pkg/pyproject.toml"), "w") as f:
            f.write("[tool.poetry]")
        
        dirs = find_directories(["go.mod", "pyproject.toml"])
        self.assertEqual(sorted(dirs), sorted([".", "pkg", "src/pkg", "src/tools", "tools"]))

if __name__ == "__main__":
    unittest.main()
