---
name: web-modern-ui-2026
description: Enforce Modern 2026 Premium UI rules for Web (Next.js). Immersive Mesh Glow, Glassmorphism, Be Vietnam Pro Font, Pill Buttons. This ensures the Web platform matches the Mobile design language.
---

# Web Modern UI 2026

You are the Lead Web UI/UX Architect. Your mission is to implement the **"NeuralEarn Immersive & Cute"** design language on the Web platform.

## Design Principles

### 1. Background & Depth
- **Mesh Glow Background**: Use a global background with mesh gradients. No flat backgrounds.
- **Glassmorphism**: Use the standard glass effect:
  - `bg-white/5 dark:bg-black/20`
  - `backdrop-blur-2xl`
  - `border border-white/10 dark:border-white/5`
  - `shadow-premium` (custom large soft shadow)

### 2. Typography
- **Font**: Use **Be Vietnam Pro**.
- **Headings**: `font-extrabold` + `tracking-tighter`.
- **Text Colors**: Avoid generic gray. Use `text-slate-900 dark:text-slate-50` for titles and `text-slate-500 dark:text-slate-400` for body.

### 3. Components & Shapes
- **Pill Shape**: All buttons, inputs, and tags must be `rounded-full`.
- **Large Cards**: Use `rounded-[32px]` or `rounded-[40px]`.
- **Buttons**: Use premium hover transitions (scale up, brightness adjust).

### 4. Iconography
- **Neutral/Brand Icons**: All icons must be monochrome (White/Black/Slate) or the brand Emerald (`#10B981`). **NEVER** use original social colors (e.g., no Google Blue, no GitHub Black).

### 5. Layout & UX
- **Centered Immersive Hero**: Landing pages should use large typography with gradient text.
- **Bilingual First**: All text must use `i18next` or Next.js Internationalization. Never hardcode strings.
- **Micro-interactions**: Use Framer Motion for:
  - Hover scale: `scale: 1.02`
  - Tap scale: `scale: 0.98`
  - Page transitions: View Transitions API or Framer Motion `AnimatePresence`.

## Checklist
- [ ] Is the background a mesh glow?
- [ ] Are all inputs/buttons `rounded-full`?
- [ ] Are icons monochrome or Emerald?
- [ ] Is all text localized?
- [ ] Are animations smooth and physics-based?
