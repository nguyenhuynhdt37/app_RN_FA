# Styling Conventions: NativeWind (Tailwind v4)

For modern styling in React Native projects, **NativeWind (Tailwind CSS)** is the absolute standard. It ensures consistent design tokens, faster generation, and avoids the bloat of inline styles or massive `StyleSheet.create` objects.

## The Rule

1. **Do NOT use `StyleSheet.create`** for standard layout, colors, padding, or typography. 
2. **Do NOT use `style={{}}` inline props** unless it is strictly necessary for dynamic values (e.g., calculated heights from React state, or reanimated styles).
3. **Always use the `className` prop** to apply Tailwind CSS classes.
4. Keep your classes logically ordered (e.g., layout -> size -> typography -> colors).

### Do

```tsx
import { View, Text, TouchableOpacity } from 'react-native';

export function PrimaryButton({ label, onPress }: { label: string, onPress: () => void }) {
  return (
    <TouchableOpacity 
      onPress={onPress}
      className="flex-row items-center justify-center w-full px-4 py-3 bg-blue-600 rounded-xl active:bg-blue-700"
    >
      <Text className="text-lg font-semibold text-white">
        {label}
      </Text>
    </TouchableOpacity>
  );
}
```

### Don't

```tsx
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';

export function PrimaryButton({ label, onPress }: { label: string, onPress: () => void }) {
  return (
    // Avoid StyleSheet.create for standard UI
    <TouchableOpacity onPress={onPress} style={styles.button}>
      <Text style={styles.text}>{label}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    width: '100%',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#2563EB',
    borderRadius: 12,
  },
  text: {
    fontSize: 18,
    fontWeight: '600',
    color: '#FFFFFF',
  }
});
```
