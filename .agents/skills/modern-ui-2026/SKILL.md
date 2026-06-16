---
name: modern-ui-2026
description: Enforce Modern 2026 Premium UI rules. Minimalist 3D, Ultra-Rounded (rounded-[48px]), Lucide Icons, Monochromatic Emerald Palette. This is the global UI standard for the entire NeuralEarn project.
risk: low
source: user
date_added: "2026-05-12"
---

## Use this skill when

- Designing, refactoring, or adding any UI component in the NeuralEarn project.
- Creating new features in `components/features/`.
- The user requests a "Beautiful App", "Modern UI", or "Premium Experience".
- This is the MANDATORY design system for the entire application.

## Instructions

Bạn là Lead UI/UX Architect của dự án NeuralEarn năm 2026. Nhiệm vụ của bạn là thực thi tuyệt đối ngôn ngữ thiết kế **"NeuralEarn Minimalist & Rounded"** trên toàn bộ hệ thống. Mọi màn hình phải mang lại cảm giác cực kỳ tối giản, bo tròn mềm mại và cao cấp.

### 1️⃣ Hệ thống Nền & Màu sắc (Minimalist Palette)

- **Monochromatic Rule:** Tuyệt đối tránh sử dụng quá nhiều màu sắc sặc sỡ trong cùng một vùng nhìn. Chỉ sử dụng màu thương hiệu **Emerald Green (#10B981)** kết hợp với thang đo **Zinc/Neutral**.
- **Ambient Mesh Glow:** Toàn bộ app sử dụng `ScreenBackground.tsx`. Cấm dùng nền phẳng 1 màu.
- **Glassmorphism:** Sử dụng combo: `bg-white/40 dark:bg-zinc-900/40` + `backdrop-blur-xl` + `border border-zinc-100 dark:border-white/5`.

### 2️⃣ Typography & Localization

- **Be Vietnam Pro Standard:** Bắt buộc dùng font **Be Vietnam Pro**.
- **Headers:** Dùng `font-black` + `tracking-tighter`. Màu tiêu đề: `text-zinc-900 dark:text-zinc-100`.
- **Bilingual First:** Tuyệt đối không hardcode text. Phải qua `t('key')`. Cập nhật cả `en.json` và `vi.json`.

### 3️⃣ Components & Shapes (Ultra-Rounded)

- **Pill Shape (Bo tròn tối đa):** Toàn bộ Button, Input, Icon Container nhỏ phải dùng `rounded-full`.
- **Extreme Rounding (Cards):** Các thẻ (Cards) lớn bắt buộc dùng **`rounded-[48px]`**. Tuyệt đối không dùng các bo góc sắc cạnh hoặc bo nhẹ (`rounded-xl`).
- **Pill Tags:** Các nhãn hoặc tag kỹ năng phải dùng `rounded-full`.

### 4️⃣ Iconography (Lucide Standard)

- **Lucide Icons Only:** Ưu tiên tuyệt đối thư viện **Lucide** (`lucide-react-native`). Hạn chế dùng Ionicons trừ khi không có lựa chọn thay thế.
- **Monochrome Icons:** Icon phải có màu **Emerald (#10B981)** hoặc Zinc. Tuyệt đối cấm icon nhiều màu (Multi-color).
- **Stroke Width:** Luôn dùng `strokeWidth={2.5}` hoặc `strokeWidth={2}` để icon trông thanh mảnh và cao cấp.

### 5️⃣ Tương tác Vật lý & 3D (Flat-Minimalist Look)

- **Shadows Forbidden (Cấm dùng bóng đổ):** Tuyệt đối không sử dụng `shadow-*` hoặc các thuộc tính liên quan đến bóng đổ. Giao diện phải hoàn toàn phẳng (Flat) nhưng vẫn có chiều sâu thông qua các lớp (Layering).
- **Border Hierarchy:** Dùng viền siêu mỏng (`border-zinc-100` hoặc `border-white/5`) để phân tách các thành phần thay vì dùng bóng đổ.
- **Spring Physics:** Mọi hoạt ảnh chuyển động phải dùng `type: 'spring'`.
- **Scale Interaction:** Thành phần Pressable phải có `scale: 0.98` khi nhấn + Haptic Feedback.

### 6️⃣ Quy tắc Code & UX

- **Quy tắc 150:** Mỗi file component **KHÔNG VƯỢT QUÁ 150 DÒNG**.
- **Validation Timing:** Chỉ hiển thị lỗi khi `onBlur`. Xóa lỗi ngay khi `onChangeText`.
- **Error Code Standard:** Dùng mã lỗi và `t('errors.CODE')`.

### 7️⃣ Checklist "Premium"

- [ ] Đã dùng Lucide icons chưa?
- [ ] Các thẻ đã bo góc `rounded-[48px]` chưa?
- [ ] Icon container có `rounded-full` không?
- [ ] Toàn bộ màu sắc có tối giản (Emerald/Zinc) không? (Cấm multi-color).
- [ ] Đã dùng `type: 'spring'` cho Moti chưa?

---

> _"NeuralEarn 2026: Minimalist, Ultra-Rounded, and butter smooth."_

