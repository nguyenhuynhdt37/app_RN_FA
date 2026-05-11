# Styling Consistency: Dark Mode

Study applications often have users studying late at night. Therefore, **Dark Mode is a first-class citizen**. 

## The Rule

1. **Every UI component MUST define both light and dark mode classes** using NativeWind's `dark:` modifier.
2. If you specify a background color or text color, you must immediately specify its `dark:` counterpart.
3. Ensure sufficient contrast in both modes (e.g., `bg-white dark:bg-zinc-900` and `text-black dark:text-white`).

### Do

```tsx
import { View, Text } from 'react-native';

export function StudyCard({ title, description }: { title: string, description: string }) {
  return (
    <View className="p-4 bg-white border border-zinc-200 rounded-xl dark:bg-zinc-900 dark:border-zinc-800">
      <Text className="text-xl font-bold text-zinc-900 dark:text-zinc-50">
        {title}
      </Text>
      <Text className="mt-2 text-base text-zinc-600 dark:text-zinc-400">
        {description}
      </Text>
    </View>
  );
}
```

### Don't

```tsx
import { View, Text } from 'react-native';

export function StudyCard({ title, description }: { title: string, description: string }) {
  // Missing dark mode classes will cause the app to look broken when the system theme switches
  return (
    <View className="p-4 bg-white border border-zinc-200 rounded-xl">
      <Text className="text-xl font-bold text-black">
        {title}
      </Text>
      <Text className="mt-2 text-base text-gray-600">
        {description}
      </Text>
    </View>
  );
}
```
