import React, { useEffect } from 'react'
import { Tabs } from 'expo-router'
import { View, Pressable, Dimensions } from 'react-native'
import { LinearGradient } from 'expo-linear-gradient'
import { Home, Search, BookOpen, User } from 'lucide-react-native'
import * as Haptics from 'expo-haptics'
import Animated, {
  useAnimatedStyle,
  withSpring,
  withSequence,
  useSharedValue,
} from 'react-native-reanimated'
import { useColorScheme } from 'nativewind'
import { useSafeAreaInsets } from 'react-native-safe-area-context'

const { width } = Dimensions.get('window')
const TAB_BAR_WIDTH = width * 0.9

function TabBarIcon({ isFocused, routeName }: { isFocused: boolean, routeName: string }) {
  const scale = useSharedValue(1)

  useEffect(() => {
    scale.value = withSpring(isFocused ? 1.25 : 1, {
      damping: 15,
      stiffness: 200,
    })
  }, [isFocused])

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }]
  }))

  const getIcon = (color: string) => {
    const props = { size: 24, color, strokeWidth: isFocused ? 2.5 : 2 }
    if (routeName === 'index') return <Home {...props} />
    if (routeName === 'explore') return <Search {...props} />
    if (routeName === 'my-learn') return <BookOpen {...props} />
    return <User {...props} />
  }

  return (
    <Animated.View style={animatedStyle}>
      {getIcon(isFocused ? '#FFFFFF' : '#9ca3af')}
    </Animated.View>
  )
}

function CustomTabBar({ state, descriptors, navigation }: any) {
  const insets = useSafeAreaInsets()
  const { colorScheme } = useColorScheme()
  const isDark = colorScheme === 'dark'

  const routes = state.routes.filter((r: any) => !['settings'].includes(r.name))
  const tabCount = routes.length
  const tabWidth = (TAB_BAR_WIDTH - 12) / tabCount
  
  const activeIndex = routes.findIndex((r: any) => r.name === state.routes[state.index].name)
  const offset = useSharedValue(activeIndex * tabWidth)
  const scale = useSharedValue(1)

  useEffect(() => {
    // "Bulge" effect: Scale up then back to normal
    scale.value = withSequence(
      withSpring(1.18, { damping: 10, stiffness: 200 }),
      withSpring(1, { damping: 15, stiffness: 150 })
    )

    offset.value = withSpring(activeIndex * tabWidth, {
      damping: 20,
      stiffness: 150,
      mass: 1,
    })
  }, [activeIndex, tabWidth])

  const animatedIndicatorStyle = useAnimatedStyle(() => ({
    transform: [
      { translateX: offset.value },
      { scale: scale.value }
    ],
  }))

  return (
    <View
      className="absolute left-0 right-0 items-center bg-transparent"
      style={{ bottom: insets.bottom + 16 }}
      pointerEvents="box-none"
    >
      <View
        className="flex-row items-center h-[66px] bg-white/10 dark:bg-black/10 backdrop-blur-2xl rounded-full px-1.5"
        style={{ 
          width: TAB_BAR_WIDTH, 
          borderWidth: 1, 
          borderColor: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(255,255,255,0.2)',
        }}
      >
        {/* iOS 26 Solid Capsule Indicator - Perfectly Rounded */}
        <Animated.View
          style={[
            {
              position: 'absolute',
              left: 6,
              width: tabWidth - 4,
              height: 56,
              borderRadius: 28,
              backgroundColor: '#10B981',
              shadowColor: '#10B981',
              shadowOffset: { width: 0, height: 6 },
              shadowOpacity: 0.4,
              shadowRadius: 12,
              overflow: 'hidden',
            },
            animatedIndicatorStyle
          ]}
        >
          <LinearGradient
            colors={['#10B981', '#059669']}
            style={{ flex: 1 }}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
          />
        </Animated.View>

        {routes.map((route: any, index: number) => {
          const isFocused = activeIndex === index
          
          const onPress = () => {
            if (isFocused) return;
            Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium)
            navigation.navigate(route.name)
          }

          return (
            <Pressable 
              key={route.key} 
              onPress={onPress}
              className="flex-1 items-center justify-center h-full"
            >
              <TabBarIcon isFocused={isFocused} routeName={route.name} />
            </Pressable>
          )
        })}
      </View>
    </View>
  )
}

export default function TabsLayout() {
  return (
    <Tabs
      tabBar={(props) => <CustomTabBar {...props} />}
      screenOptions={{ 
        headerShown: false,
        tabBarStyle: {
          position: 'absolute',
          backgroundColor: 'transparent',
          borderTopWidth: 0,
          elevation: 0,
        }
      }}
    >
      <Tabs.Screen name="index" />
      <Tabs.Screen name="explore" />
      <Tabs.Screen name="my-learn" />
      <Tabs.Screen name="profile" />
      <Tabs.Screen 
        name="settings" 
        options={{ 
          href: null,
        }} 
      />
    </Tabs>
  )
}
