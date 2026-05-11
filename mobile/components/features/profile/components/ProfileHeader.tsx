import React from 'react'
import { View, Pressable, ActivityIndicator, StyleSheet, Image, Dimensions } from 'react-native'
import { Text } from '@/components/ui/Text'
import { Feather, Ionicons } from '@expo/vector-icons'
import { User } from '@/src/types/auth'
import { useColorScheme } from 'nativewind'
import { LinearGradient } from 'expo-linear-gradient'
import { MotiView } from 'moti'
import { useSafeAreaInsets } from 'react-native-safe-area-context'

const { width } = Dimensions.get('window')

interface Props {
  user: User | null
  onPickImage: () => void
  uploading: boolean
}

export function ProfileHeader({ user, onPickImage, uploading }: Props) {
  const { colorScheme } = useColorScheme()
  const insets = useSafeAreaInsets()
  const isDark = colorScheme === 'dark'
  const initials = (user?.full_name?.[0] || 'U').toUpperCase()

  return (
    <View style={styles.container}>
      {/* Banner Background */}
      <View style={[styles.bannerContainer, { height: 180 + insets.top }]}>
        <LinearGradient
          colors={isDark ? ['#10b981', '#064e3b'] : ['#34d399', '#10b981']}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={styles.banner}
        />
        <View style={styles.meshCircle} />

        {/* Floating Controls */}
        <View style={[styles.controls, { top: insets.top + 10 }]}>
          <View style={[styles.glassBtn, { backgroundColor: isDark ? 'rgba(0,0,0,0.3)' : 'rgba(255,255,255,0.4)' }]}>
            <Ionicons name="settings-outline" size={20} color="white" />
          </View>
          <View style={styles.rightControls}>
            <View style={[styles.glassBtn, { backgroundColor: isDark ? 'rgba(0,0,0,0.3)' : 'rgba(255,255,255,0.4)' }]}>
              <Ionicons name="notifications-outline" size={20} color="white" />
            </View>
          </View>
        </View>
      </View>

      <View style={styles.content}>
        <MotiView 
          from={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ type: 'timing', duration: 400 }}
          style={styles.avatarWrapper}
        >
          {/* Static Dashed Ring */}
          <View style={[styles.avatarHalo, { borderColor: isDark ? '#10b981' : '#fff' }]} />
          
          <Pressable onPress={onPickImage} style={[styles.avatarContainer, { shadowColor: isDark ? '#000' : '#10b981' }]}>
            {user?.avatar_url ? (
              <Image source={{ uri: user.avatar_url }} style={styles.avatar} />
            ) : (
              <View style={[styles.avatar, { backgroundColor: isDark ? '#27272a' : '#f4f4f5', alignItems: 'center', justifyContent: 'center' }]}>
                <Text className="text-4xl font-black text-zinc-400 dark:text-zinc-600">{initials}</Text>
              </View>
            )}
            
            {uploading && (
              <View style={styles.uploadOverlay}>
                <ActivityIndicator color="white" />
              </View>
            )}

            <View style={styles.cameraBadge}>
              <Ionicons name="camera" size={16} color="white" />
            </View>
          </Pressable>
        </MotiView>

        <MotiView
          from={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 200, type: 'timing' }}
          style={styles.info}
        >
          <Text style={{ color: isDark ? '#fff' : '#09090b' }} className="text-4xl font-black tracking-tighter">
            {user?.full_name || 'Neural Student'}
          </Text>
          
          <View style={styles.idRow}>
            <Text className="text-zinc-500 font-bold text-lg">@{user?.username || 'user'}</Text>
            <View style={styles.statusDot} />
            <Text className="text-emerald-500 font-black text-xs uppercase tracking-widest">Online</Text>
          </View>

          <View style={styles.badgeRow}>
            <View style={[styles.pillBadge, { backgroundColor: 'rgba(16,185,129,0.1)' }]}>
              <Ionicons name="flash" size={12} color="#10b981" />
              <Text className="text-emerald-600 dark:text-emerald-400 font-bold text-xs ml-1">Pro Member</Text>
            </View>
            <View style={[styles.pillBadge, { backgroundColor: 'rgba(245,158,11,0.1)' }]}>
              <Ionicons name="star" size={12} color="#f59e0b" />
              <Text className="text-amber-600 dark:text-amber-400 font-bold text-xs ml-1">Top Student</Text>
            </View>
          </View>
        </MotiView>
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  container: { marginBottom: 30 },
  bannerContainer: { height: 180, width: '100%', position: 'relative', overflow: 'hidden' },
  banner: { ...StyleSheet.absoluteFillObject },
  meshCircle: { position: 'absolute', width: 200, height: 200, borderRadius: 100, backgroundColor: '#fff', top: -50, right: -50 },
  content: { alignItems: 'center', marginTop: -60 },
  avatarWrapper: { width: 140, height: 140, alignItems: 'center', justifyContent: 'center' },
  avatarHalo: { position: 'absolute', width: 136, height: 136, borderRadius: 68, borderWidth: 2, borderStyle: 'dashed', opacity: 0.5 },
  avatarContainer: { width: 120, height: 120, borderRadius: 60, backgroundColor: '#fff', padding: 5, elevation: 15, shadowOffset: { width: 0, height: 8 }, shadowOpacity: 0.2, shadowRadius: 15 },
  avatar: { width: '100%', height: '100%', borderRadius: 55 },
  uploadOverlay: { ...StyleSheet.absoluteFillObject, borderRadius: 60, backgroundColor: 'rgba(0,0,0,0.4)', alignItems: 'center', justifyContent: 'center' },
  cameraBadge: { position: 'absolute', bottom: 2, right: 2, width: 34, height: 34, borderRadius: 17, backgroundColor: '#10b981', alignItems: 'center', justifyContent: 'center', borderWidth: 4, borderColor: '#fff' },
  info: { alignItems: 'center', marginTop: 16 },
  idRow: { flexDirection: 'row', alignItems: 'center', gap: 8, marginTop: 4 },
  statusDot: { width: 6, height: 6, borderRadius: 3, backgroundColor: '#10b981' },
  badgeRow: { flexDirection: 'row', gap: 8, marginTop: 12 },
  pillBadge: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 99 },
  controls: { position: 'absolute', left: 20, right: 20, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  rightControls: { flexDirection: 'row', gap: 12 },
  glassBtn: { width: 44, height: 44, borderRadius: 22, alignItems: 'center', justifyContent: 'center', borderWidth: 1, borderColor: 'rgba(255,255,255,0.2)' },
})
