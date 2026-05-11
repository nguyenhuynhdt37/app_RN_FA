# UI Component Slots for AI Widgets

When designing layouts and components, especially those that might contain AI-generated widgets or dynamic streaming content, always use the **slots and children pattern**. This ensures that AI widgets can be injected into the layout without breaking the underlying structure or causing unexpected layout shifts.

## The Rule

1. **Avoid hardcoding complex widget trees** inside parent layouts.
2. **Use React's `children`** or specific slot props (e.g., `headerSlot`, `footerSlot`, `aiWidgetSlot`) to pass UI components into a structural shell.
3. This guarantees that when AI components stream in or resize, the layout component only manages the container logic, while the injected component manages its own state and content.

### Do

```tsx
import { View } from 'react-native';

type CourseLayoutProps = {
  headerSlot: React.ReactNode;
  aiChatSlot: React.ReactNode;
  children: React.ReactNode;
};

export function CourseLayout({ headerSlot, aiChatSlot, children }: CourseLayoutProps) {
  return (
    <View className="flex-1 bg-white dark:bg-zinc-900">
      <View className="px-4 py-2 border-b border-zinc-200 dark:border-zinc-800">
        {headerSlot}
      </View>
      <View className="flex-1 p-4">
        {children}
      </View>
      <View className="absolute bottom-0 w-full p-4">
        {aiChatSlot}
      </View>
    </View>
  );
}
```

### Don't

```tsx
import { View } from 'react-native';
import { AIChatWidget } from './AIChatWidget'; // Hardcoded coupling

export function CourseLayout({ children }: { children: React.ReactNode }) {
  return (
    <View className="flex-1 bg-white dark:bg-zinc-900">
      {/* ... */}
      <View className="absolute bottom-0 w-full p-4">
        {/* Hardcoded widget prevents reusing the layout or mocking the widget easily */}
        <AIChatWidget courseId="123" />
      </View>
    </View>
  );
}
```
