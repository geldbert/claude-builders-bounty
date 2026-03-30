# Pre-Tool-Use Security Hook

Blocks destructive bash commands before Claude Code executes them.

## Installation

```bash
mkdir -p ~/.claude/hooks
cp pre_tool_use_hook.py ~/.claude/hooks/
chmod +x ~/.claude/hooks/pre_tool_use_hook.py
```

## What It Blocks

| Pattern | Reason |
|---------|--------|
| `rm -rf /` | Delete entire filesystem |
| `rm -rf ~` | Delete home directory |
| `DROP TABLE` | Database destruction |
| `TRUNCATE TABLE` | Delete all rows |
| `DELETE FROM` (no WHERE) | Delete all rows |
| `git push --force` | Overwrite remote history |
| `git reset --hard HEAD~` | Lose commits |
| `sudo rm -rf` | Privileged deletion |
| `dd if=... of=/dev/` | Overwrite disk device |
| `cat *.pem` | Expose private keys |

## Log File

All blocked attempts are logged to:
```
~/.claude/hooks/blocked.log
```

Format:
```
[2026-03-30T12:00:00] BLOCKED: rm -rf /
  Reason: rm -rf / would delete entire filesystem
  Project: /path/to/project
```

## Bypassing

If you intentionally need to run a blocked command, run it directly in your terminal instead of through Claude Code.

## Testing

```bash
# Run the test script
python3 test_hook.py

# Or test manually
echo '{"tool":{"name":"bash","input":{"command":"rm -rf /"}}}' | python3 pre_tool_use_hook.py
# Should exit with code 1 and print error to stderr
```