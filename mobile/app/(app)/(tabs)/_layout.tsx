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
import { BlurView } from 'expo-blur'

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
      {getIcon(isFocused ? '#FFFFFF' : '#4b5563')}
    </Animated.View>
  )
}

function CustomTabBar({ state, descriptors, navigation }: any) {
  const insets = useSafeAreaInsets()
  const { colorScheme } = useColorScheme()
  const isDark = colorScheme === 'dark'
  const currentRouteName = state.routes[state.index].name
  const routes = state.routes.filter((r: any) => !['settings'].includes(r.name))
  const tabCount = routes.length
  const tabWidth = (TAB_BAR_WIDTH - 12) / tabCount
  
  const activeIndex = routes.findIndex((r: any) => r.name === state.routes[state.index].name)
  const offset = useSharedValue(activeIndex * tabWidth)
  const scale = useSharedValue(1)

  useEffect(() => {
    if (activeIndex === -1) return

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

  if (currentRouteName === 'settings') return null

  return (
    <View
      className="absolute left-0 right-0 items-center bg-transparent"
      style={{ bottom: insets.bottom + 4 }}
      pointerEvents="box-none"
    >
      <View
        style={{
          width: TAB_BAR_WIDTH,
          height: 74,
          borderRadius: 37,
          shadowColor: '#000',
          shadowOffset: { width: 0, height: 10 },
          shadowOpacity: isDark ? 0.5 : 0.1,
          shadowRadius: 20,
          elevation: 12,
          backgroundColor: 'transparent',
        }}
      >
        <BlurView
          intensity={isDark ? 40 : 85}
          tint={isDark ? 'dark' : 'light'}
          style={{ 
            flex: 1,
            borderRadius: 37,
            overflow: 'hidden',
            borderWidth: 1, 
            borderColor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
            flexDirection: 'row',
            alignItems: 'center',
            paddingHorizontal: 8,
          }}
        >
        {/* iOS 26 Solid Capsule Indicator - Perfectly Rounded */}
        <Animated.View
          style={[
            {
              position: 'absolute',
              left: 6,
              width: tabWidth - 6,
              height: 60,
              borderRadius: 30,
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
      </BlurView>
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
        tabBarTransparent: true,
        tabBarBackground: () => <View />,
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
