# CLAUDE.md - Next.js 15 + SQLite SaaS Project

> Opinionated conventions for AI-assisted development. Every rule exists because we learned it the hard way.

## Stack

| Layer | Technology | Version | Why |
|-------|------------|---------|-----|
| Framework | Next.js | 15.x | App Router, RSC, best DX |
| Database | SQLite | better-sqlite3 | Local-first, zero config, fast |
| ORM | Drizzle | Latest | Type-safe, migrations, minimal |
| Auth | Lucia | Latest | Simple, session-based, no OAuth complexity |
| Styling | Tailwind | 4.x | Utility-first, no CSS files |
| Forms | React Hook Form + Zod | Latest | Type-safe validation, minimal re-renders |
| Testing | Vitest | Latest | Fast, ESM-native |

**Node version:** 22.x LTS (use `.nvmrc`)

---

## Project Structure

```
src/
├── app/                    # Next.js App Router
│   ├── (auth)/            # Auth route group (no layout)
│   │   ├── login/
│   │   └── register/
│   ├── (dashboard)/       # Protected routes
│   │   ├── layout.tsx     # Dashboard layout
│   │   └── dashboard/
│   ├── api/               # API routes (REST, not tRPC)
│   │   └── [resource]/
│   │       └── route.ts
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Home
├── components/
│   ├── ui/                # Base components (Button, Input, etc.)
│   └── features/          # Feature-specific components
├── lib/
│   ├── db/                # Database layer
│   │   ├── schema.ts     # Drizzle schema (single file)
│   │   ├── migrations/    # SQL migrations
│   │   └── index.ts       # Connection + helpers
│   ├── auth.ts           # Lucia auth config
│   └── utils.ts          # Shared utilities
├── hooks/                 # Custom hooks
└── types/                 # Shared TypeScript types
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Files | kebab-case | `user-profile.tsx` |
| Components | PascalCase | `UserProfile` |
| Hooks | `use` prefix | `useCurrentUser` |
| Routes | lowercase | `/dashboard/settings` |
| API routes | RESTful nouns | `/api/users` not `/api/getUsers` |
| Database tables | snake_case | `user_sessions` |
| Columns | snake_case | `created_at` |

---

## Database Rules

### Schema Location
**Single file:** `src/lib/db/schema.ts`

```typescript
// schema.ts - ALL tables in one file
import { sqliteTable, text, integer } from 'drizzle-orm/sqlite-core';

export const users = sqliteTable('users', {
  id: text('id').primaryKey(),
  email: text('email').notNull().unique(),
  createdAt: integer('created_at', { mode: 'timestamp' }).$defaultFn(() => new Date()),
});

export const sessions = sqliteTable('sessions', {
  id: text('id').primaryKey(),
  userId: text('user_id').notNull().references(() => users.id),
  expiresAt: integer('expires_at', { mode: 'timestamp' }).notNull(),
});
```

### Migrations

| Rule | Reason |
|------|--------|
| Always use Drizzle migrations | Version control, reproducible |
| Never edit existing migrations | Causes drift, breaks prod |
| Name: `0001_add_users_table.sql` | Zero-padded for sort order |
| Test locally before commit | SQLite doesn't rollback easily |

### Migration Commands

```bash
# Generate migration after schema change
pnpm drizzle-kit generate

# Apply migrations
pnpm drizzle-kit migrate

# Push schema directly (dev only!)
pnpm drizzle-kit push
```

### SQL Patterns

```sql
-- ✅ Good: Explicit columns
SELECT id, email, created_at FROM users WHERE id = ?;

-- ❌ Bad: SELECT *
SELECT * FROM users;

-- ✅ Good: Parameterized queries (via Drizzle)
db.select().from(users).where(eq(users.id, userId));

-- ❌ Bad: String interpolation
db.execute(`SELECT * FROM users WHERE id = '${userId}'`);
```

---

## Component Patterns

### Server vs Client

| Use Server Components | Use Client Components |
|----------------------|----------------------|
| Data fetching | Interactivity (onClick, etc.) |
| Static content | Browser APIs (localStorage) |
| SEO-critical pages | Animations |
| Initial render | Form state |

```tsx
// ✅ Good: Server Component (default)
// app/dashboard/page.tsx
import { db } from '@/lib/db';

