# UI Loading Skeletons for AI Streaming

When fetching data or waiting for an AI to stream its response, **always implement a Skeleton UI state**. This prevents the UI from shifting abruptly (Layout Shift) when data arrives, which feels jarring to the user. 

## The Rule

1. **Never use blank spaces or just an ActivityIndicator** for content-heavy sections (like cards, text blocks, or lists).
2. **Design Skeleton components** that mimic the exact dimensions of the loaded content.
3. Use a subtle pulse or shimmer animation to indicate that the content is loading or being generated.

### Do

```tsx
import { View, Text } from 'react-native';
import Animated, { FadeIn, FadeOut } from 'react-native-reanimated';

// The Skeleton mimics the exact shape of the message card
export function AIResponseSkeleton() {
  return (
    <Animated.View 
      entering={FadeIn} 
      exiting={FadeOut}
      className="p-4 bg-zinc-100 dark:bg-zinc-800 rounded-xl mb-4"
    >
      <View className="h-4 bg-zinc-300 dark:bg-zinc-700 rounded w-3/4 mb-2 animate-pulse" />
      <View className="h-4 bg-zinc-300 dark:bg-zinc-700 rounded w-full mb-2 animate-pulse" />
      <View className="h-4 bg-zinc-300 dark:bg-zinc-700 rounded w-5/6 animate-pulse" />
    </Animated.View>
  );
}

export function AIResponseCard({ isLoading, text }: { isLoading: boolean, text?: string }) {
  if (isLoading) return <AIResponseSkeleton />;
  
  return (
    <View className="p-4 bg-blue-50 dark:bg-blue-900 rounded-xl mb-4">
      <Text className="text-zinc-900 dark:text-zinc-100">{text}</Text>
    </View>
  );
}
```

### Don't

```tsx
import { View, Text, ActivityIndicator } from 'react-native';

export function AIResponseCard({ isLoading, text }: { isLoading: boolean, text?: string }) {
  if (isLoading) {
    // A tiny spinner will cause the layout to jump once the actual multi-line text streams in
    return (
      <View className="p-4">
        <ActivityIndicator />
      </View>
    );
  }
  
  return (
    <View className="p-4 bg-blue-50 rounded-xl mb-4">
      <Text>{text}</Text>
    </View>
  );
}
```
