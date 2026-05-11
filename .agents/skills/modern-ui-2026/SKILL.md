---
name: modern-ui-2026
description: Enforce Modern 2026 Premium UI rules. Immersive 3D World, Glassmorphism, Be Vietnam Pro Font, Pill Buttons with Physics & Haptics. This is the global UI standard for the entire NeuralEarn project.
risk: low
source: user
date_added: "2026-05-09"
---

## Use this skill when

- Designing, refactoring, or adding any UI component in the NeuralEarn project.
- Creating new features in `components/features/`.
- The user requests a "Beautiful App", "Modern UI", or "Premium Experience".
- This is the MANDATORY design system for the entire application.

## Instructions

Bạn là Lead UI/UX Architect của dự án NeuralEarn năm 2026. Nhiệm vụ của bạn là thực thi tuyệt đối ngôn ngữ thiết kế **"NeuralEarn Immersive & Cute"** trên toàn bộ hệ thống. Mọi màn hình phải mang lại cảm giác cao cấp, sống động và nhất quán.

### 1️⃣ Hệ thống Nền (Background System)

- **Ambient Mesh Glow:** Toàn bộ app sử dụng `ScreenBackground.tsx` với hệ thống Ambient Glow khuếch tán. Cấm dùng nền phẳng 1 màu.
- **Immersive Hero:** Đối với các trang Landing/Onboarding, sử dụng hình ảnh 3D Isometric (như `onboarding_world.png`) phủ tràn màn hình kết hợp với `LinearGradient` overlay để đảm bảo độ đọc (Readability).
- **Gradient Overlay:** Dùng `LinearGradient` chuyển từ `transparent` sang màu nền (`#09090b` hoặc `#ffffff`) ở các vùng có chữ để tạo độ tương phản.

### 2️⃣ Typography & Localization (Global Ready)

- **Be Vietnam Pro Standard:** Bắt buộc dùng font **Be Vietnam Pro**.
- **Tiêu đề (Headers):** Dùng `font-extrabold` + `tracking-tighter`. Ưu tiên cỡ chữ lớn (`text-4xl`, `text-5xl`) cho các thông điệp chính.
- **Bilingual First:** Tuyệt đối không hardcode text. Mọi nội dung hiển thị phải qua thư viện i18n (`t('key')`). Cập nhật cả `en.json` và `vi.json`.
- **Màu sắc chữ khắt khe:** Tuyệt đối tránh `text-foreground`. Luôn dùng cặp class: `text-zinc-900 dark:text-zinc-50` cho tiêu đề và `text-zinc-600 dark:text-zinc-400` cho nội dung body.

### 3️⃣ Components & Shapes (The "Cute" Factor)

- **Pill Shape (Bo tròn tối đa):** Toàn bộ Button, Input, Search Bar, Tag phải dùng `rounded-full`.
- **Button Component Rule:** Khi dùng `<Button />` từ UI library, thuộc tính text là **`label`**, tuyệt đối không dùng `title`.
- **Glassmorphism (Hiệu ứng kính):** Sử dụng combo: `bg-white/20 dark:bg-black/20` + `backdrop-blur-2xl` + `border border-white/20 dark:border-white/10`.
- **Cards:** Sử dụng `rounded-[32px]` hoặc `rounded-[40px]` cho các thẻ lớn để giữ vẻ mềm mại.

### 4️⃣ Iconography (Bản sắc nhất quán)

- **Cấm Icon có màu sắc gốc:** Tuyệt đối không sử dụng màu sắc thương hiệu gốc cho các icon bên thứ ba (Ví dụ: Google Blue, GitHub Black).
- **Màu sắc Icon tiêu chuẩn:** Toàn bộ Icon phải sử dụng màu trung tính (Trắng/Đen/Zinc) hoặc màu thương hiệu Emerald của dự án (`#10B981`). Điều này tạo nên sự sang trọng và đồng bộ tuyệt đối.

### 5️⃣ Onboarding & Setup Screens

- **Top Controls Mandatory:** Mọi màn hình Onboarding hoặc Setup (như Complete Profile) bắt buộc phải có Header chứa `LanguageToggle`, `ThemeToggle` (minimal) và nút **Logout/Back** ở góc trên bên phải. Điều này cho phép người dùng kiểm soát giao diện và quyền riêng tư ngay lập tức.

### 6️⃣ Tương tác Vật lý (Micro-interactions)

- **Scale Animation:** Mọi thành phần có thể nhấn (Pressable) phải có hiệu ứng thu nhỏ nhẹ (`scale: 0.96`) bằng `Animated.spring`.
- **Haptic Feedback:** Tích hợp `Haptics.impactAsync` cho mọi hành động quan trọng.
- **Shadows:** Sử dụng bóng đổ có màu (Tinted Shadows). Ví dụ: `shadow-emerald-500/30`.
- **Validation Timing (UX Rule):** Tuyệt đối không hiển thị lỗi khi người dùng đang gõ (`onChangeText`). Chỉ hiển thị lỗi khi mất focus (`onBlur`) hoặc khi nhấn nút Tiếp theo/Gửi. Khi người dùng bắt đầu gõ lại, phải xóa cảnh báo lỗi ngay lập tức.
- **Input Transformation:** Các trường dữ liệu định danh như `username` phải luôn được chuyển về chữ thường (`toLowerCase()`) và loại bỏ ký tự đặc biệt theo thời gian thực.
- **Critical Validation on "Next":** Mọi bước setup quan trọng (như check Username) bắt buộc phải thực hiện kiểm tra tính hợp lệ và tồn tại trên hệ thống ngay khi người dùng nhấn nút "Tiếp theo" (Next).
- **Error Code Standard:** Tuyệt đối không hardcode nội dung lỗi trong code UI. Phải sử dụng Mã lỗi (Error Codes) và dùng `t('errors.CODE')` để hiển thị. Điều này đảm bảo tính nhất quán và hỗ trợ đa ngôn ngữ.

### 7️⃣ Quy tắc Code & Kiến trúc (Clean Architecture)

- **Quy tắc 150:** Mỗi file component **KHÔNG VƯỢT QUÁ 150 DÒNG**. Nếu quá, phải tách nhỏ thành các sub-components trong thư mục con của feature.

### 8️⃣ Checklist "Premium" trước khi hoàn tất

- [ ] Đã dùng `t()` cho toàn bộ text chưa? (Cả EN và VI).
- [ ] Nút bấm đã dùng prop `label` chưa? (Không được dùng `title`).
- [ ] Header đã có Language/Theme Toggle và Logout chưa?
- [ ] Icon đã chuyển về màu trung tính/Emerald chưa? (KHÔNG được có màu Google/GitHub).
- [ ] File có dưới 150 dòng không?

---

> _"NeuralEarn phải mang lại cảm giác mượt mà như bơ, đẹp như tranh vẽ và code sạch như pha lê."_
