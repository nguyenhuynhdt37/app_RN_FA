import { create } from 'zustand'

type ColorSchemePreference = 'system' | 'light' | 'dark'

/**
 * Theme store — lưu preference trong memory (không cần AsyncStorage)
 * NativeWind v4 với New Architecture dùng system colorScheme là chính.
 * Manual toggle dùng useColorScheme().setColorScheme() trực tiếp.
 */
export const useThemeStore = create<{
  preference: ColorSchemePreference
  setPreference: (p: ColorSchemePreference) => void
}>((set) => ({
  preference: 'system',
  setPreference: (preference) => set({ preference }),
}))
