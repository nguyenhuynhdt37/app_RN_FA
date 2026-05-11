import React from 'react'
import { View, Image, Dimensions } from 'react-native'
import { Text, Button } from '@/components/ui'
import { LinearGradient } from 'expo-linear-gradient'
import { useColorScheme } from 'nativewind'

const { width } = Dimensions.get('window')

export function HomeHero() {
  const { colorScheme } = useColorScheme()
  const isDark = colorScheme === 'dark'

  return (
    <View className="px-5 mb-8">
      <View className="relative h-[240px] rounded-[40px] overflow-hidden bg-emerald-500/10 border border-emerald-500/20">
        {/* 3D Isometric Image */}
        <Image 
          source={require('@/assets/images/onboarding_world.png')} 
          className="absolute w-full h-full"
          resizeMode="cover"
        />

        {/* Gradient Overlay for Readability - Tinh chỉnh để không bị quá tối */}
        <LinearGradient
          colors={['transparent', isDark ? 'rgba(9,9,11,0.7)' : 'rgba(255,255,255,0.85)']}
          className="absolute inset-0"
          start={{ x: 0, y: 0 }}
          end={{ x: 0, y: 1 }}
        />

        {/* Content */}
        <View className="absolute bottom-8 left-8 right-8">
          <Text className="text-3xl font-extrabold tracking-tighter text-zinc-900 dark:text-zinc-50 mb-5 leading-tight">
            Khám phá kiến thức{'\n'}cùng NeuralEarn 2026
          </Text>
          <View className="flex-row">
            <Button 
              label="Bắt đầu ngay" 
              size="sm" 
              className="shadow-xl shadow-emerald-500/40"
            />
          </View>
        </View>
      </View>
    </View>
  )
}
