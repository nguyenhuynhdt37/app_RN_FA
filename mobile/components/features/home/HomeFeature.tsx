import React from 'react'
import { ScrollView, View } from 'react-native'
import { Screen } from '@/components/layout/Screen'
import { HomeHeader } from './HomeHeader'
import { HomeHero } from './HomeHero'
import { HomeProgress } from './HomeProgress'
import { HomeCourseList } from './HomeCourseList'

export function HomeFeature() {
  return (
    <Screen safeArea withTabBar>
      <ScrollView 
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{ paddingBottom: 100 }}
      >
        <HomeHeader />
        <HomeHero />
        <HomeProgress />
        <HomeCourseList />
        
        {/* Extra spacing for Bottom Tabs if any */}
        <View className="h-10" />
      </ScrollView>
    </Screen>
  )
}

