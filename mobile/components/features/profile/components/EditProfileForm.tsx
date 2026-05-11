import React, { useState } from 'react'
import { View, Pressable, KeyboardAvoidingView, Platform, ScrollView, StyleSheet, Image, ActivityIndicator } from 'react-native'
import { Text } from '@/components/ui/Text'
import { Input, Button } from '@/components/ui'
import { Feather } from '@expo/vector-icons'
import { useTranslation } from 'react-i18next'
import { useColorScheme } from 'nativewind'
import * as ImagePicker from 'expo-image-picker'
import { MotiView } from 'moti'
import { authService } from '@/src/services/auth.service'
import { useAuthStore } from '@/src/stores/auth.store'

interface Props {
  data: { full_name: string; username: string; bio: string; learning_goals: string; avatar_url: string | null }
  onChange: (key: string, value: any) => void
  onSave: () => void
  onCancel: () => void
  loading: boolean
}

export function EditProfileForm({ data, onChange, onSave, onCancel, loading }: Props) {
  const { t } = useTranslation()
  const { colorScheme } = useColorScheme()
  const isDark = colorScheme === 'dark'
  const [uploading, setUploading] = useState(false)
  const refreshUser = useAuthStore(s => s.refreshUser)

  const handlePickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
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
      } catch (err) {
        console.error('Upload failed', err)
      } finally {
        setUploading(false)
      }
    }
  }

  return (
    <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={{ flex: 1 }}>
      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        {/* Header Section */}
        <MotiView 
          from={{ opacity: 0, translateY: -20 }}
          animate={{ opacity: 1, translateY: 0 }}
          style={styles.header}
        >
          <Pressable onPress={onCancel} style={[styles.backBtn, { backgroundColor: isDark ? '#27272a' : '#f4f4f5' }]}>
            <Feather name="chevron-left" size={24} color={isDark ? '#fff' : '#09090b'} />
          </Pressable>
          <Text style={{ color: isDark ? '#fff' : '#09090b' }} className="text-2xl font-black">
            {t('profile_screen.edit_profile')}
          </Text>
          <View style={{ width: 44 }} />
        </MotiView>

        {/* Avatar Section */}
        <View style={styles.avatarSection}>
          <Pressable onPress={handlePickImage} disabled={uploading}>
            <View style={[styles.avatarFrame, { borderColor: isDark ? '#27272a' : '#e4e4e7' }]}>
              {data.avatar_url ? (
                <Image source={{ uri: data.avatar_url }} style={styles.avatar} />
              ) : (
                <View style={styles.placeholderAvatar}>
                  <Feather name="user" size={40} color="#10b981" />
                </View>
              )}
              {uploading && (
                <View style={styles.uploadOverlay}>
                  <ActivityIndicator color="#fff" />
                </View>
              )}
              <View style={styles.editBadge}>
                <Feather name="camera" size={16} color="#fff" />
              </View>
            </View>
          </Pressable>
          <Text style={{ color: isDark ? '#71717a' : '#a1a1aa' }} className="text-sm font-medium mt-4">
            {t('profile_screen.fields.tap_to_change_avatar')}
          </Text>
        </View>

        {/* Form Sections */}
        <MotiView 
          from={{ opacity: 0, translateY: 20 }}
          animate={{ opacity: 1, translateY: 0 }}
          transition={{ delay: 100 }}
          style={styles.sections}
        >
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <Feather name="info" size={16} color="#10b981" />
              <Text className="text-emerald-500 text-xs font-black uppercase tracking-widest ml-2">
                {t('profile_screen.fields.basic_info_title')}
              </Text>
            </View>
            <View style={styles.fieldGroup}>
              <Input
                label={t('profile_screen.fields.full_name')}
                value={data.full_name}
                onChangeText={v => onChange('full_name', v)}
                placeholder={t('profile_screen.fields.full_name_placeholder')}
                leftSlot={<Feather name="user" size={18} color={isDark ? '#52525b' : '#a1a1aa'} />}
              />
              <Input
                label={t('profile_screen.fields.username')}
                value={data.username}
                onChangeText={v => onChange('username', v.toLowerCase().replace(/[^a-z0-9_]/g, ''))}
                placeholder={t('profile_screen.fields.username_placeholder')}
                autoCapitalize="none"
                leftSlot={<Feather name="at-sign" size={18} color={isDark ? '#52525b' : '#a1a1aa'} />}
              />
            </View>
          </View>

          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <Feather name="file-text" size={16} color="#10b981" />
              <Text className="text-emerald-500 text-xs font-black uppercase tracking-widest ml-2">
                {t('profile_screen.fields.goals_section_title')}
              </Text>
            </View>
            <View style={styles.fieldGroup}>
              <Input
                label={t('profile_screen.fields.bio')}
                value={data.bio}
                onChangeText={v => onChange('bio', v)}
                placeholder={t('profile_screen.fields.bio_input_placeholder')}
                multiline
                numberOfLines={3}
                style={{ height: 100 }}
              />
              <Input
                label={t('profile_screen.fields.learning_goals')}
                value={data.learning_goals}
                onChangeText={v => onChange('learning_goals', v)}
                placeholder={t('profile_screen.fields.goals_placeholder')}
                multiline
                numberOfLines={3}
                style={{ height: 100 }}
              />
            </View>
          </View>
        </MotiView>

        <View style={styles.actions}>
          <Button 
            label={t('profile_screen.actions.save')} 
            onPress={onSave} 
            loading={loading} 
            fullWidth 
            size="lg"
            className="rounded-3xl h-16"
          />
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  )
}

const styles = StyleSheet.create({
  scroll: { paddingBottom: 60 },
  header: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    justifyContent: 'space-between', 
    paddingHorizontal: 20,
    paddingTop: 20,
    marginBottom: 20
  },
  backBtn: {
    width: 44,
    height: 44,
    borderRadius: 22,
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarSection: {
    alignItems: 'center',
    marginBottom: 32,
  },
  avatarFrame: {
    width: 120,
    height: 120,
    borderRadius: 60,
    borderWidth: 4,
    padding: 4,
    position: 'relative',
  },
  avatar: {
    width: '100%',
    height: '100%',
    borderRadius: 54,
  },
  placeholderAvatar: {
    flex: 1,
    backgroundColor: '#ecfdf5',
    borderRadius: 54,
    alignItems: 'center',
    justifyContent: 'center',
  },
  uploadOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0,0,0,0.4)',
    borderRadius: 60,
    alignItems: 'center',
    justifyContent: 'center',
  },
  editBadge: {
    position: 'absolute',
    bottom: 4,
    right: 4,
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#10b981',
    borderWidth: 3,
    borderColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
  sections: {
    paddingHorizontal: 20,
    gap: 32,
  },
  section: {},
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
    paddingLeft: 4,
  },
  fieldGroup: {
    gap: 20,
  },
  actions: {
    paddingHorizontal: 20,
    marginTop: 40,
  },
})
