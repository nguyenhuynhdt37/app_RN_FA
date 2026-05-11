import React from 'react'
import { View, StyleSheet } from 'react-native'
import { Text } from '@/components/ui/Text'
import { Feather, Ionicons } from '@expo/vector-icons'
import { useTranslation } from 'react-i18next'
import { User } from '@/src/types/auth'
import { useColorScheme } from 'nativewind'
import { MotiView } from 'moti'

export function ProfileAbout({ user }: { user: User | null }) {
  const { t } = useTranslation()
  const { colorScheme } = useColorScheme()
  const isDark = colorScheme === 'dark'

  return (
    <View style={styles.container}>
      <MotiView
        from={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 200, type: 'timing' }}
      >
        <Text style={{ color: '#10b981' }} className="text-xs font-black uppercase tracking-[0.2em] mb-4 ml-1">
          {t('profile_screen.sections.about')}
        </Text>
      </MotiView>

      <MotiView
        from={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 300, type: 'timing' }}
        style={[styles.card, { backgroundColor: isDark ? '#18181b' : '#fff' }]}
      >
        <View style={styles.quoteBox}>
          <Ionicons name="chatbubble-ellipses-outline" size={24} color="#10b981" style={{ opacity: 0.1, position: 'absolute', top: -10, left: -5 }} />
          <Text style={{ color: isDark ? '#d4d4d8' : '#52525b' }} className="text-lg leading-relaxed italic px-4">
            {user?.bio || t('profile_screen.fields.bio_placeholder') || 'Chưa có tiểu sử.'}
          </Text>
        </View>

        <View style={[styles.divider, { backgroundColor: isDark ? '#27272a' : '#f4f4f5' }]} />

        <View style={styles.goalsSection}>
          <View style={styles.goalHeader}>
            <View style={styles.goalIcon}>
              <Ionicons name="compass" size={18} color="#10b981" />
            </View>
            <Text className="text-zinc-500 font-black text-[10px] uppercase tracking-widest ml-3">
              {t('profile_screen.fields.learning_goals')}
            </Text>
          </View>
          
          <Text style={{ color: isDark ? '#fff' : '#09090b' }} className="text-xl font-black tracking-tight leading-7 mt-3">
            {user?.learning_goals || '—'}
          </Text>

          <View style={styles.goalPill}>
            <Ionicons name="time" size={14} color="#10b981" />
            <Text className="text-emerald-500 font-bold text-xs ml-2">
              {user?.daily_goal_minutes} {t('auth.profile.goals.minutes')}
            </Text>
          </View>
        </View>
      </MotiView>
    </View>
  )
}

const styles = StyleSheet.create({
  container: { paddingHorizontal: 24, marginBottom: 30 },
  card: { borderRadius: 36, padding: 24, elevation: 4, shadowColor: '#000', shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.05, shadowRadius: 10 },
  quoteBox: { position: 'relative', marginBottom: 20 },
  divider: { height: 1, marginVertical: 4, borderRadius: 1 },
  goalsSection: { marginTop: 20 },
  goalHeader: { flexDirection: 'row', alignItems: 'center' },
  goalIcon: { width: 32, height: 32, borderRadius: 10, backgroundColor: 'rgba(16,185,129,0.1)', alignItems: 'center', justifyContent: 'center' },
  goalPill: { flexDirection: 'row', alignItems: 'center', backgroundColor: 'rgba(16,185,129,0.08)', alignSelf: 'flex-start', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 12, marginTop: 12 },
})
