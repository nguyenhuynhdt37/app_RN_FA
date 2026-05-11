import React from 'react'
import { View, Pressable, StyleSheet } from 'react-native'
import { Text } from '@/components/ui/Text'
import { Feather, Ionicons } from '@expo/vector-icons'
import * as Haptics from 'expo-haptics'
import { useTranslation } from 'react-i18next'
import { useColorScheme } from 'nativewind'
import { MotiView } from 'moti'

const SECTIONS = [
  {
    title: 'account',
    items: [
      { icon: 'person-outline', color: '#3b82f6', key: 'edit_profile', action: 'edit' },
      { icon: 'shield-checkmark-outline', color: '#10b981', key: 'sections.settings', action: 'security' },
    ]
  },
  {
    title: 'preferences',
    items: [
      { icon: 'notifications-outline', color: '#f59e0b', key: 'notifications', action: 'notifications' },
      { icon: 'language-outline', color: '#8b5cf6', key: 'language', action: 'language' },
    ]
  },
  {
    title: 'support',
    items: [
      { icon: 'help-circle-outline', color: '#f43f5e', key: 'help', action: 'help' },
      { icon: 'information-circle-outline', color: '#64748b', key: 'about_app', action: 'about' },
    ]
  }
]

export function ProfileActions({ onEdit }: { onEdit: () => void }) {
  const { t } = useTranslation()
  const { colorScheme } = useColorScheme()
  const isDark = colorScheme === 'dark'

  const handlers: Record<string, () => void> = { edit: onEdit }

  return (
    <View style={styles.container}>
      {SECTIONS.map((section, sIdx) => (
        <MotiView
          key={section.title}
          from={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 500 + sIdx * 100, type: 'timing' }}
          style={styles.section}
        >
          <Text style={{ color: '#10b981' }} className="text-xs font-black uppercase tracking-[0.2em] mb-4 ml-1">
            {t(`profile_screen.sections.${section.title}`)}
          </Text>
          
          <View style={[styles.card, { backgroundColor: isDark ? '#18181b' : '#fff' }]}>
            {section.items.map((item, iIdx) => (
              <React.Fragment key={item.key}>
                <Pressable
                  onPress={() => { Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); handlers[item.action]?.() }}
                  style={styles.row}
                >
                  <View style={[styles.iconBox, { backgroundColor: item.color + '10' }]}>
                    <Ionicons name={item.icon as any} size={20} color={item.color} />
                  </View>
                  <Text style={{ color: isDark ? '#fff' : '#09090b', flex: 1 }} className="text-lg font-bold tracking-tight">
                    {t(`profile_screen.${item.key}`)}
                  </Text>
                  <Ionicons name="chevron-forward" size={18} color={isDark ? '#3f3f46' : '#d4d4d8'} />
                </Pressable>
                {iIdx < section.items.length - 1 && (
                  <View style={[styles.divider, { backgroundColor: isDark ? '#27272a' : '#f4f4f5' }]} />
                )}
              </React.Fragment>
            ))}
          </View>
        </MotiView>
      ))}
    </View>
  )
}

const styles = StyleSheet.create({
  container: { paddingHorizontal: 24, marginBottom: 50 },
  section: { marginBottom: 30 },
  card: { borderRadius: 36, overflow: 'hidden', elevation: 4, shadowColor: '#000', shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.05, shadowRadius: 10 },
  row: { flexDirection: 'row', alignItems: 'center', gap: 16, padding: 18 },
  iconBox: { width: 44, height: 44, borderRadius: 14, alignItems: 'center', justifyContent: 'center' },
  divider: { height: 1, marginHorizontal: 20 },
})
