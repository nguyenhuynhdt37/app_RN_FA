import React, { useState } from 'react'
import { View, TextInput, Text, type TextInputProps, StyleSheet, useColorScheme } from 'react-native'
import { cn } from '@/src/lib/utils'

interface InputProps extends TextInputProps {
  label?: string
  error?: string
  leftSlot?: React.ReactNode
  rightSlot?: React.ReactNode
}

export function Input({ label, error, className, style, ...props }: InputProps) {
  const [focused, setFocused] = useState(false)
  const systemColorScheme = useColorScheme()
  const isDark = systemColorScheme === 'dark'

  return (
    <View style={styles.container}>
      {label && (
        <Text style={[styles.label, { color: isDark ? '#A1A1AA' : '#71717A' }]}>
          {label}
        </Text>
      )}
      
      <View 
        style={[
          styles.inputWrapper,
          { 
            backgroundColor: isDark ? 'rgba(24, 24, 27, 0.7)' : 'rgba(255, 255, 255, 0.7)',
            borderColor: isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
          },
          props.multiline && { height: 'auto', minHeight: 120, borderRadius: 24, alignItems: 'flex-start', paddingTop: 16 },
          focused && { borderColor: '#10B981', backgroundColor: isDark ? '#18181B' : '#FFFFFF' },
          error && { borderColor: '#F43F5E', backgroundColor: isDark ? 'rgba(244, 63, 94, 0.1)' : 'rgba(244, 63, 94, 0.05)' },
        ]}
      >
        {props.leftSlot && (
          <View style={[styles.slot, props.multiline && { marginTop: 4 }]}>
            {props.leftSlot}
          </View>
        )}
        
        <TextInput
          style={[
            styles.input, 
            { color: isDark ? '#FAFAFA' : '#09090B' },
            props.multiline && { height: 'auto', minHeight: 100 },
            style
          ]}
          placeholderTextColor={isDark ? '#52525B' : '#A1A1AA'}
          onFocus={(e) => { setFocused(true); props.onFocus?.(e) }}
          onBlur={(e) => { setFocused(false); props.onBlur?.(e) }}
          {...props}
        />

        {props.rightSlot && (
          <View style={[styles.slot, props.multiline && { marginTop: 4 }]}>
            {props.rightSlot}
          </View>
        )}
      </View>

      {error && (
        <Text style={styles.errorText}>
          {error}
        </Text>
      )}
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    gap: 8,
    width: '100%',
  },
  label: {
    fontWeight: '700',
    fontSize: 14,
    marginLeft: 16,
  },
  inputWrapper: {
    height: 64,
    borderRadius: 32,
    borderWidth: 1,
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    gap: 12,
  },
  slot: {
    width: 24,
    alignItems: 'center',
    justifyContent: 'center',
  },
  input: {
    flex: 1,
    height: '100%',
    fontSize: 18,
  },
  errorText: {
    color: '#F43F5E',
    fontSize: 12,
    fontWeight: '700',
    marginLeft: 24,
    marginTop: 2,
  }
})
