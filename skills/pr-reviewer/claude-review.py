#!/usr/bin/env python3
"""
Claude PR Reviewer - Analyzes PRs and generates structured review comments

Usage:
    claude-review --pr https://github.com/owner/repo/pull/123
    claude-review --pr owner/repo/123
    claude-review --diff changes.diff  # Review from local diff file
"""

import argparse
import os
import sys
import subprocess
import json
from pathlib import Path

def get_pr_diff(pr_url: str) -> str:
    """Fetch PR diff using gh CLI."""
    # Parse PR URL
    parts = pr_url.replace('https://github.com/', '').split('/')
    if len(parts) >= 3 and 'pull' in parts:
        owner, repo = parts[0], parts[1]
        pr_num = parts[3] if len(parts) > 3 else parts[2]
    elif '/' in pr_url:
        owner, repo, pr_num = pr_url.split('/')[-3:]
    else:
        raise ValueError(f"Invalid PR URL: {pr_url}")

    # Fetch diff
    result = subprocess.run(
        ['gh', 'api', f'repos/{owner}/{repo}/pulls/{pr_num}', '--jq', '.diff_url'],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"Failed to fetch PR: {result.stderr}")

    # Fetch actual diff
    diff_url = result.stdout.strip()
    result = subprocess.run(
        ['curl', '-sL', diff_url],
        capture_output=True, text=True
    )

    return result.stdout

def get_pr_info(pr_url: str) -> dict:
    """Get PR metadata using gh CLI."""
    parts = pr_url.replace('https://github.com/', '').split('/')
    owner, repo = parts[0], parts[1]
    pr_num = parts[3] if len(parts) > 3 else parts[2]

    result = subprocess.run(
        ['gh', 'api', f'repos/{owner}/{repo}/pulls/{pr_num}',
         '--jq', '{title: .title, author: .user.login, files: .changed_files, additions: .additions, deletions: .deletions}'],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        return {"title": "Unknown", "author": "Unknown", "files": 0}

    return json.loads(result.stdout)

def analyze_with_claude(diff: str, pr_info: dict) -> str:
    """Send diff to Claude for analysis."""
    prompt = f"""Analyze this PR diff and provide a structured code review.

PR Title: {pr_info.get('title', 'Unknown')}
Author: {pr_info.get('author', 'Unknown')}
Files Changed: {pr_info.get('files', 0)}
Additions: +{pr_info.get('additions', 0)}
Deletions: -{pr_info.get('deletions', 0)}

Diff:
```
{diff[:50000]}  # Truncate to avoid token limits
```

Respond with EXACTLY this Markdown format:

## Summary
[2-3 sentences summarizing the changes]

## Identified Risks
- [Risk 1]
- [Risk 2]
- [Risk N or "None identified"]

## Improvement Suggestions
- [Suggestion 1]
- [Suggestion 2]
- [Suggestion N]

## Confidence Score
**[Low/Medium/High]** — [Brief explanation]
"""

    # Check for Claude CLI
    result = subprocess.run(
        ['claude', '--print', prompt],
        capture_output=True, text=True, env={**os.environ, 'NO_COLOR': '1'}
    )

    if result.returncode != 0:
        # Fallback: Use local model or echo
        return generate_review_locally(diff, pr_info)

    return result.stdout

def generate_review_locally(diff: str, pr_info: dict) -> str:
    """Generate a structured review without Claude CLI."""
    # Analyze diff patterns
    risks = []
    suggestions = []

    # Check for common issues
    if 'TODO' in diff:
        risks.append("Contains TODO comments that should be resolved")
    if 'console.log' in diff:
        risks.append("Contains console.log statements (may want to remove)")
    if 'password' in diff.lower() or 'secret' in diff.lower():
        risks.append("Potential sensitive data exposure")
    if '+ any' in diff or ': any' in diff:
        suggestions.append("Consider replacing `any` types with specific types")
    if 'SELECT *' in diff.upper():
        suggestions.append("Consider specifying explicit columns instead of SELECT *")

    # Basic stats
    lines_added = diff.count('\n+') - diff.count('\n++')
    lines_removed = diff.count('\n-') - diff.count('\n--')

    confidence = "Medium"
    if len(risks) == 0 and len(suggestions) == 0:
        confidence = "High"
    elif len(risks) > 2:
        confidence = "Low"

    return f"""## Summary
This PR by {pr_info.get('author', 'Unknown')} modifies {pr_info.get('files', 0)} files with +{pr_info.get('additions', lines_added)} additions and -{pr_info.get('deletions', lines_removed)} deletions. {pr_info.get('title', 'Various changes')}.

## Identified Risks
{chr(10).join(f'- {r}' for r in risks) if risks else '- None identified'}

## Improvement Suggestions
{chr(10).join(f'- {s}' for s in suggestions) if suggestions else '- Code looks good as is'}

## Confidence Score
**{confidence}** — Based on pattern analysis without Claude API access.
"""

def main():
    parser = argparse.ArgumentParser(description='Claude PR Reviewer')
    parser.add_argument('--pr', required=True, help='PR URL or owner/repo/123')
    parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    args = parser.parse_args()

    print(f"Fetching PR: {args.pr}", file=sys.stderr)

    try:
        diff = get_pr_diff(args.pr)
        pr_info = get_pr_info(args.pr)

        print(f"Analyzing {pr_info.get('files', 0)} files...", file=sys.stderr)

        review = analyze_with_claude(diff, pr_info)

        if args.output:
            Path(args.output).write_text(review)
            print(f"Review written to {args.output}", file=sys.stderr)
        else:
            print(review)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()