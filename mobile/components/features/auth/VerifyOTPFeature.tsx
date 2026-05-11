import React, { useState, useEffect } from 'react'
import { View, KeyboardAvoidingView, Platform, ScrollView, Pressable, Image, StyleSheet, Dimensions, useColorScheme } from 'react-native'
import { useRouter } from 'expo-router'
import { Button, OTPInput } from '@/components/ui'
import { Text } from '@/components/ui/Text'
import { Feather, Ionicons } from '@expo/vector-icons'
import { authService } from '@/src/services/auth.service'
import { useAuthStore } from '@/src/stores/auth.store'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import { LinearGradient } from 'expo-linear-gradient'
import { useTranslation } from 'react-i18next'
import Animated, { FadeInDown, FadeInUp } from 'react-native-reanimated'

const { width, height } = Dimensions.get('window')

interface Props {
  identifier: string
  purpose: 'authenticate' | 'reset_password'
  initialResendCooldown?: number
  initialOtpExpiry?: number
}

export function VerifyOTPFeature({ 
  identifier, 
  purpose, 
  initialResendCooldown = 60,
  initialOtpExpiry = 300 
}: Props) {
  const { t } = useTranslation()
  const insets = useSafeAreaInsets()
  const [otp, setOtp] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [countdown, setCountdown] = useState(initialResendCooldown)
  const [otpExpiry, setOtpExpiry] = useState(initialOtpExpiry)
  const [confirmCooldown, setConfirmCooldown] = useState(0)
  const router = useRouter()
  const { saveTokens } = useAuthStore()
  const isDark = useColorScheme() === 'dark'

  // Cooldown Timer
  useEffect(() => {
    const timer = countdown > 0 ? setInterval(() => setCountdown(c => c - 1), 1000) : null
    return () => { if (timer) clearInterval(timer) }
  }, [countdown])

  // OTP Expiry Timer
  useEffect(() => {
    const timer = otpExpiry > 0 ? setInterval(() => setOtpExpiry(c => c - 1), 1000) : null
    return () => { if (timer) clearInterval(timer) }
  }, [otpExpiry])

  // Confirm Cooldown Timer
  useEffect(() => {
    const timer = confirmCooldown > 0 ? setInterval(() => setConfirmCooldown(c => c - 1), 1000) : null
    return () => { if (timer) clearInterval(timer) }
  }, [confirmCooldown])

  const handleVerify = async () => {
    if (otp.length < 6) return
    setError('')
    setLoading(true)
    try {
      const { data } = await authService.verifyOtp(identifier, otp, purpose)

      if (purpose === 'authenticate' && data.otp_token) {
        const tokenRes = await authService.authenticate(data.otp_token)
        await saveTokens(tokenRes.data)
        router.replace('/(app)')
      }
    } catch (e: any) {
      const errorCode = e.response?.data?.detail?.code
      const errorMsg = errorCode ? t(`errors.${errorCode}`) : (e.response?.data?.detail?.message || e.message || t('auth.otp_invalid'))
      setError(errorMsg)
      // Bắt đầu 10 giây chờ nếu nhập sai
      setConfirmCooldown(10)
    } finally {
      setLoading(false)
    }
  }

  const handleResend = async () => {
    if (countdown > 0) return
    setError('')
    try {
      const { data } = await authService.sendOtp(identifier, purpose)
      setCountdown(data.resend_available_in || 60)
      setOtpExpiry(data.otp_expires_in || 300)
      setOtp('')
    } catch (e: any) {
      setError(e.message || t('common.error'))
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <View style={styles.container}>
      {/* Immersive Background matching PhoneFeature */}
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
        {/* Header with Circular Back Button */}
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
            
            {/* Elegant Header Section */}
            <Animated.View entering={FadeInUp.duration(800)} style={{ marginBottom: 40 }}>
              <View className="flex-row items-center gap-4 mb-4">
                <Text
                  style={{ color: isDark ? '#FFFFFF' : '#09090B' }}
                  className="text-5xl font-extrabold tracking-tighter leading-tight"
                >
                  {t('auth.verify_title')}
                </Text>

                <View
                  className="w-12 h-12 rounded-2xl items-center justify-center shadow-lg shadow-emerald-500/20"
                  style={{ backgroundColor: isDark ? 'rgba(16, 185, 129, 0.2)' : 'rgba(16, 185, 129, 0.1)' }}
                >
                  <Ionicons name="shield-checkmark" size={28} color="#10B981" />
                </View>
              </View>

              <Text style={{ color: isDark ? '#A1A1AA' : '#52525B' }} className="text-lg leading-relaxed">
                {t('auth.verify_msg')} {'\n'}
                <Text className="font-bold text-emerald-500">{identifier}</Text>
              </Text>
            </Animated.View>

            {/* OTP Input Section */}
            <Animated.View entering={FadeInDown.delay(200).duration(800)} className="gap-8">
              <View className="items-center">
                <OTPInput value={otp} onChange={setOtp} error={error} className="justify-center" />
                
                <View className="mt-6 items-center">
                  {error ? (
                    <Text className="text-rose-500 text-sm font-bold">{error}</Text>
                  ) : (
                    <View className="flex-row items-center gap-2">
                      <Feather name="clock" size={14} color={isDark ? '#A1A1AA' : '#71717A'} />
                      <Text style={{ color: isDark ? '#A1A1AA' : '#71717A' }} className="text-sm font-medium">
                        {t('auth.otp_expires_in')}: {formatTime(otpExpiry)}
                      </Text>
                    </View>
                  )}
                </View>
              </View>

              <Button
                label={confirmCooldown > 0 ? `${t('common.confirm')} (${confirmCooldown}s)` : t('common.confirm')}
                onPress={handleVerify}
                loading={loading}
                disabled={otp.length < 6 || otpExpiry === 0 || confirmCooldown > 0}
                fullWidth
                size="lg"
              />

              <View className="flex-row items-center justify-center mt-4">
                <Text style={{ color: isDark ? '#A1A1AA' : '#52525B' }} className="text-base">
                  {t('auth.not_received')}{' '}
                </Text>
                <Pressable onPress={handleResend} disabled={countdown > 0}>
                  <Text 
                    style={{ color: countdown > 0 ? (isDark ? '#52525B' : '#A1A1AA') : '#10B981' }} 
                    className="text-base font-bold underline"
                  >
                    {countdown > 0 ? `${t('auth.resend_after')} ${countdown}s` : t('auth.resend_now')}
                  </Text>
                </Pressable>
              </View>
            </Animated.View>

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
