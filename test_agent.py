#!/usr/bin/env python3
"""Test script for claude_review.py"""

import json
import subprocess
import sys

def test_format_review():
    """Test the review formatting function."""
    from claude_review import format_review
    
    review = {
        "summary": "This PR adds user authentication with JWT tokens.",
        "risks": [
            "Missing rate limiting on login endpoint",
            "JWT secret hardcoded"
        ],
        "suggestions": [
            "Add rate limiting middleware",
            "Use environment variable for JWT secret"
        ],
        "confidence": "Medium"
    }
    
    markdown = format_review(review)
    
    # Check expected sections
    assert "## 🤖 Claude Code Review" in markdown
    assert "### Summary" in markdown
    assert "### ⚠️ Risks" in markdown
    assert "### 💡 Suggestions" in markdown
    assert "### Confidence: 🟡 Medium" in markdown
    assert "rate limiting" in markdown
    
    print("✅ format_review test passed")
    return True

def test_diff_from_file():
    """Test reading diff from file."""
    from claude_review import get_diff_from_file
    
    # Create a test diff file
    test_diff = """diff --git a/test.py b/test.py
new file mode 100644
index 0000000..1234567
--- /dev/null
+++ b/test.py
@@ -0,0 +1,3 @@
+def hello():
+    print("Hello, World!")
+"""
    
    with open('/tmp/test.diff', 'w') as f:
        f.write(test_diff)
    
    result = get_diff_from_file('/tmp/test.diff')
    assert 'def hello()' in result
    assert 'print("Hello, World!")' in result
    
    print("✅ get_diff_from_file test passed")
    return True

def test_analyze_structure():
    """Test that analyze_with_claude returns expected structure."""
    from claude_review import analyze_with_claude
    
    # Test with empty diff (will fail API call, but tests structure)
    result = analyze_with_claude("")
    
    # Should have required keys
    assert 'summary' in result
    assert 'risks' in result
    assert 'suggestions' in result
    assert 'confidence' in result
    
    print("✅ analyze_with_claude structure test passed")
    return True

def main():
    print("Testing claude_review.py...\n")
    
    all_passed = True
    
    try:
        if not test_format_review():
            all_passed = False
    except Exception as e:
        print(f"❌ format_review test failed: {e}")
        all_passed = False
    
    try:
        if not test_diff_from_file():
            all_passed = False
    except Exception as e:
        print(f"❌ get_diff_from_file test failed: {e}")
        all_passed = False
    
    try:
        if not test_analyze_structure():
            all_passed = False
    except Exception as e:
        print(f"❌ analyze_with_claude test failed: {e}")
        all_passed = False
    
    if all_passed:
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())