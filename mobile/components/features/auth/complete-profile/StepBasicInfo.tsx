import React from 'react';
import { View, TouchableOpacity, ActivityIndicator } from 'react-native';
import { Text } from '../../../ui/Text';
import { Input } from '../../../ui/Input';
import { User, Camera, AtSign } from 'lucide-react-native';
import { MotiView } from 'moti';
import { useTranslation } from 'react-i18next';
import { Image } from 'expo-image';

interface StepBasicInfoProps {
  fullName: string
  setFullName: (v: string) => void
  username: string
  setUsername: (v: string) => void
  bio: string
  setBio: (v: string) => void
  avatarUrl?: string
  onPickImage: () => void
  isUploading: boolean
  errors: Record<string, string>
  validateField: (name: string, value: string) => void
}

export function StepBasicInfo({ 
  fullName, setFullName, username, setUsername, bio, setBio,
  avatarUrl, onPickImage, isUploading,
  errors, validateField
}: StepBasicInfoProps) {
  const { t } = useTranslation()
  const API_URL = process.env.EXPO_PUBLIC_API_URL?.replace('/api/v1', '')

  const fullAvatarUrl = avatarUrl 
    ? (avatarUrl.startsWith('http') ? avatarUrl : `${API_URL}${avatarUrl}`)
    : null

  return (
    <MotiView
      from={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ type: 'timing', duration: 400 }}
    >

      <View className="items-center mb-8">
        <TouchableOpacity 
          activeOpacity={0.9}
          onPress={onPickImage}
          disabled={isUploading}
          className="relative"
        >
          <View className="w-32 h-32 rounded-full bg-emerald-500/10 dark:bg-emerald-500/20 border border-emerald-500/20 items-center justify-center backdrop-blur-3xl overflow-hidden">
            {isUploading ? (
              <ActivityIndicator color="#10B981" />
            ) : fullAvatarUrl ? (
              <Image 
                source={{ uri: fullAvatarUrl }} 
                style={{ width: '100%', height: '100%' }}
                contentFit="cover"
              />
            ) : (
              <User size={48} color="#10B981" />
            )}
          </View>
          <View className="absolute bottom-1 right-1 bg-emerald-500 p-3 rounded-full border-4 border-zinc-50 dark:border-zinc-950 shadow-lg shadow-emerald-500/50">
            <Camera size={16} color="white" />
          </View>
        </TouchableOpacity>
      </View>

      <View className="space-y-6">
        <Input 
          label={t('auth.profile.basic_info.full_name')} 
          placeholder={t('auth.profile.basic_info.full_name_placeholder')} 
          value={fullName} 
          onChangeText={setFullName}
          onBlur={() => validateField('fullName', fullName)}
          error={errors.fullName ? t(`errors.${errors.fullName}`) : ''}
          leftSlot={<User size={20} color="#10B981" />}
          className="rounded-full"
        />
        <Input 
          label={t('auth.profile.basic_info.username')} 
          placeholder={t('auth.profile.basic_info.username_placeholder')} 
          value={username} 
          onChangeText={setUsername}
          onBlur={() => validateField('username', username)}
          error={errors.username ? t(`errors.${errors.username}`) : ''}
          leftSlot={<AtSign size={20} color="#10B981" />}
          className="rounded-full"
        />
        <Input 
          label={t('auth.profile.basic_info.bio')} 
          placeholder={t('auth.profile.basic_info.bio_placeholder')} 
          value={bio} 
          onChangeText={setBio}
          multiline
          numberOfLines={2}
          className="rounded-3xl"
        />
      </View>
    </MotiView>
  )
}
