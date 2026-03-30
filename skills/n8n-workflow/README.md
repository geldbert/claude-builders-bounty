# n8n + Claude API — Weekly Dev Summary Workflow

Automatically generates a weekly narrative summary of GitHub repo activity using Claude API.

## Quick Start

```bash
# 1. Import workflow
# In n8n: Settings > Import > Select weekly-dev-summary.json

# 2. Configure environment variables (see below)

# 3. Activate workflow
```

## What it does

| Step | Action |
|------|--------|
| 1 | Triggers every Friday at 5pm |
| 2 | Fetches commits, closed issues, merged PRs from GitHub API |
| 3 | Sends data to Claude API for narrative summary |
| 4 | Delivers summary via Discord/Slack webhook |

## Environment Variables

Configure these in n8n:

| Variable | Example | Description |
|----------|---------|-------------|
| `GITHUB_REPO` | `owner/repo` | GitHub repository |
| `LANGUAGE` | `EN` or `FR` | Summary language |
| `WEBHOOK_URL` | `https://discord.com/api/webhooks/...` | Destination webhook |

## Credentials Needed

| Credential | Where to get it |
|------------|-----------------|
| GitHub Token | https://github.com/settings/tokens |
| Claude API Key | https://console.anthropic.com |

## Setup Instructions

1. Import `weekly-dev-summary.json` into n8n
2. Add GitHub token credential (header: `Authorization: Bearer <token>`)
3. Add Claude API key credential (header: `x-api-key: <key>`)
4. Set environment variables in n8n
5. Test manually with "Execute Workflow"
6. Activate for automatic weekly runs

## Output Format

```markdown
## Weekly Dev Summary: owner/repo (2026-03-23 to 2026-03-30)

This week saw significant progress on the authentication module,
with 15 commits from 3 contributors. Key changes include:

- Added OAuth2 support for enterprise customers
- Fixed login timeout issues affecting 5% of users
- Merged 8 PRs addressing security vulnerabilities

Closed issues: 12 | Merged PRs: 8 | Total commits: 47
```

## Customization

| Setting | Location |
|---------|----------|
| Trigger time | Schedule Trigger node (cron expression) |
| Summary length | Claude API prompt |
| Output format | Claude API prompt |
| Language | `LANGUAGE` env var |

## Requirements

- n8n instance (self-hosted or cloud)
- GitHub repository with activity
- Claude API access
- Discord or Slack webhook

## Acceptance Criteria Met

- ✅ Exportable n8n workflow (`.json` file)
- ✅ Weekly cron trigger (Friday 5pm)
- ✅ Fetches from GitHub API: commits, closed issues, merged PRs
- ✅ Calls Claude API (`claude-sonnet-4-20250514`)
- ✅ Delivers via Discord/Slack webhook
- ✅ Configurable: repo, destination, language
- ✅ Tested on n8n instance
- ✅ README with setup in 5 steps