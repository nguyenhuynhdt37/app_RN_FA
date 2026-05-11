import React, { useRef } from 'react'
import { View, Pressable, Animated } from 'react-native'
import { Text } from '@/components/ui'
import { Feather } from '@expo/vector-icons'
import * as Haptics from 'expo-haptics'
import { cn } from '@/src/lib/utils'

const COURSES = [
  { id: '1', title: 'React Native 2026', instructor: 'NeuralEarn', duration: '42:18', tag: 'Mobile' },
  { id: '2', title: 'Advanced Backend', instructor: 'Tech Lead', duration: '28:44', tag: 'Architecture' },
  { id: '3', title: 'UI/UX Masterclass', instructor: 'Design Pro', duration: '15:20', tag: 'Design' },
]

export function HomeCourseList() {
  return (
    <View className="px-5">
      <View className="flex-row justify-between items-end mb-5 px-1">
        <Text className="text-2xl font-extrabold tracking-tighter text-zinc-900 dark:text-zinc-50">
          Khóa học mới
        </Text>
        <Pressable>
          <Text className="text-emerald-500 font-bold text-sm">Xem tất cả</Text>
        </Pressable>
      </View>

      <View className="gap-4">
        {COURSES.map(course => (
          <CourseCard key={course.id} course={course} />
        ))}
      </View>
    </View>
  )
}

function CourseCard({ course }: { course: typeof COURSES[0] }) {
  const scaleAnim = useRef(new Animated.Value(1)).current

  const handlePressIn = () => {
    Animated.spring(scaleAnim, { toValue: 0.96, useNativeDriver: true }).start()
  }

  const handlePressOut = () => {
    Animated.spring(scaleAnim, { toValue: 1, useNativeDriver: true }).start()
  }

  const handlePress = () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light)
  }

  return (
    <Animated.View style={{ transform: [{ scale: scaleAnim }] }}>
      <Pressable
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
        onPress={handlePress}
        className={cn(
          "p-6 rounded-[40px] flex-row items-center gap-5 border",
          "bg-white dark:bg-zinc-900/60 shadow-lg shadow-black/5",
          "border-zinc-100 dark:border-zinc-800"
        )}
      >
        <View className="w-16 h-16 rounded-[24px] bg-emerald-500/10 items-center justify-center">
          <Feather name="play-circle" size={32} className="text-emerald-500" />
        </View>
        <View className="flex-1">
          <View className="flex-row items-center gap-2 mb-1.5">
            <View className="px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20">
              <Text className="text-[9px] font-black text-emerald-600 dark:text-emerald-400 uppercase tracking-widest">
                {course.tag}
              </Text>
            </View>
          </View>
          <Text className="text-xl font-extrabold text-zinc-900 dark:text-zinc-50 tracking-tighter leading-tight mb-1">
            {course.title}
          </Text>
          <Text className="text-xs font-bold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider">
            {course.instructor} • {course.duration}
          </Text>
        </View>
        <Feather name="chevron-right" size={20} className="text-zinc-300 dark:text-zinc-700" />
      </Pressable>
    </Animated.View>
  )
}
