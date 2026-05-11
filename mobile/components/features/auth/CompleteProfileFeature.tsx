import React, { useState } from 'react';
import { View, ScrollView, KeyboardAvoidingView, Platform, Alert, Image, StyleSheet, Dimensions, Pressable } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '../../../src/stores/auth.store';
import { authService } from '../../../src/services/auth.service';
import * as Haptics from 'expo-haptics';
import { AnimatePresence } from 'moti';
import { useColorScheme } from 'nativewind';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import * as ImagePicker from 'expo-image-picker';
import { ThemeToggle } from '../../ui/ThemeToggle';
import { LanguageToggle } from '../../ui/LanguageToggle';
import { Button } from '../../ui/Button';
import { Modal } from '../../ui/Modal';
import { LogOut, ArrowLeft } from 'lucide-react-native';

// Sub-components
import { ProfileStepIndicator } from './complete-profile/ProfileStepIndicator'
import { ProfileNavigation } from './complete-profile/ProfileNavigation'
import { StepBasicInfo } from './complete-profile/StepBasicInfo'
import { StepEducation } from './complete-profile/StepEducation'
import { StepSkills } from './complete-profile/StepSkills'
import { StepGoals } from './complete-profile/StepGoals'

const { height } = Dimensions.get('window')

export function CompleteProfileFeature() {
  const { t } = useTranslation()
  const insets = useSafeAreaInsets()
  const { colorScheme } = useColorScheme()
  const isDark = colorScheme === 'dark'
  const { user, refreshUser, logout } = useAuthStore()
  const [step, setStep] = useState(1)
  const [isLoading, setIsLoading] = useState(false)
  const [avatarUrl, setAvatarUrl] = useState(user?.avatar_url || '')
  const [isUploading, setIsUploading] = useState(false)

  const handlePickImage = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync()
    if (status !== 'granted') {
      Alert.alert(t('common.error'), 'Permission to access gallery is required!')
      return
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.8,
    })

    if (!result.canceled && result.assets[0].uri) {
      setIsUploading(true)
      try {
        const res = await authService.uploadAvatar(result.assets[0].uri)
        setAvatarUrl(res.data.avatar_url)
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success)
      } catch (e) {
        Alert.alert(t('common.error'), t('errors.UPLOAD_FAILED') || 'Upload failed')
      } finally {
        setIsUploading(false)
      }
    }
  }

  // Form State
  const [fullName, setFullName] = useState(user?.full_name || '')
  const [username, setUsername] = useState(user?.username || '')
  const [bio, setBio] = useState(user?.bio || '')
  const [specializations, setSpecializations] = useState<any[]>(
    user?.specializations?.filter(s => !!s.specialization_id).map(s => ({
      specialization_id: s.specialization_id,
      level: s.level || '',
      skill_ids: s.skill_ids || []
    })) || []
  )
  const [selectedInterestIds, setSelectedInterestIds] = useState<string[]>(user?.interest_ids || [])
  const [goals, setGoals] = useState(user?.learning_goals || '')
  const [dailyGoal, setDailyGoal] = useState(user?.daily_goal_minutes || 30)
  const [learningStyle, setLearningStyle] = useState(user?.preferred_learning_style || 'video')
  const [isUsernameManual, setIsUsernameManual] = useState(false)

  // Error State
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [showLogoutModal, setShowLogoutModal] = useState(false)

  const validateField = async (name: string, value: string) => {
    let errorCode = ''
    if (name === 'fullName') {
      if (!value) errorCode = 'MISSING_INFO'
      else if (value.length < 8) errorCode = 'FULL_NAME_TOO_SHORT'
    }
    
    if (name === 'username') {
      if (!value) errorCode = 'MISSING_INFO'
      else if (value.length < 8) errorCode = 'USERNAME_TOO_SHORT'
      else if (/^[0-9]/.test(value)) errorCode = 'USERNAME_STARTS_WITH_NUMBER'
      else if (/[^a-z0-9_]/.test(value)) errorCode = 'USERNAME_INVALID_FORMAT'
      else {
        // Check availability
        try {
          const res = await authService.checkUsername(value)
          if (!res.available) errorCode = 'USERNAME_TAKEN'
        } catch {
          // Ignore network errors for now
        }
      }
    }

    if (name === 'goals' && value.length < 10) errorCode = 'GOAL_TOO_SHORT'
    
    setErrors(prev => ({ ...prev, [name]: errorCode }))
    return !errorCode
  }

  const handleFullNameChange = (val: string) => {
    setFullName(val)
    // Clear error when user starts typing
    if (errors.fullName) {
      setErrors(prev => ({ ...prev, fullName: '' }))
    }
    
    if (!isUsernameManual) {
      const generated = val.toLowerCase()
        .normalize("NFD").replace(/[\u0300-\u036f]/g, "") // Remove accents
        .replace(/[^a-z0-9]/g, '') // Remove special chars
      
      if (generated) {
        const finalUsername = /^[0-9]/.test(generated) ? `user${generated}` : generated
        setUsername(finalUsername)
        // Clear username error too since it's auto-generated
        if (errors.username) {
          setErrors(prev => ({ ...prev, username: '' }))
        }
      }
    }
  }

  const handleUsernameChange = (val: string) => {
    const lowerValue = val.toLowerCase()
    setUsername(lowerValue)
    setIsUsernameManual(true)
    // Clear error when user starts typing
    if (errors.username) {
      setErrors(prev => ({ ...prev, username: '' }))
    }
  }

  const handleNext = async () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium)
    
    if (step === 1) {
      const isNameValid = await validateField('fullName', fullName)
      const isUserValid = await validateField('username', username)
      if (!isNameValid || !isUserValid) return
    }
    
    if (step === 2 && (specializations.length === 0 || specializations.some(s => !s.level))) {
      return Alert.alert(t('common.error'), t('auth.profile.education.missing_specialization'))
    }
    
    setStep(s => s + 1)
  }

  const handleSubmit = async () => {
    if (!validateField('goals', goals)) return
    setIsLoading(true)
    try {
      await authService.updateProfile({
        full_name: fullName, 
        username, 
        bio, 
        specializations,
        learning_goals: goals, 
        interest_ids: selectedInterestIds,
        daily_goal_minutes: dailyGoal, 
        preferred_learning_style: learningStyle,
        avatar_url: avatarUrl
      })
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success)
      await refreshUser()
    } catch (e: any) {
      const errorCode = e.response?.data?.detail?.code
      const errorMsg = errorCode ? t(`errors.${errorCode}`) : (e.response?.data?.detail?.message || e.message || t('common.error'))
      Alert.alert(t('common.error'), errorMsg)
    } finally { setIsLoading(false) }
  }

  return (
    <View className="flex-1 bg-black">
      {/* Immersive World Background */}
      <Image 
        source={require('@/assets/images/onboarding_world.png')} 
        style={StyleSheet.absoluteFill} 
        resizeMode="cover" 
        blurRadius={Platform.OS === 'ios' ? 10 : 5}
      />
      <LinearGradient
        colors={[
          'transparent', 
          isDark ? 'rgba(9,9,11,0.9)' : 'rgba(255,255,255,0.85)', 
          isDark ? '#09090b' : '#f8fafc' // Slate-50 for light mode instead of pure white
        ]}
        style={{ position: 'absolute', bottom: 0, left: 0, right: 0, height: height * 0.85 }}
      />

      <View style={{ flex: 1, paddingTop: insets.top }}>
        <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} className="flex-1">
          <ScrollView 
            className="flex-1 px-8" 
            contentContainerStyle={{ 
              paddingTop: 20, 
              paddingBottom: Math.max(insets.bottom, 50) 
            }} 
            showsVerticalScrollIndicator={false}
          >
            
            <ProfileStepIndicator 
              step={step} 
              leftSlot={
                step === 1 ? (
                  <LanguageToggle />
                ) : (
                  <Pressable 
                    onPress={() => setStep(s => s - 1)}
                    className="w-10 h-10 rounded-full bg-white/20 dark:bg-zinc-800/50 items-center justify-center border border-white/30 dark:border-zinc-700/50"
                  >
                    <ArrowLeft size={24} color={isDark ? '#fff' : '#27272a'} />
                  </Pressable>
                )
              }
              rightSlot={
                step === 1 ? (
                  <View className="flex-row items-center gap-3">
                    <ThemeToggle minimal />
                    <Pressable 
                      onPress={() => setShowLogoutModal(true)}
                      className="w-10 h-10 rounded-full bg-rose-500/10 items-center justify-center border border-rose-500/20"
                    >
                      <LogOut size={20} color="#F43F5E" />
                    </Pressable>
                  </View>
                ) : null
              }
            />
            
            <View className="min-h-[400px]">
              {step === 1 && (
                <StepBasicInfo 
                  fullName={fullName} setFullName={handleFullNameChange} 
                  username={username} setUsername={handleUsernameChange} 
                  bio={bio} setBio={setBio} 
                  avatarUrl={avatarUrl}
                  onPickImage={handlePickImage}
                  isUploading={isUploading}
                  errors={errors} validateField={validateField}
                />
              )}
              {step === 2 && <StepEducation specializations={specializations} setSpecializations={setSpecializations} />}
              {step === 3 && (
                <StepSkills 
                  specializations={specializations} 
                  setSpecializations={setSpecializations} 
                  selectedInterestIds={selectedInterestIds} 
                  setSelectedInterestIds={setSelectedInterestIds} 
                />
              )}
              {step === 4 && (
                <StepGoals 
                  goals={goals} setGoals={setGoals} 
                  dailyGoal={dailyGoal} setDailyGoal={setDailyGoal} 
                  learningStyle={learningStyle} setLearningStyle={setLearningStyle} 
                  errors={errors} validateField={validateField}
                />
              )}
            </View>

            <ProfileNavigation step={step} handleBack={() => setStep(s => s - 1)} handleNext={handleNext} handleSubmit={handleSubmit} isLoading={isLoading} />
          </ScrollView>
        </KeyboardAvoidingView>

        <Modal 
          visible={showLogoutModal}
          onClose={() => setShowLogoutModal(false)}
          onConfirm={logout}
          title={t('auth.profile.logout_confirm.title')}
          description={t('auth.profile.logout_confirm.description')}
          confirmText={t('auth.profile.logout_confirm.confirm')}
          variant="danger"
        />
      </View>
    </View>
  )
}
