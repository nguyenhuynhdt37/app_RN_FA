# AI Streaming UI Best Practices

When rendering text or UI that is actively streaming from an AI backend (e.g., Vercel AI SDK), the stream arrives in small chunks. Improperly handling these chunks can lead to catastrophic performance issues, layout thrashing, and Markdown parsing crashes.

## The Rule

1. **Debounce or Throttle Updates**: If the AI stream updates React state 50 times a second, your React Native app will crash or freeze. Ensure the streaming hook or store throttles UI updates to a reasonable frame rate (e.g., 16ms or 50ms).
2. **Stable Markdown Parsing**: Ensure your Markdown renderer can handle incomplete syntax safely. A half-streamed `**bold` tag should not crash the parser. Use robust libraries like `react-native-markdown-display` and memoize the rendered output.
3. **Scroll to Bottom**: When content is streaming, automatically scroll the `ScrollView` or `FlatList` to the bottom, but only if the user hasn't manually scrolled up to read earlier text.
4. **Use Skeletons (See `ui-loading-skeletons.md`)**: Provide visual context before the first chunk arrives.

### Do

```tsx
import { ScrollView, Text } from 'react-native';
import { useRef, useEffect } from 'react';

export function AIStreamingChat({ messages, isStreaming }: { messages: any[], isStreaming: boolean }) {
  const scrollViewRef = useRef<ScrollView>(null);

  return (
    <ScrollView 
      ref={scrollViewRef}
      onContentSizeChange={() => {
        // Auto-scroll when new chunks arrive
        if (isStreaming) {
          scrollViewRef.current?.scrollToEnd({ animated: true });
        }
      }}
      className="flex-1 p-4 bg-white dark:bg-zinc-900"
    >
      {messages.map((msg, idx) => (
        <MessageBubble key={idx} message={msg} />
      ))}
      
      {/* Visual indicator that the AI is typing, even if chunks are delayed */}
      {isStreaming && <TypingIndicator />}
    </ScrollView>
  );
}
```

### Don't

```tsx
import { ScrollView, Text } from 'react-native';

export function AIStreamingChat({ streamText }: { streamText: string }) {
  return (
    <ScrollView className="flex-1 p-4 bg-white">
      {/* 
        Updating a giant string in React State 100 times/sec causes massive re-renders.
        No auto-scroll means the user has to manually scroll as text appears.
      */}
      <Text>{streamText}</Text>
    </ScrollView>
  );
}
```
