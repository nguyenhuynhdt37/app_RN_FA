# Data Fetching: TanStack Query (React Query)

High-end mobile applications require robust network handling. Directly using `fetch` or `axios` inside `useEffect` leads to poor UX: missing loading states, lack of caching, complex error handling, and race conditions.

## The Rule

1. **NEVER use `useEffect` for data fetching.**
2. **Always use TanStack Query (`@tanstack/react-query`)**. Use `useQuery` for fetching data (GET requests) and `useMutation` for modifying data (POST, PUT, DELETE).
3. **Separate API calls from Components.** Define your API fetching functions in a separate file (e.g., `api.ts` or `services.ts`) and use custom hooks to encapsulate the `useQuery` logic.
4. Always handle `isLoading` and `isError` states visually in your components (e.g., using Skeletons).

### Do

```tsx
// 1. Separate API logic
import { useQuery } from '@tanstack/react-query';

async function fetchCourseDetails(courseId: string) {
  const response = await fetch(`https://api.example.com/courses/${courseId}`);
  if (!response.ok) throw new Error('Network response was not ok');
  return response.json();
}

// 2. Custom Hook
export function useCourseDetails(courseId: string) {
  return useQuery({
    queryKey: ['course', courseId],
    queryFn: () => fetchCourseDetails(courseId),
    staleTime: 1000 * 60 * 5, // Cache for 5 minutes
  });
}

// 3. Component Usage
import { View, Text } from 'react-native';
import { CourseSkeleton } from './CourseSkeleton';

export function CourseScreen({ courseId }: { courseId: string }) {
  const { data, isLoading, isError } = useCourseDetails(courseId);

  if (isLoading) return <CourseSkeleton />;
  if (isError) return <Text className="text-red-500">Failed to load course.</Text>;

  return (
    <View className="flex-1 p-4 bg-white dark:bg-zinc-900">
      <Text className="text-2xl font-bold dark:text-white">{data.title}</Text>
    </View>
  );
}
```

### Don't

```tsx
import { useState, useEffect } from 'react';
import { View, Text, ActivityIndicator } from 'react-native';

export function CourseScreen({ courseId }: { courseId: string }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  // BAD: Manual fetching logic leads to race conditions and no caching.
  useEffect(() => {
    fetch(`https://api.example.com/courses/${courseId}`)
      .then(res => res.json())
      .then(json => {
        setData(json);
        setLoading(false);
      });
  }, [courseId]);

  if (loading) return <ActivityIndicator />;

  return (
    <View>
      <Text>{data.title}</Text>
    </View>
  );
}
```
