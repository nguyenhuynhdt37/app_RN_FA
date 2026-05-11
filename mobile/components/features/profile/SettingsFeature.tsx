import React from 'react'
import { View, ScrollView, Switch, Pressable } from 'react-native'
import { Screen } from '@/components/layout/Screen'
import { Text, Badge } from '@/components/ui'
import { Feather } from '@expo/vector-icons'
import { useRouter } from 'expo-router'
import { useColorScheme } from 'nativewind'

export function SettingsFeature() {
  const router = useRouter()
  const { colorScheme, setColorScheme } = useColorScheme()

  return (
    <Screen safeArea>
      <View className="flex-row items-center px-5 py-4 border-b border-white/20 dark:border-white/10 bg-white/50 dark:bg-zinc-900/50 backdrop-blur-md">
        <Pressable onPress={() => router.back()} className="mr-4">
          <Feather name="arrow-left" size={24} className="text-foreground" />
        </Pressable>
        <Text className="text-xl font-bold text-foreground">Cài đặt</Text>
      </View>

      <ScrollView className="flex-1 px-5 pt-6">
        <View className="mb-6">
          <Text className="text-sm font-bold text-primary uppercase mb-3">Hiển thị</Text>
          <View className="bg-white/70 dark:bg-zinc-900/60 border border-white/40 dark:border-white/10 rounded-2xl shadow-sm shadow-black/5 backdrop-blur-md">
            <View className="flex-row items-center justify-between p-4">
              <View className="flex-row items-center gap-3">
                <Feather name={colorScheme === 'dark' ? "moon" : "sun"} size={20} className="text-foreground" />
                <Text className="font-medium text-foreground">Chế độ ban đêm</Text>
              </View>
              <Switch
                value={colorScheme === 'dark'}
                onValueChange={v => setColorScheme(v ? 'dark' : 'light')}
                trackColor={{ false: '#E5E7EB', true: '#00A73D' }}
                thumbColor="#FFFFFF"
              />
            </View>
          </View>
        </View>

        <View className="mb-6">
          <Text className="text-sm font-bold text-primary uppercase mb-3">Thông tin ứng dụng</Text>
          <View className="bg-white/70 dark:bg-zinc-900/60 border border-white/40 dark:border-white/10 rounded-2xl p-4 items-center gap-2 shadow-sm shadow-black/5 backdrop-blur-md">
            <Feather name="cpu" size={32} className="text-primary" />
            <Text className="text-lg font-bold text-foreground">NEURALEARN</Text>
            <Text className="text-sm text-muted-foreground">Phiên bản 1.0.0</Text>
            <Badge label="Premium Mesh & Glassmorphism" variant="primary" className="mt-2" />
          </View>
        </View>
      </ScrollView>
    </Screen>
  )
}
