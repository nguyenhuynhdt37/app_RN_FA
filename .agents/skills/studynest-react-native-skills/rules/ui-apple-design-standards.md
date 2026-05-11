# UI/UX: Apple Design Standards (iOS Style)

To achieve a "Super High-End" premium feel, especially on iOS devices, the application UI must adhere to Apple's Human Interface Guidelines (HIG). This means utilizing native-feeling typography, glassmorphism, spring animations, and haptic feedback.

## The Rule

1. **Typography**: Rely on the system default font (SF Pro on iOS). Do not load custom fonts unless explicitly required by brand guidelines. Use standard font weights (e.g., `font-semibold` for titles, `font-normal` for body).
2. **Glassmorphism (Blur)**: Use `expo-blur` (`<BlurView>`) for floating headers, bottom sheets, and tab bars. Never use a solid opaque color for overlays if a blur can be applied.
3. **Animations**: Always use `react-native-reanimated` with `withSpring` for layout transitions, modal presentations, and interactive components. Avoid linear `withTiming` animations as they feel robotic and non-native to iOS users.
4. **Haptic Feedback**: Always use `expo-haptics` for meaningful user interactions (e.g., toggling a switch, submitting a form, pulling to refresh, or deleting an item). Use `Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light)` for subtle interactions.

### Do

```tsx
import { View, Text, TouchableOpacity } from 'react-native';
import { BlurView } from 'expo-blur';
import * as Haptics from 'expo-haptics';
import Animated, { useSharedValue, useAnimatedStyle, withSpring } from 'react-native-reanimated';

// 1. Premium Glassmorphism Header
export function BlurredHeader({ title }: { title: string }) {
  return (
    <BlurView intensity={80} tint="light" className="absolute top-0 w-full pt-12 pb-4 px-4 z-10 border-b border-black/10">
      <Text className="text-xl font-bold text-center">{title}</Text>
    </BlurView>
  );
}

// 2. Interactive Button with Haptics and Spring Animation
export function PremiumButton({ onPress }: { onPress: () => void }) {
  const scale = useSharedValue(1);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  const handlePressIn = () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    scale.value = withSpring(0.95, { damping: 15, stiffness: 300 });
  };

  const handlePressOut = () => {
    scale.value = withSpring(1, { damping: 15, stiffness: 300 });
  };

  return (
    <Animated.View style={animatedStyle}>
      <TouchableOpacity 
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
        onPress={onPress}
        activeOpacity={1}
        className="bg-blue-600 px-6 py-4 rounded-2xl shadow-sm"
      >
        <Text className="text-white font-semibold text-center text-lg">Continue</Text>
      </TouchableOpacity>
    </Animated.View>
  );
}
```

### Don't

```tsx
import { View, Text, TouchableOpacity } from 'react-native';

// BAD: Solid header with no blur effect feels cheap and blocks content abruptly
export function SolidHeader({ title }: { title: string }) {
  return (
    <View className="absolute top-0 w-full pt-12 pb-4 px-4 bg-white z-10 shadow-md">
      <Text className="text-xl font-bold">{title}</Text>
    </View>
  );
}

// BAD: Basic TouchableOpacity with no tactile haptic feedback and linear opacity animation
export function BasicButton({ onPress }: { onPress: () => void }) {
  return (
    <TouchableOpacity onPress={onPress} className="bg-blue-600 px-6 py-4 rounded-xl">
      <Text className="text-white font-semibold text-center">Continue</Text>
    </TouchableOpacity>
  );
}
```
