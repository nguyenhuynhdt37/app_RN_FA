import React from 'react'
import { Stack } from 'expo-router'

export default function AppLayout() {
  return (
    <Stack screenOptions={{ headerShown: false }}>
      <Stack.Screen name="(tabs)" />
      <Stack.Screen 
        name="complete-profile" 
        options={{ 
          gestureEnabled: false, // Ngăn vuốt ngược khi đang làm profile
        }} 
      />
    </Stack>
  )
}