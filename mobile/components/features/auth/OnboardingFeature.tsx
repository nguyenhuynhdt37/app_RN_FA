import React, { useState, useEffect } from 'react'
import { View, Image, Dimensions, StyleSheet, BackHandler } from 'react-native'
import { useRouter } from 'expo-router'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import { LinearGradient } from 'expo-linear-gradient'
import { useTranslation } from 'react-i18next'
import { Button, ThemeToggle, LanguageToggle } from '@/components/ui'
import { Text } from '@/components/ui/Text'
import { useAuthStore } from '@/src/stores/auth.store'
import { useColorScheme } from 'nativewind'

const { width, height } = Dimensions.get('window')

export function OnboardingFeature() {
  const router = useRouter()
  const insets = useSafeAreaInsets()
  const bypassLogin = useAuthStore(s => s.bypassLogin)
  const isAuthenticated = useAuthStore(s => s.isAuthenticated)
  const [loading, setLoading] = useState(false)
  const { t } = useTranslation()
  const { colorScheme } = useColorScheme()
  const isDark = colorScheme === 'dark'

  // Handle Android Back Button
  useEffect(() => {
    const backAction = () => {
      if (!isAuthenticated) {
        // Nếu chưa login mà ở onboarding thì thoát app luôn thay vì lỗi back
        BackHandler.exitApp()
        return true
      }
      return false
    }

    const backHandler = BackHandler.addEventListener('hardwareBackPress', backAction)
    return () => backHandler.remove()
  }, [isAuthenticated])

  const handleTestLogin = async () => {
    setLoading(true)
    await bypassLogin()
    router.replace('/(app)')
  }

  return (
    <View style={styles.container}>
      {/* Immersive World Background */}
      <Image 
        source={require('@/assets/images/onboarding_world.png')} 
        style={StyleSheet.absoluteFill} 
        resizeMode="cover" 
      />

      {/* Elegant Overlay Gradient for Text Readability */}
      <LinearGradient
        colors={[
          'transparent', 
          isDark ? 'rgba(9,9,11,0.85)' : 'rgba(255,255,255,0.85)', 
          isDark ? '#09090b' : '#ffffff'
        ]}
        style={styles.gradient}
      />

      <View style={{ flex: 1, paddingTop: insets.top, paddingBottom: Math.max(insets.bottom, 20) }}>
        {/* Nút chuyển đổi giao diện và ngôn ngữ ở góc trên bên phải */}
        <View className="flex-row justify-end items-center px-6 pt-2 gap-3">
          <LanguageToggle />
          <ThemeToggle minimal />
        </View>

        <View className="flex-1 px-8 pb-10 justify-end">
          
          <View className="mb-8">
            <View className="bg-emerald-500/20 dark:bg-emerald-500/30 self-start px-5 py-2 rounded-full mb-5 backdrop-blur-xl border border-emerald-500/20">
              <Text className="text-emerald-700 dark:text-emerald-400 font-extrabold text-xs tracking-[2px] uppercase">
                {t('auth.onboarding.badge')}
              </Text>
            </View>
            
            {/* Sửa lỗi chữ đen trong Dark Mode bằng cách dùng class màu cụ thể */}
            <Text className="text-5xl font-extrabold text-zinc-900 dark:text-zinc-50 mb-4 tracking-tighter leading-[1.1]">
              {t('auth.onboarding.title')}
            </Text>
            <Text className="text-zinc-600 dark:text-zinc-400 text-xl leading-relaxed">
              {t('auth.onboarding.description')}
            </Text>
          </View>

          <View className="gap-4 w-full">
            <Button 
              label={t('auth.onboarding.start')} 
              onPress={() => router.push('/(auth)/phone')} 
              size="lg" 
              fullWidth 
              className="shadow-2xl shadow-emerald-500/30"
            />
            <Button 
              label={t('auth.onboarding.try_dev')} 
              onPress={handleTestLogin} 
              variant="secondary" 
              size="md" 
              loading={loading} 
              fullWidth 
            />
          </View>
        </View>
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  gradient: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: height * 0.8, // Tăng độ phủ của gradient để chữ nổi bật hơn
  }
})
