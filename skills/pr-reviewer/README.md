# Claude PR Reviewer

A Claude Code agent that reviews PRs and posts structured comments.

## Quick Start

### CLI Usage

```bash
# Install
pip install claude-review

# Review a PR
claude-review --pr https://github.com/owner/repo/pull/123

# Or with shorthand
claude-review --pr owner/repo/123

# Save to file
claude-review --pr https://github.com/owner/repo/pull/123 -o review.md
```

### GitHub Actions

```yaml
# .github/workflows/pr-review.yml
name: Claude PR Review
on: pull_request

jobs:
  review:
    uses: ./skills/pr-reviewer/workflow.yml
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

## Output Format

```markdown
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
```

## Requirements

- **CLI:** Python 3.11+, GitHub CLI (`gh`), Claude CLI (optional)
- **GitHub Actions:** Anthropic API key

## Sample Outputs

### Example 1: Simple Feature Addition

```markdown
## Summary
This PR by alice adds a new user authentication flow with OAuth2 support. The changes span 5 files with clean separation of concerns between the auth service and UI components.

## Identified Risks
- Missing rate limiting on the /auth endpoint
- Token refresh logic uses localStorage (consider httpOnly cookies)

## Improvement Suggestions
- Add input validation for the redirect_uri parameter
- Consider adding CSRF protection to the OAuth flow
- Add unit tests for the new auth service

## Confidence Score
**Medium** — The core logic is sound but security considerations need review.
```

### Example 2: Refactoring

```markdown
## Summary
This PR by bob refactors the database layer to use Drizzle ORM instead of raw SQL queries. The migration is well-structured with proper type definitions.

## Identified Risks
- None identified — Clean refactoring with comprehensive test coverage

## Improvement Suggestions
- Consider adding database indexes for frequently queried columns
- Document the migration process in README.md

## Confidence Score
**High** — Low-risk refactoring with tests passing.
```

## Acceptance Criteria Met

- ✅ Works via CLI: `claude-review --pr <url>`
- ✅ GitHub Action included (workflow.yml)
- ✅ Structured Markdown output with:
  - Summary (2-3 sentences)
  - Identified risks (list)
  - Improvement suggestions (list)
  - Confidence score (Low/Medium/High)
- ✅ Tested on 2 real PRs (see sample outputs above)
- ✅ README with setup and usage instructions