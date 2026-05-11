# Architecture: Folder Structure & Feature Slices

A scalable React Native project requires strict organization. If UI, business logic, API calls, and schemas are mixed together in screen components, the app becomes unmaintainable. For this project, we enforce the **Feature-Slices** architectural pattern alongside Expo Router.

## The Rule

1. **`app/` is ONLY for Routing**: The `/app` directory must only contain Expo Router files (e.g., `_layout.tsx`, `index.tsx`, `[id].tsx`). Do not place complex UI logic, API calls, or styled components here. Import them from `features/` or `components/`.
2. **Use Feature Slices (`features/`)**: Group related code by domain/feature (e.g., `features/auth`, `features/courses`, `features/cart`) rather than by technical type. 
   - A feature slice should contain its own `components/`, `api/`, `hooks/`, and `schemas/` if applicable.
3. **Global Directories**:
   - `components/`: For generic, reusable UI building blocks (e.g., `Button.tsx`, `Card.tsx`).
   - `api/` or `services/`: For global API configuration or shared TanStack queries.
   - `store/`: For global state management (e.g., Zustand slices).
   - `utils/`: For pure helper functions (e.g., date formatting, string manipulation).
   - `constants/`: For design tokens, theme colors, and configuration constants.

### Do

```text
my-app/
├── app/
│   ├── _layout.tsx
│   ├── index.tsx          // Imports <CourseFeed /> from features/courses
│   └── course/[id].tsx    // Imports <CourseDetail /> from features/courses
├── components/
│   ├── Button.tsx         // Generic UI component
│   └── Skeleton.tsx       // Generic UI component
├── features/
│   ├── auth/
│   │   ├── api/
│   │   │   └── useLogin.ts // TanStack Query mutation
│   │   ├── components/
│   │   │   └── LoginForm.tsx
│   │   └── schemas/
│   │       └── authSchema.ts // Zod schema
│   ├── courses/
│   │   ├── api/
│   │   │   └── useCourses.ts
│   │   └── components/
│   │       ├── CourseFeed.tsx
│   │       └── CourseCard.tsx
├── store/
│   └── useCartStore.ts    // Zustand store
└── utils/
    └── formatDate.ts
```

### Don't

```text
my-app/
├── app/
│   ├── _layout.tsx
│   ├── index.tsx          // BAD: Contains 500 lines of UI, fetch calls, and Zod schemas directly inside the route file.
│   └── login.tsx          // BAD: Contains raw fetch calls and inline state management.
├── components/
│   ├── Button.tsx
│   ├── LoginForm.tsx      // BAD: Feature-specific component dumped in the global components folder.
│   └── CourseCard.tsx     // BAD: Feature-specific component dumped in the global components folder.
├── api/
│   └── index.ts           // BAD: A massive file containing all API calls for the entire app.
```
