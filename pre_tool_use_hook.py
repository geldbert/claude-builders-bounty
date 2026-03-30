#!/usr/bin/env python3
"""
PreToolUse Hook for Claude Code
Blocks destructive bash commands before execution.

Installation:
  cp pre_tool_use_hook.py ~/.claude/hooks/
  chmod +x ~/.claude/hooks/pre_tool_use_hook.py

Log file: ~/.claude/hooks/blocked.log
"""

import sys
import os
import re
import json
from datetime import datetime
from pathlib import Path

# Dangerous patterns to block
BLOCKED_PATTERNS = [
    # Filesystem destruction
    (r'rm\s+-rf\s+/', 'rm -rf / would delete entire filesystem'),
    (r'rm\s+-rf\s+~', 'rm -rf ~ would delete home directory'),
    (r'rm\s+-rf\s+\*', 'rm -rf * would delete everything in current directory'),
    (r'rm\s+-rf\s+\.\.', 'rm -rf .. would delete parent directory'),
    (r'rm\s+-rf\s+/', 'rm -rf with absolute path is dangerous'),
    
    # Database destruction
    (r'\bDROP\s+TABLE\b', 'DROP TABLE would delete database table'),
    (r'\bDROP\s+DATABASE\b', 'DROP DATABASE would delete entire database'),
    (r'\bDROP\s+SCHEMA\b', 'DROP SCHEMA would delete database schema'),
    (r'\bTRUNCATE\s+TABLE?\b', 'TRUNCATE would delete all rows'),
    (r'\bDELETE\s+FROM\b(?!\s*\w+\s+WHERE)', 'DELETE FROM without WHERE would delete all rows'),
    
    # Git destruction
    (r'git\s+push\s+--force', 'git push --force could overwrite remote history'),
    (r'git\s+push\s+-f\b', 'git push -f could overwrite remote history'),
    (r'git\s+reset\s+--hard\s+HEAD~', 'git reset --hard HEAD~ would lose commits'),
    (r'git\s+clean\s+-fdx', 'git clean -fdx would remove all untracked files'),
    
    # System destruction
    (r'\bsudo\s+rm\s+-rf', 'sudo rm -rf is extremely dangerous'),
    (r'\bdd\s+if=.*of=/dev/', 'dd to /dev/ would overwrite device'),
    (r'>\s*/dev/sd[a-z]', 'Writing directly to disk device'),
    (r'\bmkfs\.', 'mkfs would format a disk'),
    
    # Credential/secret exposure
    (r'cat\s+.*\.pem\b', 'Reading .pem files could expose private keys'),
    (r'cat\s+.*id_rsa\b', 'Reading id_rsa would expose SSH private key'),
    (r'cat\s+.*\.key\b', 'Reading .key files could expose secrets'),
]

def log_blocked(command: str, reason: str, project_path: str):
    """Log blocked attempt to file."""
    log_dir = Path.home() / '.claude' / 'hooks'
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'blocked.log'
    
    timestamp = datetime.now().isoformat()
    log_entry = f"[{timestamp}] BLOCKED: {command}\n  Reason: {reason}\n  Project: {project_path}\n\n"
    
    with open(log_file, 'a') as f:
        f.write(log_entry)

def check_command(command: str) -> tuple[bool, str]:
    """
    Check if command contains dangerous patterns.
    Returns (is_blocked, reason).
    """
    # Extract bash command if wrapped in JSON
    if command.strip().startswith('{'):
        try:
            data = json.loads(command)
            if 'command' in data:
                command = data['command']
        except json.JSONDecodeError:
            pass
    
    for pattern, reason in BLOCKED_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return True, reason
    
    return False, ''

def main():
    # Read input from stdin (Claude Code sends JSON)
    try:
        input_data = sys.stdin.read()
        if not input_data:
            sys.exit(0)  # No input, allow
        
        data = json.loads(input_data)
    except json.JSONDecodeError:
        sys.exit(0)  # Invalid JSON, allow
    
    # Extract command from tool use
    command = ''
    project_path = data.get('project_path', 'unknown')
    
    if 'tool' in data:
        tool = data['tool']
        if tool.get('name') == 'bash':
            command = tool.get('input', {}).get('command', '')
        elif 'input' in tool and isinstance(tool['input'], dict):
            command = tool['input'].get('command', '')
    
    if not command:
        sys.exit(0)  # No command, allow
    
    # Check command against patterns
    is_blocked, reason = check_command(command)
    
    if is_blocked:
        log_blocked(command, reason, project_path)
        
        # Output error message for Claude
        error = {
            'error': f'Command blocked by security hook: {reason}',
            'details': f'The command "{command[:100]}..." was blocked to prevent potential damage.',
            'suggestion': 'If this is intentional, you can bypass this check by running the command directly in your terminal.'
        }
        print(json.dumps(error), file=sys.stderr)
        sys.exit(1)  # Block the command
    
    sys.exit(0)  # Allow the command

if __name__ == '__main__':
    main()