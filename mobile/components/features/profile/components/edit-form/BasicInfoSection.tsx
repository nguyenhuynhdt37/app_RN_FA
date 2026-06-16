import React from 'react'
import { View, Pressable, Image, ActivityIndicator } from 'react-native'
import { getFullImageUrl } from '@/src/utils/image'
import { Text } from '@/components/ui/Text'
import { Input } from '@/components/ui'
import { useTranslation } from 'react-i18next'
import { useColorScheme } from 'nativewind'
import * as ImagePicker from 'expo-image-picker'
import { authService } from '@/src/services/auth.service'
import { useAuthStore } from '@/src/stores/auth.store'
import { User, Camera, Info, AtSign, FileText } from 'lucide-react-native'
import * as Haptics from 'expo-haptics'

interface BasicInfoSectionProps {
  data: { 
    full_name: string; 
    username: string; 
    bio: string; 
    avatar_url: string | null 
  }
  onChange: (key: string, value: any) => void
}

export function BasicInfoSection({ data, onChange }: BasicInfoSectionProps) {
  const { t } = useTranslation()
  const { colorScheme } = useColorScheme()
  const isDark = colorScheme === 'dark'
  const [uploading, setUploading] = React.useState(false)
  const refreshUser = useAuthStore(s => s.refreshUser)

  const handlePickImage = async () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light)
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.8,
    })

    if (!result.canceled && result.assets[0].uri) {
      try {
        setUploading(true)
        const res = await authService.uploadAvatar(result.assets[0].uri)
        onChange('avatar_url', res.data.avatar_url)
        await refreshUser()
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success)
      } catch (err) {
        console.error('Upload failed', err)
      } finally {
        setUploading(false)
      }
    }
  }

  return (
    <View className="gap-10">
      {/* Avatar Section */}
      <View className="items-center">
        <Pressable onPress={handlePickImage} disabled={uploading}>
          <View 
            className={`w-[130px] h-[130px] rounded-full border-2 p-1 relative ${isDark ? 'border-zinc-800 bg-zinc-900' : 'border-zinc-100 bg-white'}`}
          >
            <View className="w-full h-full rounded-full overflow-hidden">
              {data.avatar_url ? (
                <Image 
                  source={{ uri: getFullImageUrl(data.avatar_url) as string }} 
                  className="w-full h-full" 
                />
              ) : (
                <View className={`w-full h-full rounded-full items-center justify-center ${isDark ? 'bg-zinc-800' : 'bg-zinc-100'}`}>
                  <User size={40} color={isDark ? '#3f3f46' : '#d4d4d8'} strokeWidth={2.5} />
                </View>
              )}
            </View>
            
            {uploading && (
              <View className="absolute inset-0 bg-black/40 rounded-full items-center justify-center">
                <ActivityIndicator color="#fff" />
              </View>
            )}
            
            <View className={`absolute bottom-1 right-1 w-[38px] h-[38px] rounded-full bg-emerald-500 border-4 ${isDark ? 'border-zinc-950' : 'border-white'} items-center justify-center`}>
              <Camera size={16} color="white" fill="white" />
            </View>
          </View>
        </Pressable>
        <Text className="text-zinc-500 dark:text-zinc-400 text-[10px] font-black uppercase tracking-[0.2em] mt-4">
          {t('profile_screen.fields.tap_to_change_avatar')}
        </Text>
      </View>

      {/* Fields Section */}
      <View>
        <View className="flex-row items-center mb-6 px-1">
          <View className="w-6 h-6 rounded-full bg-emerald-500/10 items-center justify-center mr-3">
            <Info size={12} color="#10b981" strokeWidth={3} />
          </View>
          <Text className="text-zinc-400 dark:text-zinc-500 text-[10px] font-black uppercase tracking-[0.3em]">
            {t('profile_screen.fields.basic_info_title')}
          </Text>
        </View>
        
        <View className="gap-8">
          <Input
            label={t('profile_screen.fields.full_name')}
            labelStyle={{ fontSize: 11, fontWeight: '900', textTransform: 'uppercase', letterSpacing: 1.5, color: '#10b981', marginBottom: 8 }}
            value={data.full_name}
            onChangeText={v => onChange('full_name', v)}
            placeholder={t('profile_screen.fields.full_name_placeholder')}
            className="rounded-full h-14 px-6 border-zinc-100 dark:border-white/5"
            leftSlot={<User size={18} color={isDark ? '#3f3f46' : '#d4d4d8'} strokeWidth={2.5} />}
          />
          <Input
            label={t('profile_screen.fields.username')}
            labelStyle={{ fontSize: 11, fontWeight: '900', textTransform: 'uppercase', letterSpacing: 1.5, color: '#10b981', marginBottom: 8 }}
            value={data.username}
            onChangeText={v => onChange('username', v.toLowerCase().replace(/[^a-z0-9_]/g, ''))}
            placeholder={t('profile_screen.fields.username_placeholder')}
            autoCapitalize="none"
            className="rounded-full h-14 px-6 border-zinc-100 dark:border-white/5"
            leftSlot={<AtSign size={18} color={isDark ? '#3f3f46' : '#d4d4d8'} strokeWidth={2.5} />}
          />
          <Input
            label={t('profile_screen.fields.bio')}
            labelStyle={{ fontSize: 11, fontWeight: '900', textTransform: 'uppercase', letterSpacing: 1.5, color: '#10b981', marginBottom: 8 }}
            value={data.bio}
            onChangeText={v => onChange('bio', v)}
            placeholder={t('profile_screen.fields.bio_input_placeholder')}
            multiline
            numberOfLines={3}
            className="rounded-[32px] h-32 px-6 pt-5 border-zinc-100 dark:border-white/5"
            leftSlot={
              <View className="pt-1">
                <FileText size={18} color={isDark ? '#3f3f46' : '#d4d4d8'} strokeWidth={2.5} />
              </View>
            }
          />
        </View>
      </View>
    </View>
  )
}

