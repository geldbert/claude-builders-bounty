# CLAUDE.md - Next.js 15 + SQLite SaaS Project

> Opinionated template for AI-assisted development with Claude Code.
> Every rule exists because we learned the hard way.

## Stack & Versions

```
Next.js: 15.x (App Router)
React: 19.x
SQLite: better-sqlite3 (local) or Turso/libsql (edge)
TypeScript: 5.x
Node.js: 20.x LTS
```

## Project Structure

```
src/
├── app/                    # Next.js App Router
│   ├── (auth)/            # Auth route group
│   │   ├── login/
│   │   ├── signup/
│   │   └── layout.tsx
│   ├── (dashboard)/       # Protected routes
│   │   ├── dashboard/
│   │   ├── settings/
│   │   └── layout.tsx
│   ├── api/               # API routes
│   │   ├── webhooks/
│   │   └── [...catchall]/
│   ├── layout.tsx
│   └── page.tsx
├── components/
│   ├── ui/                # Base UI (shadcn/ui)
│   ├── forms/             # Form components
│   └── features/          # Feature-specific
├── lib/
│   ├── db.ts              # SQLite connection
│   ├── auth.ts            # Auth utilities
│   ├── utils.ts           # Shared utilities
│   └── constants.ts
├── hooks/                  # Custom React hooks
└── types/                  # TypeScript types

migrations/                 # SQL migration files
├── 0001_initial.sql
├── 0002_add_users.sql
└── ...

scripts/
├── seed.ts               # Development seeding
└── migrate.ts            # Run migrations
```

## Database Conventions

### SQLite Best Practices

```typescript
// lib/db.ts
import Database from 'better-sqlite3';

const db = new Database('data/app.db');
db.pragma('journal_mode = WAL');  // Always use WAL mode

export default db;
```

### Migrations

1. **One migration per logical change** - Don't combine unrelated changes
2. **Always reversible** - Include DOWN migration
3. **Named with timestamp prefix**: `0001_description.sql`

```sql
-- migrations/0001_initial.sql
-- UP
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  created_at INTEGER DEFAULT (strftime('%s', 'now'))
);

CREATE INDEX idx_users_email ON users(email);

-- DOWN
DROP TABLE users;
```

### Query Patterns

```typescript
// ✅ Use prepared statements
const getUser = db.prepare('SELECT * FROM users WHERE id = ?');
const user = getUser.get(userId);

// ✅ Use transactions for multi-step operations
const insertUser = db.transaction((email, name) => {
  const stmt = db.prepare('INSERT INTO users (email, name) VALUES (?, ?)');
  const result = stmt.run(email, name);
  
  const audit = db.prepare('INSERT INTO audit_log (action, user_id) VALUES (?, ?)');
  audit.run('user_created', result.lastInsertRowid);
  
  return result.lastInsertRowid;
});

// ❌ Never interpolate directly
const bad = db.exec(`SELECT * FROM users WHERE email = '${email}'`);  // SQL injection!
```

## Naming Conventions

### Files

- Components: `PascalCase.tsx` (e.g., `UserProfile.tsx`)
- Utilities: `camelCase.ts` (e.g., `formatDate.ts`)
- Hooks: `use[HookName].ts` (e.g., `useAuth.ts`)
- API routes: `kebab-case.ts` (e.g., `api-keys/route.ts`)

### Database

- Tables: `snake_case` plural (e.g., `users`, `api_keys`)
- Columns: `snake_case` (e.g., `created_at`, `user_id`)
- Foreign keys: `table_id` (e.g., `user_id` references `users.id`)

### Variables

```typescript
// ✅ Good
const userCount = await getUserCount();
const isAuthorized = checkAuth();
const formattedEmail = email.toLowerCase().trim();

// ❌ Bad - Hungarian notation
const nUserCount = await getUserCount();
const bIsAuthorized = checkAuth();

// ✅ Database results use snake_case
const { user_id, created_at } = result;

// ✅ Convert to camelCase for API responses
return { userId: user_id, createdAt: created_at };
```

## Component Patterns

### Server vs Client Components

```typescript
// app/(dashboard)/dashboard/page.tsx (Server Component)
import { getServerSession } from 'next-auth';
import DashboardClient from './DashboardClient';

export default async function DashboardPage() {
  const session = await getServerSession();
  const data = await getDashboardData(session.user.id);
  
  return <DashboardClient initialData={data} />;
}

// app/(dashboard)/dashboard/DashboardClient.tsx (Client Component)
'use client';
import { useState } from 'react';

export default function DashboardClient({ initialData }) {
  const [data, setData] = useState(initialData);
  
  return (
    <div>
      {/* Interactive UI here */}
    </div>
  );
}
```

### Form Components

```typescript
// components/forms/SettingsForm.tsx
'use client';
import { useActionState } from 'react';
import { updateSettings } from './actions';

export default function SettingsForm({ initialSettings }) {
  const [state, action, pending] = useActionState(updateSettings, {
    message: '',
    errors: {},
  });

  return (
    <form action={action}>
      <input name="email" defaultValue={initialSettings.email} />
      {state.errors?.email && <p>{state.errors.email}</p>}
      <button disabled={pending}>Save</button>
    </form>
  );
}
```

