#!/usr/bin/env python3
"""Test script for pre_tool_use_hook.py"""

import subprocess
import json
import sys

def run_hook(command_json):
    """Run the hook with given input and return exit code."""
    result = subprocess.run(
        ['python3', 'pre_tool_use_hook.py'],
        input=json.dumps(command_json),
        capture_output=True,
        text=True
    )
    return result.returncode, result.stderr

def test_blocked_commands():
    """Test that dangerous commands are blocked."""
    blocked = [
        ('rm -rf /', 'rm -rf / should be blocked'),
        ('rm -rf ~', 'rm -rf ~ should be blocked'),
        ('DROP TABLE users', 'DROP TABLE should be blocked'),
        ('TRUNCATE TABLE users', 'TRUNCATE should be blocked'),
        ('DELETE FROM users', 'DELETE FROM without WHERE should be blocked'),
        ('git push --force origin main', 'git push --force should be blocked'),
        ('sudo rm -rf /var', 'sudo rm -rf should be blocked'),
    ]
    
    for cmd, desc in blocked:
        input_data = {'tool': {'name': 'bash', 'input': {'command': cmd}}}
        code, err = run_hook(input_data)
        if code == 0:
            print(f'❌ FAILED: {desc}')
            return False
        print(f'✅ BLOCKED: {cmd}')
    
    return True

def test_allowed_commands():
    """Test that safe commands are allowed."""
    allowed = [
        ('ls -la', 'ls should be allowed'),
        ('git status', 'git status should be allowed'),
        ('npm install', 'npm install should be allowed'),
        ('cat README.md', 'cat README should be allowed'),
        ('DELETE FROM users WHERE id = 1', 'DELETE with WHERE should be allowed'),
    ]
    
    for cmd, desc in allowed:
        input_data = {'tool': {'name': 'bash', 'input': {'command': cmd}}}
        code, err = run_hook(input_data)
        if code != 0:
            print(f'❌ FAILED: {desc}')
            return False
        print(f'✅ ALLOWED: {cmd}')
    
    return True

def main():
    print('Testing pre_tool_use_hook.py...\n')
    
    print('Testing BLOCKED commands:')
    if not test_blocked_commands():
        sys.exit(1)
    
    print('\nTesting ALLOWED commands:')
    if not test_allowed_commands():
        sys.exit(1)
    
    print('\n✅ All tests passed!')
    return 0

if __name__ == '__main__':
    sys.exit(main())