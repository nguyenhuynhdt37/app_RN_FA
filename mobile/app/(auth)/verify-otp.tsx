import React from 'react'
import { useLocalSearchParams } from 'expo-router'
import { VerifyOTPFeature } from '@/components/features/auth/VerifyOTPFeature'

export default function VerifyOTPScreen() {
  const { phone, email, purpose, resend_available_in, otp_expires_in } = useLocalSearchParams<{ 
    phone?: string; 
    email?: string; 
    purpose: 'authenticate' | 'reset_password';
    resend_available_in?: string;
    otp_expires_in?: string;
  }>()
  
  const identifier = email || phone
  if (!identifier || !purpose) return null

  return (
    <VerifyOTPFeature 
      identifier={identifier} 
      purpose={purpose} 
      initialResendCooldown={resend_available_in ? parseInt(resend_available_in) : 60}
      initialOtpExpiry={otp_expires_in ? parseInt(otp_expires_in) : 300}
    />
  )
}
