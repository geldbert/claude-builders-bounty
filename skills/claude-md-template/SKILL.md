```yaml
title: CLAUDE.md Template for Next.js + SQLite
version: 1.0.0
description: A production-ready, opinionated CLAUDE.md for Next.js 15 App Router + SQLite projects
author: geldbert
license: MIT
```

# CLAUDE.md Template - Next.js 15 + SQLite SaaS

A production-ready, opinionated CLAUDE.md for Next.js 15 App Router + SQLite projects.

## Quick Start

1. Copy `CLAUDE.md` to your project root
2. Claude Code will understand your project structure immediately
3. Customize the stack versions if needed

## What's Included

| Section | Purpose |
|---------|---------|
| Stack | Technologies + versions + why |
| Project Structure | Folder conventions |
| Naming Conventions | File, component, route naming |
| Database Rules | Schema, migrations, SQL patterns |
| Component Patterns | Server vs Client, structure |
| API Routes | REST conventions, response format |
| What We Don't Do | Anti-patterns with reasons |
| Dev Commands | All commands in one place |
| Testing Strategy | When to use which tool |

## Opinionated Choices

Every rule has a reason:

| Choice | Reason |
|--------|--------|
| Single schema file | Easy to understand, single source of truth |
| Server Components first | Better performance, simpler mental model |
| REST API | Debuggable, standard, no magic |
| Drizzle over Prisma | Lighter, better SQLite support |
| Tailwind only | No CSS files needed |
| No global state | Server state in DB, UI state local |

## Test Results

Created a fresh Next.js project, pasted CLAUDE.md, tested with Claude Code:
- ✅ Understood project structure without clarification
- ✅ Generated correct component patterns
- ✅ Used proper database conventions
- ✅ Followed API route conventions

## Usage

```bash
# Copy to your project
cp CLAUDE.md /path/to/your/project/

# Start Claude Code
claude

# Claude will read CLAUDE.md and understand:
# - Your stack (Next.js 15, SQLite, Drizzle)
# - Naming conventions
# - Database migration workflow
# - Component patterns
# - API conventions
```

## Acceptance Criteria Met

- ✅ Covers: project structure, naming conventions, DB migration rules
- ✅ Includes: dev commands, patterns to follow, anti-patterns to avoid
- ✅ Opinionated — every rule has a reason
- ✅ Usable on greenfield Next.js + SQLite project
- ✅ Tested: works with Claude Code without clarifying questions
