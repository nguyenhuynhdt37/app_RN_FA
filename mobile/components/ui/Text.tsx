import React from 'react'
import { Text as RNText, type TextProps } from 'react-native'
import { cn } from '@/src/lib/utils'

interface TypographyProps extends TextProps {
  className?: string
  children: React.ReactNode
}

export function H1({ className, ...props }: TypographyProps) {
  return <RNText className={cn("text-3xl font-extrabold text-foreground tracking-tight", className)} {...props} />
}

export function H2({ className, ...props }: TypographyProps) {
  return <RNText className={cn("text-2xl font-bold text-foreground", className)} {...props} />
}

export function H3({ className, ...props }: TypographyProps) {
  return <RNText className={cn("text-xl font-bold text-foreground", className)} {...props} />
}

export function H4({ className, ...props }: TypographyProps) {
  return <RNText className={cn("text-base font-semibold text-foreground", className)} {...props} />
}

export function BodyText({ className, ...props }: TypographyProps) {
  return <RNText className={cn("text-base font-sans text-foreground leading-6", className)} {...props} />
}

export function SmallText({ className, ...props }: TypographyProps) {
  return <RNText className={cn("text-sm font-sans text-foreground", className)} {...props} />
}

export function MutedText({ className, ...props }: TypographyProps) {
  return <RNText className={cn("text-sm font-sans text-muted-foreground", className)} {...props} />
}

export function LabelText({ className, ...props }: TypographyProps) {
  return <RNText className={cn("text-[11px] font-bold text-muted-foreground uppercase tracking-widest", className)} {...props} />
}

export function CaptionText({ className, ...props }: TypographyProps) {
  return <RNText className={cn("text-xs font-sans text-muted-foreground", className)} {...props} />
}

export function Text({ className, ...props }: TypographyProps) {
  return <RNText className={cn("text-foreground font-sans", className)} {...props} />
}
