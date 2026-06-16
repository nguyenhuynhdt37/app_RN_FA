import { api } from './api'
import type { OtpVerifyResponse, TokenResponse, User, Session, UserProfileSummary } from '../types/auth'

export const authService = {
  // ── OTP ────────────────────────────────────────────────────────────────────
  sendOtp: (identifier: string, purpose: 'authenticate' | 'reset_password') => {
    const data = identifier.includes('@') ? { email: identifier, purpose } : { phone: identifier, purpose }
    return api.post('/auth/send-otp', data)
  },

  verifyOtp: (identifier: string, otp_code: string, purpose: 'authenticate' | 'reset_password') => {
    const data = identifier.includes('@') 
      ? { email: identifier, otp_code, purpose } 
      : { phone: identifier, otp_code, purpose }
    return api.post<OtpVerifyResponse>('/auth/verify-otp', data)
  },

  // ── Authenticate ───────────────────────────────────────────────────────────
  authenticate: (otp_token: string, device_token?: string) =>
    api.post<TokenResponse>('/auth/authenticate', {
      otp_token,
      device_type: 'ANDROID',
      device_name: 'NEURALEARN App',
      device_token,
    }),

  loginWithGoogle: (id_token: string, device_token?: string) =>
    api.post<TokenResponse>('/auth/oauth/google', {
      id_token,
      device_type: 'ANDROID',
      device_name: 'NEURALEARN App',
      device_token,
    }),

  // ── Token ──────────────────────────────────────────────────────────────────
  refresh: (refresh_token: string) =>
    api.post<TokenResponse>('/auth/refresh', { refresh_token, device_type: 'ANDROID' }),

  // ── Logout ─────────────────────────────────────────────────────────────────
  logout: (refresh_token: string) =>
    api.post('/auth/logout', { refresh_token, device_type: 'ANDROID' }),

  logoutAll: () => api.post('/auth/logout-all'),

  // ── User ───────────────────────────────────────────────────────────────────
  getMe: () => api.get<User>('/auth/me'),
  getProfileSummary: () => api.get<UserProfileSummary>('/auth/profile-summary'),
  updateProfile: (data: {
    full_name: string
    username: string
    bio?: string
    specializations: Array<{ specialization_id: string; level: string; skill_ids: string[] }>
    learning_goals: string
    interest_ids: string[]
    daily_goal_minutes: number
    preferred_learning_style?: string
    email?: string
    avatar_url?: string
    cover_url?: string
    social_links?: Record<string, string>
  }) => api.patch<User>('/auth/profile', data),

  uploadAvatar: (fileUri: string) => {
    const formData = new FormData()
    const filename = fileUri.split('/').pop() || 'avatar.jpg'
    const match = /\.(\w+)$/.exec(filename)
    const type = match ? `image/${match[1]}` : `image`

    // @ts-ignore
    formData.append('file', {
      uri: fileUri,
      name: filename,
      type,
    })

    return api.post<{ avatar_url: string }>('/auth/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  uploadCover: (fileUri: string) => {
    const formData = new FormData()
    const filename = fileUri.split('/').pop() || 'cover.jpg'
    const match = /\.(\w+)$/.exec(filename)
    const type = match ? `image/${match[1]}` : `image`

    // @ts-ignore
    formData.append('file', {
      uri: fileUri,
      name: filename,
      type,
    })

    return api.post<{ cover_url: string }>('/auth/cover', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  checkUsername: async (username: string) => {
    const response = await api.get<{ available: boolean }>(`/auth/check-username`, {
      params: { username }
    });
    return response.data;
  },

  // ── Sessions ───────────────────────────────────────────────────────────────
  getSessions: () => api.get<{ sessions: Session[]; total: number }>('/auth/sessions'),

  revokeSession: (sessionId: string) => api.delete(`/auth/sessions/${sessionId}`),
}
