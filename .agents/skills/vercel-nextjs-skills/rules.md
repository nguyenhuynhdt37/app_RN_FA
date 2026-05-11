# Next.js 15 Agent Rules

## 1. Core Principles
- **Default to Server Components**: Everything is a Server Component unless it needs interactivity (`useState`, `useEffect`, event listeners).
- **Server Actions for Mutations**: Use Server Actions (`'use server'`) for all `POST`, `PATCH`, `DELETE` operations.
- **Async/Await Data Fetching**: Fetch data directly in Server Components. Avoid `useEffect` for data fetching.

## 2. File Structure & Routing
- **App Router**: Use the `app/` directory.
- **Route Files**: Every route segment should ideally have `page.tsx`, `loading.tsx`, `error.tsx`, and `layout.tsx` if needed.
- **Colocation**: Place components, styles, and types used only by a specific route inside that route's directory.

## 3. Data Fetching & Caching
- **Fetch API**: Use the native `fetch` API. Next.js extends it with caching options.
- **Validation**: Use **Zod** to validate all API responses and form inputs.
- **Revalidation**: Use `revalidatePath` or `revalidateTag` inside Server Actions to purge cache after mutations.

## 4. Components & Styling
- **Client Components**: Mark with `'use client'` at the top. Keep them small and at the "leaves" of your tree.
- **Tailwind CSS**: Use Tailwind for all styling. Follow the project's design system (defined in `globals.css`).
- **Icons**: Use `lucide-react` or similar lightweight SVG icon libraries.

## 5. TypeScript
- **Strict Typing**: No `any`. Use interfaces for component props.
- **Server Action Types**: Define clear input/output types for Server Actions.

## 6. Performance & SEO
- **Metadata**: Always define `metadata` or `generateMetadata` for SEO.
- **Images**: Use `next/image` for all images with proper `alt`, `width`, and `height`.
- **Fonts**: Use `next/font` for optimized font loading.