## API Routes

```typescript
// app/api/users/route.ts
import { NextResponse } from 'next/server';
import { auth } from '@/lib/auth';
import db from '@/lib/db';

export async function GET(request: Request) {
  const session = await auth();
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const users = db.prepare('SELECT id, email FROM users').all();
  return NextResponse.json(users);
}

export async function POST(request: Request) {
  const session = await auth();
  if (!session?.admin) {
    return NextResponse.json({ error: 'Forbidden' }, { status: 403 });
  }

  const body = await request.json();
  const stmt = db.prepare('INSERT INTO users (email) VALUES (?)');
  const result = stmt.run(body.email);

  return NextResponse.json({ id: result.lastInsertRowid }, { status: 201 });
}
```

## Environment Variables

```bash
# .env.local
DATABASE_URL="./data/app.db"    # Local SQLite
# DATABASE_URL="libsql://..."    # Turso/edge

NEXTAUTH_SECRET="..."           # Auth.js secret
NEXTAUTH_URL="http://localhost:3000"

STRIPE_SECRET_KEY="..."         # Payments
STRIPE_WEBHOOK_SECRET="..."

# .env.example (commit this)
DATABASE_URL="./data/app.db"
NEXTAUTH_SECRET=""
NEXTAUTH_URL=""
STRIPE_SECRET_KEY=""
STRIPE_WEBHOOK_SECRET=""
```

## What We Don't Do (And Why)

### ❌ ORM (Prisma, Drizzle)

SQLite is simple. Direct SQL is:
- Faster to debug (see exactly what runs)
- No schema sync issues
- Fewer dependencies

Use better-sqlite3 prepared statements. If you need migrations, use a simple script.

### ❌ GraphQL

REST is fine for most SaaS:
- Simpler mental model
- Better caching
- Easier to debug

Use tRPC or Server Actions for type-safe RPC when needed.

### ❌ Global State (Redux, Zustand)

Next.js 15 + React 19:
- Server Components handle data fetching
- React Context for client state
- URL state for filters/search

Only add Zustand for complex multi-component UI state.

### ❌ CSS-in-JS (Styled Components, Emotion)

Use Tailwind CSS:
- Smaller bundle
- Better performance (no runtime)
- Works with Server Components
- Design system is built-in

### ❌ Barrel Exports (`index.ts`)

```typescript
// ❌ Don't do this
export * from './Button';
export * from './Input';
export * from './Select';

// ✅ Import directly
import Button from '@/components/ui/Button';
```

Why: Barrel exports break tree-shaking and slow dev builds.

## Dev Commands

```bash
# Development
npm run dev           # Start Next.js dev server
npm run db:migrate    # Run migrations
npm run db:seed       # Seed development data
npm run db:reset      # Reset database (dev only!)

# Build
npm run build         # Build for production
npm run start         # Start production server

# Testing
npm run test          # Run tests
npm run test:watch    # Watch mode

# Database
npx tsx scripts/migrate.ts    # Run custom migration
npx tsx scripts/seed.ts       # Seed data
```

## Security Checklist

- [ ] Input validation with Zod
- [ ] CSRF protection (built into Next.js)
- [ ] Rate limiting on auth endpoints
- [ ] SQL prepared statements (never interpolate!)
- [ ] Environment variables in `.env.local` (never commit secrets)
- [ ] HTTPS in production (use Vercel/Cloudflare)
- [ ] Auth checks on all protected routes
- [ ] API rate limits for abuse prevention

## Testing

```typescript
// __tests__/lib/db.test.ts
import { describe, it, expect, beforeEach } from 'vitest';
import Database from 'better-sqlite3';

describe('Database', () => {
  let db: Database.Database;

  beforeEach(() => {
    db = new Database(':memory:');
    db.exec('CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT UNIQUE)');
  });

  it('inserts user correctly', () => {
    const stmt = db.prepare('INSERT INTO users (email) VALUES (?)');
    const result = stmt.run('test@example.com');
    expect(result.lastInsertRowid).toBe(1);
  });
});
```

## Quick Reference

| Task | Command/Pattern |
|------|-----------------|
| New page | `app/(group)/path/page.tsx` |
| API route | `app/api/path/route.ts` |
| DB query | `db.prepare('SQL').get/all/run()` |
| Auth check | `await getServerSession()` |
| Form action | `useActionState(action, state)` |
| Client component | Add `'use client'` at top |
| Server component | Default (no directive) |

---

## For Claude Code

When working on this project:

1. **Always use prepared statements** for SQL queries
2. **Server Components first**, Client Components for interactivity
3. **Single migration file** per logical change
4. **snake_case for DB**, **camelCase for API**
5. **Validate input** with Zod before database operations

Don't create ORMs, GraphQL, or global state unless explicitly asked.