export default async function Dashboard() {
  const users = await db.select().from(users);
  return <UserList users={users} />;
}

// ✅ Good: Client Component (explicit)
// components/user-list.tsx
'use client';

import { useState } from 'react';

export function UserList({ users }) {
  const [filter, setFilter] = useState('');
  // Client-side filtering, interactivity
}
```

### Component Structure

```tsx
// ✅ Good: Destructure props, explicit return
type Props = {
  user: { id: string; email: string };
  onSelect?: (id: string) => void;
};

export function UserCard({ user, onSelect }: Props) {
  return (
    <div className="p-4 border rounded">
      <h3>{user.email}</h3>
      {onSelect && (
        <button onClick={() => onSelect(user.id)}>
          Select
        </button>
      )}
    </div>
  );
}

// ❌ Bad: Implicit return, no types
export const UserCard = ({ user }) => (
  <div>{user.email}</div>
);
```

---

## API Routes

### REST Conventions

| Method | Path | Action |
|--------|------|--------|
| GET | `/api/users` | List |
| GET | `/api/users/:id` | Get one |
| POST | `/api/users` | Create |
| PATCH | `/api/users/:id` | Update |
| DELETE | `/api/users/:id` | Delete |

### Response Format

```typescript
// ✅ Good: Consistent response shape
// app/api/users/route.ts
import { NextResponse } from 'next/server';
import { db } from '@/lib/db';
import { users } from '@/lib/db/schema';

export async function GET() {
  const allUsers = await db.select().from(users);
  return NextResponse.json({ data: allUsers });
}

export async function POST(request: Request) {
  const body = await request.json();
  const [user] = await db.insert(users).values(body).returning();
  return NextResponse.json({ data: user }, { status: 201 });
}

// ❌ Bad: Inconsistent shape
return NextResponse.json(users);  // No wrapper
return NextResponse.json({ user, count: 5 });  // Different shape
```

---

## What We Don't Do (And Why)

| Anti-pattern | Reason |
|--------------|--------|
| `useEffect` for fetching | Use Server Components or SWR |
| Global state (Redux) | Server state in DB, UI state local |
| CSS files | Tailwind handles everything |
| `any` type | Defeats TypeScript purpose |
| Dynamic imports everywhere | Slower initial load |
| tRPC | REST is simpler for small apps |
| Prisma | Drizzle is lighter, better SQLite support |
| Server Actions for everything | REST API is more debuggable |

---

## Dev Commands

```bash
# Development
pnpm dev              # Start dev server (port 3000)
pnpm db:studio        # Drizzle Studio (DB GUI)
pnpm db:migrate       # Run migrations

# Build & Deploy
pnpm build            # Production build
pnpm start            # Production server

# Testing
pnpm test             # Run Vitest
pnpm test:ui          # Vitest UI

# Linting
pnpm lint             # ESLint
pnpm format           # Prettier
```

---

## Quick Context for Claude

When starting work on this project:

1. **Check `src/lib/db/schema.ts`** for all database tables
2. **Use Server Components** unless interactivity required
3. **Run migrations** with `pnpm db:migrate` after schema changes
4. **Follow REST** for API routes
5. **Type everything** — no `any`

---

## Environment Variables

```env
DATABASE_URL=./sqlite.db
SESSION_SECRET=your-secret-here
NODE_ENV=development
```

---

## Testing Strategy

| Type | When | Tool |
|------|------|------|
| Unit | Pure functions, utils | Vitest |
| Integration | API routes | Vitest + fetch |
| E2E | Critical user flows | Playwright (optional) |

```typescript
// Example: API route test
import { expect, test } from 'vitest';

test('GET /api/users returns users', async () => {
  const res = await fetch('http://localhost:3000/api/users');
  const { data } = await res.json();
  expect(Array.isArray(data)).toBe(true);
});
```

---

## Summary

- **Single schema file** → Easy to understand
- **Server Components first** → Better performance, simpler
- **REST API** → Debuggable, standard
- **Drizzle migrations** → Safe schema changes
- **Tailwind only** → No CSS files needed
- **Type everything** → Catch errors early

This project prioritizes **simplicity over abstraction**. If you're adding a library, ask: "Do we really need this?"