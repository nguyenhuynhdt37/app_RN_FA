---
name: vercel-nextjs-skills
description:
  Next.js 15 App Router best practices for building high-performance, SEO-optimized, 
  and type-safe web applications. Covers Server Components, Server Actions, 
  Data Fetching, and UI patterns.
license: MIT
metadata:
  author: vercel
  version: '1.0.0'
---

# Next.js 15 Skills

Comprehensive best practices for Next.js 15 App Router applications. These rules ensure 
modern, efficient, and maintainable code generation.

## When to Apply

Reference these guidelines when:

- Building or refactoring Next.js 15+ App Router projects
- Implementing Server Components vs. Client Components
- Setting up Data Fetching and Caching strategies
- Working with Server Actions for mutations
- Optimizing for SEO and Core Web Vitals
- Configuring API Route Handlers

## Rule Categories by Priority

| Priority | Category          | Impact   | Prefix              |
| -------- | ----------------- | -------- | ------------------- |
| 1        | App Router Basics | CRITICAL | `next-app-`         |
| 2        | Data Fetching     | CRITICAL | `next-fetch-`       |
| 3        | Server Actions    | HIGH     | `next-action-`      |
| 4        | Component Pattern | HIGH     | `next-component-`   |
| 5        | SEO & Metadata    | HIGH     | `next-seo-`         |
| 6        | TypeScript        | MEDIUM   | `next-ts-`          |
| 7        | Performance       | MEDIUM   | `next-perf-`        |

## Quick Reference

### 1. App Router Basics (CRITICAL)
- **Server Components First**: Use Server Components by default.
- **Colocation**: Keep components, hooks, and tests close to their routes.
- **Route Segments**: Always include `loading.tsx` and `error.tsx`.

### 2. Data Fetching (CRITICAL)
- **Async Components**: Fetch data directly in Server Components using `async/await`.
- **Zod Validation**: Validate all external data and API inputs with Zod.

### 3. Server Actions (HIGH)
- **Form Mutations**: Use Server Actions for all form submissions and data mutations.
- **Optimistic UI**: Implement `useOptimistic` for a faster user experience.

### 4. Component Pattern (HIGH)
- **Client Boundary**: Use `'use client'` only at the leaves of the component tree.
- **Composition**: Pass Client Components as children to Server Components.

### 5. SEO & Metadata (HIGH)
- **Metadata API**: Use the `metadata` object or `generateMetadata` function.
- **Semantic HTML**: Use proper HTML5 elements for accessibility and SEO.

## How to Use

Follow these rules strictly when generating Next.js code. Refer to the specific rule files for detailed examples.
