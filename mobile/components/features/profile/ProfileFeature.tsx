import React, { useState, useEffect } from 'react'
import { ScrollView, Alert, View } from 'react-native'
import { useColorScheme } from 'nativewind'
import { useAuthStore } from '@/src/stores/auth.store'
import { useRouter } from 'expo-router'
import { useTranslation } from 'react-i18next'
import * as ImagePicker from 'expo-image-picker'
import { authService } from '@/src/services/auth.service'
import * as Haptics from 'expo-haptics'
import { AnimatePresence } from 'moti'

// Sub-components
import { ProfileHeader } from './components/ProfileHeader'
import { ProfileStats } from './components/ProfileStats'
import { ProfileAbout } from './components/ProfileAbout'
import { ProfileExpertise } from './components/ProfileExpertise'
import { ProfileActions } from './components/ProfileActions'
import { EditProfileForm } from './components/EditProfileForm'

import { Screen } from '@/components/layout/Screen'

export function ProfileFeature() {
  const { user, logout, setUser } = useAuthStore()
  const router = useRouter()
  const { t } = useTranslation()
  const [isEditing, setIsEditing] = useState(false)
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [editData, setEditData] = useState({
    full_name: '', 
    username: '', 
    bio: '', 
    learning_goals: '', 
    avatar_url: '',
  })

  useEffect(() => {
    if (user) {
      setEditData({
        full_name: user.full_name || '',
        username: user.username || '',
        bio: user.bio || '',
        learning_goals: user.learning_goals || '',
        avatar_url: user.avatar_url || '',
      })
    }
  }, [user])

  const handleLogout = () => {
    Alert.alert(t('auth.profile.logout_confirm.title'), t('auth.profile.logout_confirm.description'), [
      { text: t('common.cancel'), style: 'cancel' },
      { text: t('auth.profile.logout_confirm.confirm'), style: 'destructive', onPress: async () => {
        await logout(); router.replace('/(auth)/phone');
      }}
    ])
  }

  const handlePickImage = async () => {
    const res = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaType.Images,
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.7,
    })

    if (res.canceled) return

    try {
      setUploading(true)
      const { data } = await authService.uploadAvatar(res.assets[0].uri)
      setEditData(p => ({ ...p, avatar_url: data.avatar_url }))
      if (user) {
        setUser({ ...user, avatar_url: data.avatar_url })
      }
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success)
    } catch (e) {
      Alert.alert(t('common.error'), 'Upload failed.')
    } finally {
      setUploading(false)
    }
  }

  const handleSave = async () => {
    try {
      setLoading(true)
      const { data } = await authService.updateProfile({
        ...editData,
        specializations: user?.specializations || [],
        interest_ids: user?.interest_ids || [],
        daily_goal_minutes: user?.daily_goal_minutes || 30
      })
      setUser(data)
      setIsEditing(false)
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success)
    } catch (e) {
      Alert.alert(t('common.error'), 'Update failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Screen safeArea={false} withTabBar={!isEditing}>
      {isEditing ? (
        <EditProfileForm
          data={editData}
          onChange={(k, v) => setEditData(p => ({ ...p, [k]: v }))}
          onSave={handleSave}
          onCancel={() => setIsEditing(false)}
          loading={loading}
        />
      ) : (
        <ScrollView 
          style={{ flex: 1 }} 
          showsVerticalScrollIndicator={false}
          contentContainerStyle={{ paddingBottom: 100 }}
        >
          <ProfileHeader 
            user={user} 
            onPickImage={handlePickImage} 
            uploading={uploading} 
          />
          <ProfileStats />
          <ProfileAbout user={user} />
          <ProfileExpertise user={user} />
          <ProfileActions onEdit={() => setIsEditing(true)} />
        </ScrollView>
      )}
    </Screen>
  )
}
