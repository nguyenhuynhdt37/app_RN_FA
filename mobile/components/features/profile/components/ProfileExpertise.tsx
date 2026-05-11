import React from 'react'
import { View, StyleSheet } from 'react-native'
import { Text } from '@/components/ui/Text'
import { Feather, Ionicons } from '@expo/vector-icons'
import { useTranslation } from 'react-i18next'
import { User, UserSpecialization } from '@/src/types/auth'
import { useColorScheme } from 'nativewind'
import { MotiView } from 'moti'

export function ProfileExpertise({ user }: { user: User | null }) {
  const { t, i18n } = useTranslation()
  const { colorScheme } = useColorScheme()
  const isDark = colorScheme === 'dark'
  const isVI = i18n.language === 'vi'

  if (!user?.specializations?.length) return null

  return (
    <View style={styles.container}>
      <MotiView
        from={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 200, type: 'timing' }}
      >
        <Text style={{ color: '#10b981' }} className="text-xs font-black uppercase tracking-[0.2em] mb-4 ml-1">
          {t('profile_screen.sections.expertise')}
        </Text>
      </MotiView>

      {user.specializations.map((spec: UserSpecialization, i: number) => (
        <MotiView 
          key={i} 
          from={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 300 + i * 100, type: 'timing' }}
          style={[styles.card, { backgroundColor: isDark ? '#18181b' : '#fff' }, i > 0 && { marginTop: 16 }]}
        >
          <View style={styles.top}>
            <View style={styles.iconBox}>
              <Ionicons name="school" size={20} color="#10b981" />
            </View>
            <View style={{ flex: 1, marginLeft: 16 }}>
              <Text style={{ color: isDark ? '#fff' : '#09090b' }} className="text-xl font-black tracking-tight leading-7">
                {isVI ? spec.name_vi : spec.name_en}
              </Text>
              <View style={styles.levelBadge}>
                <Ionicons name="ribbon" size={12} color="#10b981" />
                <Text className="text-emerald-500 font-bold text-xs ml-1">
                  {t(`auth.profile.education.levels.${spec.level}`)}
                </Text>
              </View>
            </View>
          </View>

          {spec.skills && spec.skills.length > 0 && (
            <View style={styles.tags}>
              {spec.skills.map((sk: any, j: number) => (
                <MotiView 
                  key={j} 
                  from={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 400 + j * 50, type: 'timing' }}
                  style={[styles.tag, { backgroundColor: isDark ? 'rgba(16,185,129,0.1)' : 'rgba(16,185,129,0.06)' }]}
                >
                  <Text className="text-emerald-600 dark:text-emerald-400 font-bold text-xs">
                    {isVI ? sk.name_vi : sk.name_en}
                  </Text>
                </MotiView>
              ))}
            </View>
          )}
        </MotiView>
      ))}
    </View>
  )
}

const styles = StyleSheet.create({
  container: { paddingHorizontal: 24, marginBottom: 30 },
  card: { borderRadius: 36, padding: 20, elevation: 4, shadowColor: '#000', shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.05, shadowRadius: 10 },
  top: { flexDirection: 'row', alignItems: 'center' },
  iconBox: { width: 48, height: 48, borderRadius: 18, backgroundColor: 'rgba(16,185,129,0.1)', alignItems: 'center', justifyContent: 'center' },
  levelBadge: { flexDirection: 'row', alignItems: 'center', backgroundColor: 'rgba(16,185,129,0.08)', alignSelf: 'flex-start', paddingHorizontal: 10, paddingVertical: 4, borderRadius: 10, marginTop: 4 },
  tags: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginTop: 20 },
  tag: { paddingHorizontal: 14, paddingVertical: 8, borderRadius: 16, borderWidth: 1, borderColor: 'rgba(16,185,129,0.1)' },
})
