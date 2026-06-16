export interface SkillInfo {
  id: string
  name: string
  name_en: string
  name_vi: string
}

export interface UserSpecialization {
  specialization_id: string
  name: string
  name_en: string
  name_vi: string
  level: string
  level_label: string
  skill_ids: string[]
  skills: SkillInfo[]
}

export interface UserProfileSummary {
  full_name: string | null
  avatar_url: string | null
  username: string | null
}

export interface User {
  id: string
  phone: string | null
  email: string | null
  full_name: string | null
  username: string | null
  bio: string | null
  is_profile_completed: boolean
  specializations: UserSpecialization[]
  interest_ids: string[]
  interests: SkillInfo[]
  learning_goals: string | null
  daily_goal_minutes: number
  preferred_learning_style: string | null
  social_links: Record<string, string>
  avatar_url: string | null
  cover_url: string | null
  status: 'ACTIVE' | 'BLOCKED' | 'PENDING'
  is_verified: boolean
  roles: string[]
  created_at: string
  last_login_at: string | null
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  session_id: string
}

export interface Session {
  id: string
  device_type: 'IOS' | 'ANDROID' | 'WEB'
  device_name: string | null
  ip_address: string | null
  user_agent: string | null
  last_used_at: string | null
  created_at: string
  is_current: boolean
}

export interface OtpVerifyResponse {
  verified: boolean
  otp_token: string
  phone: string | null
  email: string | null
  message: string
}

export interface ApiError {
  status_code: number
  code: string
  detail: string
}

// Auth flow state — shared between OTP screens
export type AuthPurpose = 'authenticate' | 'reset_password'

export interface OtpFlowParams {
  phone?: string
  email?: string
  purpose: AuthPurpose
  otp_token?: string
}
