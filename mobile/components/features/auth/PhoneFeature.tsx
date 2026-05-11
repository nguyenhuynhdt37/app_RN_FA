import React, { useState } from 'react'
import { View, KeyboardAvoidingView, Platform, ScrollView, Pressable, Image, StyleSheet, Dimensions, useColorScheme } from 'react-native'
import { useRouter } from 'expo-router'
import { Button, Input } from '@/components/ui'
import { Text } from '@/components/ui/Text'
import { Feather, Ionicons } from '@expo/vector-icons'
import { authService } from '@/src/services/auth.service'
import { useAuthStore } from '@/src/stores/auth.store'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import { LinearGradient } from 'expo-linear-gradient'
import { SocialAuthFeature } from './SocialAuthFeature'
import { useTranslation } from 'react-i18next'

const { width, height } = Dimensions.get('window')

export function PhoneFeature() {
  const { t } = useTranslation()
  const insets = useSafeAreaInsets()
  const [mode, setMode] = useState<'phone' | 'email'>('phone')
  const [value, setValue] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const router = useRouter()
  const { bypassLogin } = useAuthStore()
  const isDark = useColorScheme() === 'dark'

  const handleContinue = async () => {
    if (!value) return setError(t('auth.enter_value'))
    
    if (mode === 'phone' && !/^(0|\+84)[3|5|7|8|9][0-9]{8}$/.test(value)) {
      return setError(t('auth.invalid_phone'))
    }
    if (mode === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
      return setError(t('auth.invalid_email'))
    }

    setError('')
    setLoading(true)
    try {
      let identifier = value
      if (mode === 'phone') {
        identifier = value.startsWith('0') ? `+84${value.slice(1)}` : value
      }
      
      const { data } = await authService.sendOtp(identifier, 'authenticate')
      
      router.push({ 
        pathname: '/(auth)/verify-otp', 
        params: { 
          [mode]: identifier, 
          purpose: 'authenticate',
          resend_available_in: data.resend_available_in,
          otp_expires_in: data.otp_expires_in
        } 
      })
    } catch (e: any) {
      const errorCode = e.response?.data?.detail?.code
      const errorMsg = errorCode ? t(`errors.${errorCode}`) : (e.response?.data?.detail?.message || e.message || t('common.error'))
      setError(errorMsg)
    } finally { setLoading(false) }
  }

  return (
    <View style={styles.container}>
      {/* Immersive World Background (Original) */}
      <View style={StyleSheet.absoluteFill}>
        <Image
          source={require('@/assets/images/onboarding_world.png')}
          style={StyleSheet.absoluteFill}
          resizeMode="cover"
          blurRadius={Platform.OS === 'ios' ? 12 : 6}
        />
        <LinearGradient
          colors={[
            isDark ? 'rgba(9,9,11,0.6)' : 'rgba(255,255,255,0.4)',
            isDark ? 'rgba(9,9,11,0.95)' : 'rgba(255,255,255,0.92)',
            isDark ? '#09090b' : '#ffffff'
          ]}
          style={StyleSheet.absoluteFill}
        />
      </View>

      <View style={{ flex: 1, paddingTop: insets.top }}>
        <View style={styles.header}>
          <Pressable
            onPress={() => router.back()}
            style={[styles.backBtn, {
              backgroundColor: isDark ? 'rgba(255,255,255,0.15)' : 'rgba(0,0,0,0.05)',
              borderColor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'
            }]}
          >
            <Feather name="arrow-left" size={26} color={isDark ? '#FFFFFF' : '#000000'} />
          </Pressable>
        </View>

        <KeyboardAvoidingView 
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'} 
          style={{ flex: 1 }}
          keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 20}
        >
          <ScrollView 
            contentContainerStyle={[
              styles.scrollContent, 
              { paddingBottom: Math.max(insets.bottom, 40) }
            ]} 
            showsVerticalScrollIndicator={false}
          >
            {/* Original Header Section with i18n */}
            <View style={{ marginBottom: 40 }}>
              <View className="flex-row items-center gap-4 mb-4">
                <Text
                  style={{ color: isDark ? '#FFFFFF' : '#09090B' }}
                  className="text-5xl font-extrabold tracking-tighter leading-tight"
                >
                  {mode === 'phone' ? t('auth.welcome') : t('auth.email_login')}
                </Text>

                <View
                  className="w-12 h-12 rounded-2xl items-center justify-center shadow-lg shadow-emerald-500/20"
                  style={{ backgroundColor: isDark ? 'rgba(16, 185, 129, 0.2)' : 'rgba(16, 185, 129, 0.1)' }}
                >
                  <Ionicons name={mode === 'phone' ? 'library' : 'mail'} size={28} color="#10B981" />
                </View>
              </View>

              <Text style={{ color: isDark ? '#A1A1AA' : '#52525B' }} className="text-lg leading-relaxed">
                {mode === 'phone' ? t('auth.phone_msg') : t('auth.email_msg')}
              </Text>
            </View>

            {/* Input & Action Section with i18n */}
            <View className="gap-8">
              <Input
                label={mode === 'phone' ? t('auth.phone_placeholder') : t('auth.email_label')}
                placeholder={mode === 'phone' ? '0912 345 678' : t('auth.email_placeholder')}
                keyboardType={mode === 'phone' ? 'phone-pad' : 'email-address'}
                autoCapitalize="none"
                value={value}
                onChangeText={setValue}
                error={error}
                leftSlot={<Feather name={mode === 'phone' ? 'phone' : 'mail'} size={24} color={isDark ? '#A1A1AA' : '#71717A'} />}
              />

              <Button label={t('auth.continue')} onPress={handleContinue} loading={loading} fullWidth size="lg" />

              <Pressable
                onPress={() => { setMode(mode === 'phone' ? 'email' : 'phone'); setValue(''); setError('') }}
                className="py-2"
              >
                <Text style={{ color: isDark ? '#34D399' : '#059669' }} className="font-bold underline text-center text-lg">
                  {mode === 'phone' ? t('auth.use_email') : t('auth.use_phone')}
                </Text>
              </Pressable>

              <SocialAuthFeature />

              <Button
                label={t('auth.onboarding.try_dev')}
                onPress={async () => { setLoading(true); await bypassLogin(); router.replace('/(app)') }}
                variant="ghost"
                fullWidth
              />
            </View>
          </ScrollView>
        </KeyboardAvoidingView>
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  header: { paddingHorizontal: 24, paddingTop: 12, paddingBottom: 12, zIndex: 100 },
  backBtn: { width: 52, height: 52, borderRadius: 26, alignItems: 'center', justifyContent: 'center', borderWidth: 1 },
  scrollContent: { paddingHorizontal: 24, paddingTop: 32, minHeight: height * 0.7 }
})
