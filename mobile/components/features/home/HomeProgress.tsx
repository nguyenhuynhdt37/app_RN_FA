import React from 'react'
import { View } from 'react-native'
import { Text } from '@/components/ui'
import { Feather } from '@expo/vector-icons'
import { cn } from '@/src/lib/utils'

export function HomeProgress() {
  return (
    <View className="px-5 mb-8">
      <View 
        className={cn(
          "p-7 rounded-[40px] border shadow-2xl shadow-emerald-500/10",
          "bg-white/40 dark:bg-zinc-900/60 backdrop-blur-2xl",
          "border-white/40 dark:border-zinc-800"
        )}
      >
        <View className="flex-row items-center justify-between mb-4">
          <View className="flex-row items-center gap-3">
            <View className="w-10 h-10 rounded-full bg-emerald-500/20 items-center justify-center">
              <Feather name="book-open" size={20} className="text-emerald-500" />
            </View>
            <View>
              <Text className="text-xs font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-widest">
                Đang tiếp tục
              </Text>
              <Text className="text-lg font-extrabold text-zinc-900 dark:text-zinc-50 tracking-tight">
                Clean Architecture
              </Text>
            </View>
          </View>
          <Text className="text-2xl font-black text-emerald-500">65%</Text>
        </View>

        <View className="h-3 bg-zinc-200 dark:bg-zinc-800 rounded-full overflow-hidden">
          <View 
            className="h-full bg-emerald-500 rounded-full" 
            style={{ width: '65%' }} 
          />
        </View>
        
        <View className="flex-row justify-between mt-3">
          <Text className="text-xs font-medium text-zinc-500 dark:text-zinc-400">
            Bài 4: Domain Layer
          </Text>
          <Text className="text-xs font-medium text-zinc-500 dark:text-zinc-400">
            12/18 bài học
          </Text>
        </View>
      </View>
    </View>
  )
}
