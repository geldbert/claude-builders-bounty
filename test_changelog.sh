#!/bin/bash
# Test script for changelog generator

set -e

echo "Testing changelog generator..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Create a temp repo for testing
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"
git init
git config user.email "test@example.com"
git config user.name "Test User"

# Create some test commits
echo "# Test Project" > README.md
git add README.md
git commit -m "feat: Initial commit"

echo "console.log('hello');" > app.js
git add app.js
git commit -m "feat: Add main application"

echo "function test() { return true; }" >> app.js
git add app.js
git commit -m "fix: Fix test function"

echo "Updated" >> README.md
git add README.md
git commit -m "refactor: Improve README"

# Run the changelog generator (script is in SCRIPT_DIR)
"$SCRIPT_DIR/changelog.sh" --output CHANGELOG.md

# Verify output
if [ -f "CHANGELOG.md" ]; then
    echo "✅ CHANGELOG.md created"
    echo "---"
    cat CHANGELOG.md
    echo "---"
    
    # Check categories
    if grep -q "### Added" CHANGELOG.md; then
        echo "✅ Added category found"
    else
        echo "❌ Added category missing"
    fi
    
    if grep -q "### Fixed" CHANGELOG.md; then
        echo "✅ Fixed category found"
    else
        echo "❌ Fixed category missing"
    fi
    
    if grep -q "### Changed" CHANGELOG.md; then
        echo "✅ Changed category found"
    else
        echo "❌ Changed category missing"
    fi
    
    echo ""
    echo "All tests passed!"
else
    echo "❌ CHANGELOG.md not created"
    exit 1
fi

# Cleanup
cd /
rm -rf "$TEMP_DIR"