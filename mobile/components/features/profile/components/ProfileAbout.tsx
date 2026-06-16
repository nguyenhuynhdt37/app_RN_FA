import React from 'react'
import { View } from 'react-native'
import { Text } from '@/components/ui/Text'
import { useTranslation } from 'react-i18next'
import { User } from '@/src/types/auth'
import { useColorScheme } from 'nativewind'
import { MotiView } from 'moti'
import { MessageSquare, Target, Clock } from 'lucide-react-native'

export function ProfileAbout({ user }: { user: User | null }) {
  const { t } = useTranslation()
  const { colorScheme } = useColorScheme()
  const isDark = colorScheme === 'dark'

  return (
    <View className="px-6 mb-8">
      <MotiView
        from={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 200, type: 'spring' }}
      >
        <View className="flex-row items-center mb-6 ml-3">
          <View className="w-1 h-3 bg-emerald-500 rounded-full mr-3" />
          <Text className="text-zinc-400 dark:text-zinc-500 text-[10px] font-black uppercase tracking-[0.3em]">
            {t('profile_screen.sections.about')}
          </Text>
        </View>
      </MotiView>

      <MotiView
        from={{ opacity: 0, translateY: 20 }}
        animate={{ opacity: 1, translateY: 0 }}
        transition={{ delay: 400, type: 'spring' }}
        className={`p-8 rounded-[48px] border ${isDark ? 'bg-zinc-900/40 border-white/5' : 'bg-white border-zinc-100'}`}
      >
        <View className="relative mb-8">
          <MessageSquare size={24} color="#10b981" className="opacity-10 absolute -top-4 -left-2" />
          <Text className={`text-lg leading-[30px] italic px-4 font-medium ${isDark ? 'text-zinc-300' : 'text-zinc-600'}`}>
            {user?.bio || t('profile_screen.fields.bio_placeholder') || 'Chưa có tiểu sử.'}
          </Text>
        </View>

        <View className={`h-[1px] mx-6 rounded-full ${isDark ? 'bg-white/5' : 'bg-zinc-50'}`} />

        <View className="mt-8">
          <View className="flex-row items-center">
            <View className={`w-10 h-10 rounded-full items-center justify-center ${isDark ? 'bg-emerald-500/10' : 'bg-emerald-50'}`}>
              <Target size={20} color="#10b981" strokeWidth={2.5} />
            </View>
            <Text className="text-zinc-500 dark:text-zinc-400 font-black text-[11px] uppercase tracking-[0.2em] ml-4">
              {t('profile_screen.fields.learning_goals')}
            </Text>
          </View>
          
          <Text className={`text-xl font-black tracking-tight leading-8 mt-4 ${isDark ? 'text-white' : 'text-zinc-900'}`}>
            {user?.learning_goals || '—'}
          </Text>

          <View className={`flex-row items-center self-start px-4 py-2 rounded-full mt-5 border ${isDark ? 'bg-zinc-800/50 border-white/5' : 'bg-zinc-50 border-zinc-100'}`}>
            <Clock size={16} color="#10b981" strokeWidth={2.5} />
            <Text className={`font-black text-[10px] ml-3 uppercase tracking-widest ${isDark ? 'text-zinc-400' : 'text-zinc-600'}`}>
              {user?.daily_goal_minutes} {t('auth.profile.goals.minutes')}
            </Text>
          </View>
        </View>
      </MotiView>
    </View>
  )
}




