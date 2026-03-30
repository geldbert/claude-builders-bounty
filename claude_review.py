#!/usr/bin/env python3
"""
Claude PR Review Agent
Analyzes a GitHub PR diff and generates a structured review comment.

Installation:
  pip install anthropic

Usage:
  export ANTHROPIC_API_KEY=your_key
  claude-review --pr https://github.com/owner/repo/pull/123
  claude-review --diff ./changes.diff
"""

import argparse
import os
import subprocess
import sys
import json
from typing import Optional

def get_pr_diff(pr_url: str) -> str:
    """Fetch PR diff using gh CLI."""
    result = subprocess.run(
        ['gh', 'pr', 'diff', pr_url],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise Exception(f"Failed to fetch PR diff: {result.stderr}")
    return result.stdout

def get_diff_from_file(filepath: str) -> str:
    """Read diff from file."""
    with open(filepath, 'r') as f:
        return f.read()

def analyze_with_claude(diff: str) -> dict:
    """
    Use Claude to analyze the PR diff.
    Returns structured review data.
    """
    try:
        import anthropic
    except ImportError:
        return {
            "error": "anthropic package not installed. Run: pip install anthropic",
            "summary": "Unable to analyze - missing dependency",
            "risks": [],
            "suggestions": [],
            "confidence": "Low"
        }
    
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        return {
            "error": "ANTHROPIC_API_KEY not set",
            "summary": "Unable to analyze - missing API key",
            "risks": [],
            "suggestions": [],
            "confidence": "Low"
        }
    
    client = anthropic.Anthropic(api_key=api_key)
    
    prompt = f"""Analyze this GitHub PR diff and provide a structured code review.

<diff>
{diff[:50000]}  <!-- Truncate to avoid token limits -->
</diff>

Respond in JSON format with these fields:
{{
  "summary": "2-3 sentence summary of changes",
  "risks": ["list of identified risks or concerns"],
  "suggestions": ["list of improvement suggestions"],
  "confidence": "Low|Medium|High"
}}

Focus on:
- Security vulnerabilities
- Performance issues
- Code quality and maintainability
- Potential bugs or edge cases
- Missing error handling"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse JSON from response
        response_text = message.content[0].text
        
        # Extract JSON if wrapped in markdown
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0]
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0]
        
        return json.loads(response_text.strip())
    
    except json.JSONDecodeError:
        # Fallback: return raw response as summary
        return {
            "summary": message.content[0].text[:500],
            "risks": ["Unable to parse structured response"],
            "suggestions": [],
            "confidence": "Low"
        }
    except Exception as e:
        return {
            "error": str(e),
            "summary": "Analysis failed",
            "risks": [],
            "suggestions": [],
            "confidence": "Low"
        }

def format_review(review: dict) -> str:
    """Format review as Markdown."""
    md = "## 🤖 Claude Code Review\n\n"
    
    md += "### Summary\n"
    md += f"{review.get('summary', 'No summary available')}\n\n"
    
    risks = review.get('risks', [])
    if risks:
        md += "### ⚠️ Risks\n"
        for risk in risks:
            md += f"- {risk}\n"
        md += "\n"
    
    suggestions = review.get('suggestions', [])
    if suggestions:
        md += "### 💡 Suggestions\n"
        for suggestion in suggestions:
            md += f"- {suggestion}\n"
        md += "\n"
    
    confidence = review.get('confidence', 'Low')
    confidence_emoji = {'Low': '🔴', 'Medium': '🟡', 'High': '🟢'}.get(confidence, '⚪')
    md += f"### Confidence: {confidence_emoji} {confidence}\n"
    
    if 'error' in review:
        md += f"\n*Error: {review['error']}*\n"
    
    return md

def main():
    parser = argparse.ArgumentParser(description='Claude PR Review Agent')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--pr', help='GitHub PR URL')
    group.add_argument('--diff', help='Path to diff file')
    parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    
    args = parser.parse_args()
    
    # Get diff
    if args.pr:
        print(f"Fetching PR diff from {args.pr}...", file=sys.stderr)
        diff = get_pr_diff(args.pr)
    else:
        print(f"Reading diff from {args.diff}...", file=sys.stderr)
        diff = get_diff_from_file(args.diff)
    
    # Analyze
    print("Analyzing with Claude...", file=sys.stderr)
    review = analyze_with_claude(diff)
    
    # Format output
    markdown = format_review(review)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(markdown)
        print(f"Review written to {args.output}", file=sys.stderr)
    else:
        print(markdown)

if __name__ == '__main__':
    main()