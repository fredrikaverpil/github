#!/bin/bash
# Script to detect project types for workflow syncing

# Initialize variables
TYPES=()
FEATURES=()

# Detect Go projects
if [ -f "go.mod" ]; then
	TYPES+=("go")

	# Check for specific Go project features
	if grep -q "github.com/gin-gonic/gin" go.mod; then
		FEATURES+=("gin")
	fi

	if grep -q "github.com/stretchr/testify" go.mod; then
		FEATURES+=("testify")
	fi
fi

# Detect Python projects
if [ -f "pyproject.toml" ] || [ -f "setup.py" ] || [ -f "requirements.txt" ]; then
	TYPES+=("python")

	# Check for specific Python project features
	if [ -f "pyproject.toml" ] && grep -q "fastapi" pyproject.toml; then
		FEATURES+=("fastapi")
	fi

	if [ -f "pytest.ini" ] || grep -q "pytest" pyproject.toml 2>/dev/null; then
		FEATURES+=("pytest")
	fi
fi

# Detect Lua projects
if ls *.lua 1>/dev/null 2>&1 || [ -f ".luacheckrc" ]; then
	TYPES+=("lua")
fi

# Output types as comma-separated list
if [ ${#TYPES[@]} -gt 0 ]; then
	echo "types=$(
		IFS=,
		echo "${TYPES[*]}"
	)" >>$GITHUB_OUTPUT
else
	echo "types=unknown" >>$GITHUB_OUTPUT
fi

# Output features as comma-separated list
if [ ${#FEATURES[@]} -gt 0 ]; then
	echo "features=$(
		IFS=,
		echo "${FEATURES[*]}"
	)" >>$GITHUB_OUTPUT
else
	echo "features=none" >>$GITHUB_OUTPUT
fi

# Always include common workflows
echo "has_common=true" >>$GITHUB_OUTPUT
