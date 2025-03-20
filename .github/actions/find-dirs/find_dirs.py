"""
Find directories containing specific file patterns while respecting exclusion patterns.

Patterns:
  - Simple name (e.g., "tools"): Excludes all directories with that name
  - Root pattern (e.g., "/tools" or "./tools"): Excludes only root-level directory
  - Glob patterns (e.g., "**/vendor", "src/*/tools"): Uses fnmatch for glob matching
"""

import os
import json
import glob
import fnmatch
import argparse
import sys

def find_directories(file_patterns, exclude_patterns=None):
    """
    Find directories containing files matching the given patterns,
    excluding directories that match the exclude patterns.
    
    Args:
        file_patterns: List of file glob patterns to search for
        exclude_patterns: List of directory patterns to exclude
        
    Returns:
        List of directory paths
    """
    if exclude_patterns is None:
        exclude_patterns = []
        
    # Set to track unique directories
    directories = set()

    # Find all matching files
    for pattern in file_patterns:
        matching_files = glob.glob(f'**/{pattern}', recursive=True)

        # Extract directories
        for file_path in matching_files:
            # Use '.' for the root directory
            dir_path = os.path.dirname(file_path) or '.'
            directories.add(dir_path)

    # Filter directories based on exclude patterns
    filtered_directories = set()
    for dir_path in directories:
        should_keep = True
        
        for exclude_pattern in exclude_patterns:
            # Handle root directory patterns
            is_root_pattern = False
            pattern_to_match = exclude_pattern
            
            if exclude_pattern.startswith('/'):
                pattern_to_match = exclude_pattern[1:]
                is_root_pattern = True
            elif exclude_pattern.startswith('./'):
                pattern_to_match = exclude_pattern[2:]
                is_root_pattern = True
            
            # For root patterns, only match exact root directories
            if is_root_pattern:
                if dir_path == pattern_to_match:
                    should_keep = False
                    print(f"Excluding root directory {dir_path} (matched root pattern /{pattern_to_match})")
                    break
            else:
                # For non-root patterns, use fnmatch for glob-style matching
                if fnmatch.fnmatch(dir_path, pattern_to_match):
                    should_keep = False
                    print(f"Excluding directory {dir_path} (matched pattern {exclude_pattern})")
                    break
        
        if should_keep:
            filtered_directories.add(dir_path)

    # Convert to sorted list
    return sorted(list(filtered_directories))

def main():
    parser = argparse.ArgumentParser(description='Find directories containing specific files.')
    parser.add_argument('--file-patterns', required=True, 
                        help='Comma-separated list of file patterns to search for')
    parser.add_argument('--exclude-patterns', default='',
                        help='Comma-separated list of directory patterns to exclude')
    parser.add_argument('--output', default='',
                        help='Path to write the GitHub Actions output variable (optional)')
    
    args = parser.parse_args()
    
    # Process input patterns
    file_patterns = [p.strip() for p in args.file_patterns.split(',') if p.strip()]
    exclude_patterns = [p.strip() for p in args.exclude_patterns.split(',') if p.strip()]
    
    # Find directories
    dir_list = find_directories(file_patterns, exclude_patterns)
    
    # Format as JSON matrix
    matrix = json.dumps({"dir": dir_list})
    
    # Write GitHub output if requested
    if args.output:
        with open(args.output, 'a') as f:
            f.write(f"matrix={matrix}\n")
    else:
        # Print to stdout otherwise
        print(matrix)
        
    # Print debugging info to stderr
    print(f"Found directories: {dir_list}", file=sys.stderr)
    print(f"Excluded patterns: {exclude_patterns}", file=sys.stderr)
    print(f"File patterns searched: {file_patterns}", file=sys.stderr)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
