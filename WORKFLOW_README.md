# n8n Weekly Dev Summary Workflow

Automatically generates a weekly narrative summary of GitHub repo activity using Claude API.

## Setup (5 Steps)

### 1. Import Workflow

```bash
# In n8n, go to Workflows → Import from File
# Select: workflows/weekly-dev-summary.json
```

### 2. Configure Environment Variables

In n8n, go to Settings → Variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `GITHUB_OWNER` | GitHub owner/organization | `openclaw` |
| `GITHUB_REPO` | Repository name | `openclaw` |
| `LANGUAGE` | Summary language | `EN` or `FR` |
| `SLACK_WEBHOOK_URL` | Slack incoming webhook | `https://hooks.slack.com/...` |

### 3. Add Credentials

**GitHub Token:**
1. Go to Settings → Credentials → Add Credential
2. Type: HTTP Header Auth
3. Name: `GitHub Token`
4. Header Name: `Authorization`
5. Header Value: `token ghp_your_github_token`

**Claude API:**
1. Go to Settings → Credentials → Add Credential
2. Type: Anthropic API
3. Name: `Claude API`
4. API Key: Your Anthropic API key

**Slack (optional):**
1. Create a Slack App with incoming webhooks
2. Add the webhook URL to environment variables

### 4. Select Delivery Method

The workflow includes both Email and Slack outputs:
- **Email**: Configure SMTP credentials and update the Email node
- **Slack**: Set `SLACK_WEBHOOK_URL` environment variable
- **Both**: Both nodes are connected, both will receive summaries

### 5. Activate Workflow

1. Click "Save"
2. Toggle "Active" to ON
3. The workflow will run every Friday at 5 PM (configurable)

## Configuration

### Change Schedule

Edit the Weekly Trigger node:
```
Cron Expression: 0 17 * * 5  (Friday 5 PM)
```

### Change Repository

Update environment variables:
```
GITHUB_OWNER=openclaw
GITHUB_REPO=openclaw
```

### Change Language

Set `LANGUAGE` variable:
- `EN` - English
- `FR` - French
- Add more in the Claude prompt as needed

## Example Output

```markdown
## Weekly Dev Summary - 2026-03-30

**Repository:** openclaw/openclaw

---

This week saw significant progress on the CLI dashboard feature. The team merged 
15 commits, closed 8 issues, and completed 5 pull requests.

### Key Achievements

The Textual UI implementation was completed, bringing a rich terminal interface 
to users. @alice led the development with 10 commits, focusing on the widget 
architecture and keyboard navigation.

### Notable Changes

- Added SQLite database integration for state persistence
- Implemented hot reload for development workflow
- Fixed critical memory leak in async operations
- Updated documentation with examples

### Contributors

Thanks to @alice, @bob, and @charlie for their contributions this week!

### Looking Forward

Next week's focus will be on performance optimization and adding export 
capabilities for dashboard data.
```

## Requirements

- n8n version >= 1.0
- GitHub Personal Access Token (repo read scope)
- Anthropic API key (Claude access)
- Slack or email for delivery (choose one or both)

## Troubleshooting

**"GitHub API rate limited"**
- Use authenticated requests (add GitHub token)
- Rate limit is 5000 requests/hour with auth

**"Claude API error"**
- Check API key is valid
- Verify you have credits available

**"No data in summary"**
- Check repository has activity in the past 7 days
- Verify environment variables are set correctly