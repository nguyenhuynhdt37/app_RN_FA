// NEURALEARN Design System — Dark-first theme
export const Colors = {
  // Brand
  primary: '#7C3AED',        // Violet-600
  primaryLight: '#8B5CF6',   // Violet-500
  primaryDark: '#6D28D9',    // Violet-700
  accent: '#06B6D4',         // Cyan-500 (AI highlight)
  accentGold: '#F59E0B',     // Amber-500 (premium)

  // Backgrounds
  background: '#0A0A0F',     // Near black
  surface: '#12121A',        // Card bg
  surfaceHigh: '#1A1A26',    // Elevated card
  surfaceBorder: '#2A2A3E',  // Border

  // Text
  textPrimary: '#F1F0FF',    // Soft white
  textSecondary: '#9B99B8',  // Muted
  textTertiary: '#5C5A78',   // Very muted

  // Status
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  info: '#3B82F6',

  // Gradient stops
  gradientPurple: ['#7C3AED', '#4F46E5'] as const,
  gradientCyan: ['#06B6D4', '#3B82F6'] as const,
  gradientDark: ['#12121A', '#0A0A0F'] as const,
} as const

export const Spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
} as const

export const Radius = {
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  full: 9999,
} as const

export const Typography = {
  // Font sizes
  xs: 11,
  sm: 13,
  base: 15,
  lg: 17,
  xl: 20,
  '2xl': 24,
  '3xl': 30,
  '4xl': 36,
  // Line heights
  tight: 1.2,
  normal: 1.5,
  loose: 1.8,
} as const

export const Shadow = {
  sm: {
    shadowColor: '#7C3AED',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 3,
  },
  md: {
    shadowColor: '#7C3AED',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.25,
    shadowRadius: 16,
    elevation: 6,
  },
  glow: {
    shadowColor: '#8B5CF6',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.6,
    shadowRadius: 20,
    elevation: 10,
  },
} as const
