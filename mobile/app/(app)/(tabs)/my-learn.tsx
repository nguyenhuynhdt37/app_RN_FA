import { View, Text, StyleSheet } from 'react-native'
import { SafeAreaView } from 'react-native-safe-area-context'
import { Colors, Typography } from '@/src/constants/theme'

export default function MyLearnScreen() {
  return (
    <SafeAreaView style={s.c}>
      <View style={s.center}>
        <Text style={s.icon}>📚</Text>
        <Text style={s.title}>Học của tôi</Text>
        <Text style={s.sub}>Playlist & Progress Tracking{'\n'}Coming soon...</Text>
      </View>
    </SafeAreaView>
  )
}
const s = StyleSheet.create({
  c: { flex: 1, backgroundColor: Colors.background },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', gap: 12 },
  icon: { fontSize: 60 },
  title: { color: Colors.textPrimary, fontSize: Typography['2xl'], fontWeight: '700' },
  sub: { color: Colors.textSecondary, fontSize: Typography.base, textAlign: 'center', lineHeight: 24 },
})
