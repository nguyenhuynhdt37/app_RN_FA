import React, { useRef } from 'react'
import { View, Pressable, Animated, Image } from 'react-native'
import { Text } from '@/components/ui'
import { Feather } from '@expo/vector-icons'
import * as Haptics from 'expo-haptics'
import { cn } from '@/src/lib/utils'
import { useAuthStore } from '@/src/stores/auth.store'

export function HomeHeader() {
  const user = useAuthStore((state) => state.user)
  const firstName = user?.full_name?.split(' ')[0] || 'Bạn'

  return (
    <View className="flex-row items-center justify-between px-6 pt-5 pb-2.5">
      <View className="flex-row items-center flex-1">
        <View className="relative w-[60px] h-[60px] items-center justify-center">
          {/* Decorative Background Ring */}
          <View className="absolute w-[58px] h-[58px] rounded-full border-[1.5px] border-emerald-500 opacity-15" />
          
          <View className="w-[50px] h-[50px] rounded-full bg-emerald-50 overflow-hidden border-2 border-white">
            {user?.avatar_url ? (
              <Image 
                source={{ uri: user.avatar_url }} 
                className="w-full h-full"
                resizeMode="cover"
              />
            ) : (
              <View className="flex-1 items-center justify-center">
                <Feather name="smile" size={26} color="#10b981" />
              </View>
            )}
          </View>
          
          {/* Status Badge */}
          <View className="absolute bottom-0.5 right-0.5 w-[18px] h-[18px] rounded-full bg-white items-center justify-center shadow-sm shadow-black elevation-sm">
            <View className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
          </View>
        </View>

        <View className="ml-3.5 justify-center">
          <Text className="text-[13px] font-semibold text-zinc-500 -mb-0.5">Chào buổi sáng 👋</Text>
          <Text className="text-[22px] font-black text-zinc-900 tracking-tighter" numberOfLines={1}>
            {firstName}
          </Text>
        </View>
      </View>

      <View className="flex-row gap-2.5">
        <HeaderButton icon="search" />
        <HeaderButton icon="bell" hasDot />
      </View>
    </View>
  )
}

function HeaderButton({ icon, hasDot }: { icon: keyof typeof Feather.glyphMap; hasDot?: boolean }) {
  const scaleAnim = useRef(new Animated.Value(1)).current

  const handlePressIn = () => {
    Animated.spring(scaleAnim, {
      toValue: 0.9,
      useNativeDriver: true,
      speed: 40,
      bounciness: 10,
    }).start()
  }

  const handlePressOut = () => {
    Animated.spring(scaleAnim, {
      toValue: 1,
      useNativeDriver: true,
      speed: 40,
      bounciness: 10,
    }).start()
  }

  const handlePress = () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light)
  }

  return (
    <Animated.View style={{ transform: [{ scale: scaleAnim }] }}>
      <Pressable
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
        onPress={handlePress}
        className="w-12 h-12 rounded-full items-center justify-center border border-emerald-500/10 bg-emerald-500/[0.08] active:bg-emerald-500/15"
      >
        <Feather name={icon} size={22} color="#10b981" />
        {hasDot && <View className="absolute top-3 right-3 w-2 h-2 rounded-full bg-red-500 border-[1.5px] border-white" />}
      </Pressable>
    </Animated.View>
  )
}
