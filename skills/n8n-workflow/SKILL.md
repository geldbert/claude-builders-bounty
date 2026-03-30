# n8n Workflow: Weekly Dev Summary with Claude API

An n8n workflow that automatically generates weekly narrative summaries of GitHub repository activity using the Claude API.

## Features

- **Automated trigger**: Runs every Friday at 5pm (configurable)
- **GitHub integration**: Fetches commits, closed issues, and merged PRs
- **Claude API**: Generates narrative summary using `claude-sonnet-4-20250514`
- **Webhook delivery**: Sends to Discord or Slack
- **Multi-language**: Supports EN/FR output

## Quick Setup (5 Steps)

```bash
# 1. Import workflow in n8n
Settings > Import > weekly-dev-summary.json

# 2. Add GitHub token credential
Authorization: Bearer ghp_xxxx

# 3. Add Claude API key credential  
x-api-key: sk-ant-xxxx

# 4. Set environment variables
GITHUB_REPO=owner/repo
LANGUAGE=EN
WEBHOOK_URL=https://discord.com/api/webhooks/...

# 5. Activate workflow
```

## Configuration

| Variable | Required | Example |
|----------|----------|---------|
| `GITHUB_REPO` | Yes | `openclaw/openclaw` |
| `LANGUAGE` | No (default: EN) | `EN` or `FR` |
| `WEBHOOK_URL` | Yes | Discord/Slack webhook URL |

## Workflow Nodes

```
Schedule Trigger → Get Commits → Merge → Claude API → Send Webhook
                  → Get Issues   →
                  → Get PRs      →
```