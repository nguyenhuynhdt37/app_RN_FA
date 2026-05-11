import React from 'react'
import { View, StyleSheet, Dimensions } from 'react-native'
import { Text } from '@/components/ui/Text'
import { Feather, Ionicons } from '@expo/vector-icons'
import { useTranslation } from 'react-i18next'
import { useColorScheme } from 'nativewind'
import { MotiView } from 'moti'
import { LinearGradient } from 'expo-linear-gradient'

const STATS = [
  { key: 'points', value: '1,240', icon: 'flash' as const, color: '#f59e0b', gradient: ['#fbbf24', '#f59e0b'] },
  { key: 'streak', value: '12', icon: 'flame' as const, color: '#f43f5e', gradient: ['#fb7185', '#f43f5e'] },
  { key: 'courses', value: '5', icon: 'book' as const, color: '#10b981', gradient: ['#34d399', '#10b981'] },
]

export function ProfileStats() {
  const { t } = useTranslation()
  const { colorScheme } = useColorScheme()
  const isDark = colorScheme === 'dark'

  return (
    <View style={styles.container}>
      {/* Level Progress Section */}
      <MotiView
        from={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 200, type: 'timing' }}
        style={[styles.levelCard, { backgroundColor: isDark ? '#18181b' : '#fff' }]}
      >
        <View style={styles.levelHeader}>
          <View style={styles.levelBadge}>
            <Text className="text-white font-black">LV. 12</Text>
          </View>
          <Text style={{ color: isDark ? '#fff' : '#09090b' }} className="text-sm font-bold">
            {t('profile_screen.stats.next_level', { xp: 450 })}
          </Text>
        </View>
        <View style={[styles.progressBarBg, { backgroundColor: isDark ? '#27272a' : '#f4f4f5' }]}>
          <LinearGradient
            colors={['#10b981', '#34d399']}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 0 }}
            style={[styles.progressBarFill, { width: '65%' }]}
          />
        </View>
      </MotiView>

      {/* Main Stats Row */}
      <View style={styles.row}>
        {STATS.map((s, i) => (
          <MotiView
            key={s.key}
            from={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 300 + i * 100, type: 'timing' }}
            style={[styles.card, { backgroundColor: isDark ? '#18181b' : '#fff' }]}
          >
            <LinearGradient
              colors={s.gradient as any}
              style={styles.iconBox}
            >
              <Ionicons name={s.icon as any} size={20} color="white" />
            </LinearGradient>
            <Text style={{ color: isDark ? '#fff' : '#09090b' }} className="text-2xl font-black tracking-tight mt-2">
              {s.value}
            </Text>
            <Text className="text-zinc-500 text-[10px] font-bold uppercase tracking-widest text-center">
              {t(`profile_screen.stats.${s.key}`)}
            </Text>
          </MotiView>
        ))}
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  container: { paddingHorizontal: 24, marginBottom: 30 },
  levelCard: { borderRadius: 32, padding: 20, marginBottom: 16, elevation: 4, shadowColor: '#000', shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.05, shadowRadius: 10 },
  levelHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  levelBadge: { backgroundColor: '#10b981', paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12 },
  progressBarBg: { height: 10, borderRadius: 5, overflow: 'hidden' },
  progressBarFill: { height: '100%', borderRadius: 5 },
  row: { flexDirection: 'row', gap: 12 },
  card: { flex: 1, borderRadius: 32, padding: 16, alignItems: 'center', elevation: 4, shadowColor: '#000', shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.05, shadowRadius: 10 },
  iconBox: { width: 44, height: 44, borderRadius: 16, alignItems: 'center', justifyContent: 'center' },
})
