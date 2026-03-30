# Claude PR Review Agent

Automated PR review using Claude API. Analyzes diffs and posts structured comments.

## Setup

### CLI Usage

```bash
# Install dependencies
pip install anthropic

# Set API key
export ANTHROPIC_API_KEY=your_key

# Review a PR
python claude_review.py --pr https://github.com/owner/repo/pull/123

# Review from diff file
python claude_review.py --diff changes.diff
```

### GitHub Actions

1. Add `ANTHROPIC_API_KEY` to repository secrets
2. Copy `.github/workflows/claude-pr-review.yml` to your repo
3. Reviews will post automatically on new PRs

## Output Format

```markdown
## 🤖 Claude Code Review

### Summary
2-3 sentence summary of changes.

### ⚠️ Risks
- Identified risk 1
- Identified risk 2

### 💡 Suggestions
- Improvement suggestion 1
- Improvement suggestion 2

### Confidence: 🟢 High
```

## Example Output

### Example 1: Simple Feature PR

**PR:** Add user authentication endpoint

```markdown
## 🤖 Claude Code Review

### Summary
This PR adds a new `/auth/login` endpoint with JWT token generation.
The implementation uses bcrypt for password hashing and includes
basic error handling for invalid credentials.

### ⚠️ Risks
- Missing rate limiting on login endpoint (brute force vulnerability)
- JWT secret is hardcoded instead of using environment variable
- No input validation on email format

### 💡 Suggestions
- Add rate limiting middleware (e.g., express-rate-limit)
- Move JWT_SECRET to environment variables
- Add email format validation with a library like validator.js

### Confidence: 🟡 Medium
```

### Example 2: Refactoring PR

**PR:** Refactor database queries to use prepared statements

```markdown
## 🤖 Claude Code Review

### Summary
Refactors all raw SQL queries to use prepared statements,
preventing SQL injection vulnerabilities. Also adds connection
pooling for improved performance.

### ⚠️ Risks
- None identified - this is a security improvement

### 💡 Suggestions
- Consider adding query timeout configuration
- Document the prepared statement patterns for future developers

### Confidence: 🟢 High
```

## Configuration

| Environment Variable | Required | Description |
|---------------------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Your Anthropic API key |

## Limitations

- Maximum diff size: ~50k tokens (truncates larger diffs)
- Requires network access for API calls
- GitHub Actions requires `pull-requests: write` permission