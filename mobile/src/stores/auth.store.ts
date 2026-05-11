import { create } from 'zustand'
import * as SecureStore from 'expo-secure-store'
import type { User, TokenResponse } from '../types/auth'
import { authService } from '../services/auth.service'

interface AuthState {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  connectionError: boolean

  // Actions
  initialize: () => Promise<void>
  saveTokens: (tokens: TokenResponse) => Promise<void>
  clearTokens: () => Promise<void>
  refreshUser: () => Promise<void>
  setUser: (user: User) => void
  setConnectionError: (v: boolean) => void
  logout: () => Promise<void>
  bypassLogin: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isLoading: true,
  isAuthenticated: false,
  connectionError: false,

  setConnectionError: (v: boolean) => set({ connectionError: v }),

  initialize: async () => {
    try {
      set({ isLoading: true, connectionError: false })
      const token = await SecureStore.getItemAsync('access_token')
      const cachedUser = await SecureStore.getItemAsync('cached_user')
      
      if (cachedUser) {
        set({ user: JSON.parse(cachedUser), isAuthenticated: !!token })
      }

      if (!token) {
        set({ isLoading: false, isAuthenticated: false, user: null })
        await SecureStore.deleteItemAsync('cached_user')
        return
      }

      // getMe() will trigger the interceptor if 401
      const { data } = await authService.getMe()
      set({ user: data, isAuthenticated: true, connectionError: false })
      await SecureStore.setItemAsync('cached_user', JSON.stringify(data))
    } catch (error: any) {
      // Check for timeout or network error
      const isTimeout = error.code === 'ECONNABORTED' || error.message?.includes('timeout')
      const noResponse = !error.response

      if (isTimeout || noResponse) {
        set({ connectionError: true })
      } else if (error.response?.status === 401 || error.response?.status === 403) {
        await get().clearTokens()
        set({ connectionError: false })
      } else {
        const token = await SecureStore.getItemAsync('access_token')
        set({ isAuthenticated: !!token, connectionError: false })
      }
    } finally {
      set({ isLoading: false })
    }
  },

  saveTokens: async (tokens: TokenResponse) => {
    await SecureStore.setItemAsync('access_token', tokens.access_token)
    await SecureStore.setItemAsync('refresh_token', tokens.refresh_token)
    await SecureStore.setItemAsync('session_id', tokens.session_id)
    // Refresh user info
    try {
      const { data } = await authService.getMe()
      set({ user: data, isAuthenticated: true })
      await SecureStore.setItemAsync('cached_user', JSON.stringify(data))
    } catch {
      set({ isAuthenticated: true })
    }
  },

  clearTokens: async () => {
    await SecureStore.deleteItemAsync('access_token')
    await SecureStore.deleteItemAsync('refresh_token')
    await SecureStore.deleteItemAsync('session_id')
    await SecureStore.deleteItemAsync('cached_user')
    set({ user: null, isAuthenticated: false })
  },

  refreshUser: async () => {
    try {
      const { data } = await authService.getMe()
      set({ user: data })
      await SecureStore.setItemAsync('cached_user', JSON.stringify(data))
    } catch {}
  },
  setUser: (user: User) => {
    set({ user })
    SecureStore.setItemAsync('cached_user', JSON.stringify(user))
  },

  logout: async () => {
    try {
      const rt = await SecureStore.getItemAsync('refresh_token')
      if (rt) await authService.logout(rt)
    } catch {}
    await get().clearTokens()
  },

  bypassLogin: async () => {
    set({
      user: {
        id: 'dev-123',
        full_name: 'Developer Mode',
        roles: ['USER'],
        phone: '0912345678',
        email: null,
        avatar_url: null,
        status: 'ACTIVE',
        is_verified: true,
        created_at: new Date().toISOString(),
        last_login_at: new Date().toISOString()
      },
      isAuthenticated: true,
    })
  },
}))
