#!/bin/bash
# CHANGELOG Generator
# Generates a structured CHANGELOG.md from git history
# Usage: ./changelog.sh [--since-tag TAG] [--output FILE]

set -e

OUTPUT_FILE="CHANGELOG.md"
SINCE_TAG=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --since-tag)
            SINCE_TAG="$2"
            shift 2
            ;;
        --output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

# Change to git repo directory if output path is specified
if [[ "$OUTPUT_FILE" == */* ]]; then
    REPO_DIR=$(dirname "$OUTPUT_FILE")
    OUTPUT_FILE=$(basename "$OUTPUT_FILE")
    cd "$REPO_DIR" 2>/dev/null || true
fi

# Find the last tag if not specified
if [ -z "$SINCE_TAG" ]; then
    SINCE_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
fi

# Get commits since tag (or all commits if no tag)
if [ -n "$SINCE_TAG" ]; then
    COMMITS=$(git log "$SINCE_TAG"..HEAD --pretty=format:"%h|%s|%an|%ad" --date=short 2>/dev/null)
    SINCE_TEXT="since $SINCE_TAG"
else
    COMMITS=$(git log --pretty=format:"%h|%s|%an|%ad" --date=short 2>/dev/null)
    SINCE_TEXT="all commits"
fi

# Categorize commits
ADDED=""
FIXED=""
CHANGED=""
REMOVED=""
OTHER=""

while IFS='|' read -r hash subject author date; do
    [ -z "$hash" ] && continue
    
    # Categorize based on commit message prefix
    lower_subject=$(echo "$subject" | tr '[:upper:]' '[:lower:]')
    
    if [[ "$lower_subject" =~ ^(feat|feature|add|new|\+) ]]; then
        ADDED="$ADDED- $subject ($hash) [$author]\n"
    elif [[ "$lower_subject" =~ ^(fix|bug|patch|resolve|-) ]]; then
        FIXED="$FIXED- $subject ($hash) [$author]\n"
    elif [[ "$lower_subject" =~ ^(change|update|modify|refactor|improve) ]]; then
        CHANGED="$CHANGED- $subject ($hash) [$author]\n"
    elif [[ "$lower_subject" =~ ^(remove|delete|drop|deprecate) ]]; then
        REMOVED="$REMOVED- $subject ($hash) [$author]\n"
    else
        OTHER="$OTHER- $subject ($hash) [$author]\n"
    fi
done <<< "$COMMITS"

# Generate CHANGELOG
VERSION=$(git describe --tags --always 2>/dev/null || echo "unreleased")
DATE=$(date +%Y-%m-%d)

cat > "$OUTPUT_FILE" << EOF
# Changelog

## [$VERSION] - $DATE

EOF

if [ -n "$ADDED" ]; then
    echo "### Added" >> "$OUTPUT_FILE"
    echo -e "$ADDED" >> "$OUTPUT_FILE"
fi

if [ -n "$FIXED" ]; then
    echo "### Fixed" >> "$OUTPUT_FILE"
    echo -e "$FIXED" >> "$OUTPUT_FILE"
fi

if [ -n "$CHANGED" ]; then
    echo "### Changed" >> "$OUTPUT_FILE"
    echo -e "$CHANGED" >> "$OUTPUT_FILE"
fi

if [ -n "$REMOVED" ]; then
    echo "### Removed" >> "$OUTPUT_FILE"
    echo -e "$REMOVED" >> "$OUTPUT_FILE"
fi

if [ -n "$OTHER" ]; then
    echo "### Other" >> "$OUTPUT_FILE"
    echo -e "$OTHER" >> "$OUTPUT_FILE"
fi

echo "Generated $OUTPUT_FILE with changes $SINCE_TEXT"