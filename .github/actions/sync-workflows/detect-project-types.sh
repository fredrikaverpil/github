#!/bin/bash
# Script to detect project types for workflow syncing

# Initialize variables
TYPES=""

# Detect Go projects
if [ -f "go.mod" ]; then
	TYPES="${TYPES}go,"
fi

# Detect Python projects
if [ -f "pyproject.toml" ] || [ -f "setup.py" ] || [ -f "requirements.txt" ]; then
	TYPES="${TYPES}python,"
fi

# Detect Lua projects
if ls *.lua 1>/dev/null 2>&1 || [ -f ".luacheckrc" ]; then
	TYPES="${TYPES}lua,"
fi

# Remove trailing comma
TYPES=${TYPES%,}

# If no types detected, set to "unknown"
if [ -z "$TYPES" ]; then
	TYPES="unknown"
fi

# Set features (placeholder for future expansion)
FEATURES="none"

# Output detection results
if [ -n "$GITHUB_OUTPUT" ]; then
	# We're running in GitHub Actions
	echo "types=$TYPES" >>$GITHUB_OUTPUT
	echo "features=$FEATURES" >>$GITHUB_OUTPUT
else
	# We're running locally
	echo "Detected project types: $TYPES"
	echo "Detected features: $FEATURES"
fi
