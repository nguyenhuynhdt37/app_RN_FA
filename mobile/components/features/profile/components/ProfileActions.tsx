import React from 'react'
import { View, Pressable } from 'react-native'
import { Text } from '@/components/ui/Text'
import { useRouter } from 'expo-router'
import * as Haptics from 'expo-haptics'
import { useTranslation } from 'react-i18next'
import { useColorScheme } from 'nativewind'
import { MotiView } from 'moti'
import { User, Shield, Bell, Languages, HelpCircle, Info, ChevronRight } from 'lucide-react-native'
import { LinearGradient } from 'expo-linear-gradient'

const SECTIONS = [
  {
    title: 'account',
    items: [
      { Icon: User, key: 'edit_profile', action: 'edit' },
      { Icon: Shield, key: 'sections.settings', action: 'security' },
    ]
  },
  {
    title: 'preferences',
    items: [
      { Icon: Bell, key: 'notifications', action: 'notifications' },
      { Icon: Languages, key: 'language', action: 'language' },
    ]
  },
  {
    title: 'support',
    items: [
      { Icon: HelpCircle, key: 'help', action: 'help' },
      { Icon: Info, key: 'about_app', action: 'about' },
    ]
  }
]

export function ProfileActions({ onEdit }: { onEdit: () => void }) {
  const { t } = useTranslation()
  const { colorScheme } = useColorScheme()
  const router = useRouter()
  const isDark = colorScheme === 'dark'

  const handlers: Record<string, () => void> = { 
    edit: onEdit,
    security: () => router.push('/settings'),
    language: () => router.push('/(app)/language' as any)
  }

  return (
    <View className="px-6 mb-[100px]">
      {SECTIONS.map((section, sIdx) => (
        <MotiView
          key={section.title}
          from={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 500 + sIdx * 100, type: 'spring' }}
          className="mb-10"
        >
          <View className="flex-row items-center mb-6 ml-3">
            <View className="w-1 h-3 bg-emerald-500 rounded-full mr-3" />
            <Text className="text-zinc-400 dark:text-zinc-500 text-[10px] font-black uppercase tracking-[0.3em]">
              {t(`profile_screen.sections.${section.title}`)}
            </Text>
          </View>
          
          <View className={`rounded-[48px] overflow-hidden border ${isDark ? 'bg-zinc-900/40 border-white/5' : 'bg-white border-zinc-100'}`}>
            {section.items.map((item, iIdx) => (
              <React.Fragment key={item.key}>
                <Pressable
                  onPress={() => { 
                    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium); 
                    if (handlers[item.action]) {
                      handlers[item.action]();
                    }
                  }}
                >
                  {({ pressed }) => (
                    <MotiView
                      animate={{
                        scale: pressed ? 0.98 : 1,
                        backgroundColor: pressed 
                          ? (isDark ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.02)') 
                          : 'transparent'
                      }}
                      className="flex-row items-center gap-5 p-6"
                    >
                      <View className={`w-12 h-12 rounded-full items-center justify-center border ${isDark ? 'bg-emerald-500/10 border-emerald-500/20' : 'bg-emerald-50 bg-zinc-100/50 border-zinc-100'}`}>
                        <item.Icon size={20} color="#10b981" strokeWidth={2.5} />
                      </View>
                      
                      <Text className={`flex-1 text-base font-bold tracking-tight ${isDark ? 'text-zinc-200' : 'text-zinc-800'}`}>
                        {t(`profile_screen.${item.key}`)}
                      </Text>
                      
                      <View className={`w-8 h-8 rounded-full items-center justify-center ${isDark ? 'bg-white/5' : 'bg-zinc-50'}`}>
                        <ChevronRight size={14} color={isDark ? '#52525b' : '#a1a1aa'} strokeWidth={3} />
                      </View>
                    </MotiView>
                  )}
                </Pressable>
                
                {iIdx < section.items.length - 1 && (
                  <View className={`h-[1px] mx-8 ${isDark ? 'bg-white/5' : 'bg-zinc-50'}`} />
                )}
              </React.Fragment>
            ))}
          </View>
        </MotiView>
      ))}
    </View>
  )
}



