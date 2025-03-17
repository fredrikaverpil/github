#!/usr/bin/env bash
set -euo pipefail

repo_dir="${1:-.}"
template_dir="${2:-templates}"
output_file="${3:-}"

# Create array for detected types
types=()

# Detect project types
if [[ -f "${repo_dir}/go.mod" ]]; then
	types+=("go")
fi

# TODO: add python
# if [[ -f "${repo_dir}/pyproject.toml" ]] || [[ -f "${repo_dir}/uv.lock" ]] || [[ -f "${repo_dir}/requirements.txt" ]]; then
# 	types+=("python")
# fi

# Ensure workflows directory exists
mkdir -p "${repo_dir}/.github/workflows"

# Copy common templates
if [[ -d "${template_dir}/common" ]]; then
	cp "${template_dir}"/common/*.yml "${repo_dir}/.github/workflows/"
fi

# Copy project type-specific templates
for type in "${types[@]}"; do
	if [[ -f "${template_dir}/${type}.yml" ]]; then
		cp "${template_dir}/${type}.yml" "${repo_dir}/.github/workflows/"
	fi
done

# Output for GitHub Actions
if [[ -n "${output_file}" ]]; then
	echo "types=${types[*]}" >>"${output_file}"
fi
