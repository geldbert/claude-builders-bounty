# Changelog Generator Skill

Generates a structured `CHANGELOG.md` from git history.

## Installation

1. Copy `changelog.sh` to your project root or `$HOME/.local/bin/`
2. Make executable: `chmod +x changelog.sh`

## Usage

### Command Line

```bash
# Generate CHANGELOG.md from all commits
./changelog.sh

# Generate from specific tag
./changelog.sh --since-tag v1.0.0

# Output to custom file
./changelog.sh --output RELEASE_NOTES.md
```

### Claude Code Command

Add this to your `.claude/commands/generate-changelog.md`:

```markdown
# Generate Changelog

Generate a structured CHANGELOG.md from the git history.

## Steps

1. Run `./changelog.sh` to generate the changelog
2. Review the output in CHANGELOG.md
3. Commit changes if satisfied

## Arguments

- `--since-tag TAG`: Only include commits after this tag
- `--output FILE`: Write to custom output file (default: CHANGELOG.md)
```

## Categories

Commits are auto-categorized based on message prefix:

| Category | Prefixes |
|----------|----------|
| Added | feat, feature, add, new, + |
| Fixed | fix, bug, patch, resolve, - |
| Changed | change, update, modify, refactor, improve |
| Removed | remove, delete, drop, deprecate |

## Example Output

```markdown
# Changelog

## [v1.2.3] - 2026-03-30

### Added
- feat: Add user authentication (#abc) [Author]

### Fixed
- fix: Resolve login timeout issue (#def) [Author]

### Changed
- refactor: Improve database query performance [Author]

### Removed
- deprecate: Remove legacy API endpoints [Author]
```

## Testing

Run the test script:

```bash
./test_changelog.sh
```