---
name: nextjs-architecture-2026
description: Production-ready patterns for Next.js 15 App Router. Enforces Feature-Sliced Design (FSD) light, Server Components first, and secure Data Fetching patterns.
---

# Next.js Architecture 2026

Standardized architecture for high-performance Next.js 15 applications.

## Folder Structure (FSD-Light)

Everything lives in `src/`:
- `app/`: Routing, Layouts, Loading, Error (The "Pages").
- `features/`: Specific business features (e.g., `auth`, `user-profile`, `data-dashboard`).
  - `components/`: UI components for this feature.
  - `actions.ts`: Server Actions for this feature.
  - `types.ts`: TypeScript definitions.
  - `services.ts`: Data fetching logic (Server-side).
- `components/`: Global UI components (e.g., `ui/` folder for shadcn-like components).
- `lib/`: Shared utilities (API clients, formatting).
- `hooks/`: Global React hooks.
- `store/`: Global state management (Zustand).

## Implementation Rules

### 1. Data Fetching
- **Server-Side First**: Fetch data directly in `page.tsx` using `async/await`.
- **API Client**: Use the centralized `apiFetch` in `lib/api.ts` to ensure cookie-based auth is handled.
- **Zod Validation**: Always validate API responses with Zod schemas.

### 2. Mutations
- **Server Actions**: Use `'use server'` actions for all data changes.
- **Revalidation**: Call `revalidatePath` or `revalidateTag` after successful mutations.

### 3. Components
- **Server by Default**: Do not use `'use client'` unless necessary for hooks or event listeners.
- **Prop Drilling**: Avoid deep prop drilling; use composition or context for deep trees.

### 4. Security
- **Never expose Secret Keys**: Ensure no backend environment variables are prefixed with `NEXT_PUBLIC_`.
- **Validation**: All inputs must be sanitized and validated on the server.

## Performance Checklist
- [ ] Are images using `next/image`?
- [ ] Is data fetching happening on the server where possible?
- [ ] Are dynamic routes using `loading.tsx` for streaming?
- [ ] Is `metadata` defined for SEO?
