import React, { useRef } from 'react'
import { View, Pressable, Animated, Image, StyleSheet } from 'react-native'
import { Text } from '@/components/ui'
import { Feather } from '@expo/vector-icons'
import * as Haptics from 'expo-haptics'
import { cn } from '@/src/lib/utils'
import { useAuthStore } from '@/src/stores/auth.store'

export function HomeHeader() {
  const user = useAuthStore((state) => state.user)
  const firstName = user?.full_name?.split(' ')[0] || 'Bạn'

  return (
    <View style={styles.header}>
      <View style={styles.left}>
        <View style={styles.avatarWrapper}>
          {/* Decorative Background Ring */}
          <View style={styles.avatarRing} />
          
          <View style={styles.avatarContainer}>
            {user?.avatar_url ? (
              <Image 
                source={{ uri: user.avatar_url }} 
                style={styles.avatar}
                resizeMode="cover"
              />
            ) : (
              <View style={styles.placeholderAvatar}>
                <Feather name="smile" size={26} color="#10b981" />
              </View>
            )}
          </View>
          
          {/* Status Badge */}
          <View style={styles.statusBadge}>
            <View style={styles.statusDot} />
          </View>
        </View>

        <View style={styles.textGroup}>
          <Text style={styles.greeting}>Chào buổi sáng 👋</Text>
          <Text style={styles.name} numberOfLines={1}>
            {firstName}
          </Text>
        </View>
      </View>

      <View style={styles.right}>
        <HeaderButton icon="search" />
        <HeaderButton icon="bell" hasDot />
      </View>
    </View>
  )
}

function HeaderButton({ icon, hasDot }: { icon: keyof typeof Feather.glyphMap; hasDot?: boolean }) {
  const scaleAnim = useRef(new Animated.Value(1)).current

  const handlePressIn = () => {
    Animated.spring(scaleAnim, {
      toValue: 0.9,
      useNativeDriver: true,
      speed: 40,
      bounciness: 10,
    }).start()
  }

  const handlePressOut = () => {
    Animated.spring(scaleAnim, {
      toValue: 1,
      useNativeDriver: true,
      speed: 40,
      bounciness: 10,
    }).start()
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
        style={({ pressed }) => [
          styles.btn,
          { backgroundColor: pressed ? 'rgba(16,185,129,0.15)' : 'rgba(16,185,129,0.08)' }
        ]}
      >
        <Feather name={icon} size={22} color="#10b981" />
        {hasDot && <View style={styles.btnDot} />}
      </Pressable>
    </Animated.View>
  )
}

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 24,
    paddingTop: 20,
    paddingBottom: 10,
  },
  left: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  avatarWrapper: {
    position: 'relative',
    width: 60,
    height: 60,
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarRing: {
    position: 'absolute',
    width: 58,
    height: 58,
    borderRadius: 29,
    borderWidth: 1.5,
    borderColor: '#10b981',
    opacity: 0.15,
  },
  avatarContainer: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#ecfdf5',
    overflow: 'hidden',
    borderWidth: 2,
    borderColor: '#fff',
  },
  avatar: {
    width: '100%',
    height: '100%',
  },
  placeholderAvatar: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  statusBadge: {
    position: 'absolute',
    bottom: 2,
    right: 2,
    width: 18,
    height: 18,
    borderRadius: 9,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  statusDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: '#10b981',
  },
  textGroup: {
    marginLeft: 14,
    justifyContent: 'center',
  },
  greeting: {
    fontSize: 13,
    fontWeight: '600',
    color: '#71717a',
    marginBottom: -2,
  },
  name: {
    fontSize: 22,
    fontWeight: '900',
    color: '#09090b',
    letterSpacing: -0.5,
  },
  right: {
    flexDirection: 'row',
    gap: 10,
  },
  btn: {
    width: 48,
    height: 48,
    borderRadius: 24,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: 'rgba(16,185,129,0.1)',
  },
  btnDot: {
    position: 'absolute',
    top: 12,
    right: 12,
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#ef4444',
    borderWidth: 1.5,
    borderColor: '#fff',
  },
})
