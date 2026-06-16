# NeuralEarn Agent Standards

> Các quy tắc và hướng dẫn cho AI Coding Agents làm việc trên dự án NeuralEarn.

---

## Tổng quan dự án

**NeuralEarn** là nền tảng học tập trực tuyến với 3 platform:

| Platform | Stack | Location |
|---------|-------|----------|
| Backend | FastAPI + PostgreSQL + Redis | `backend/` |
| Mobile | React Native + Expo | `mobile/` |
| Web | Next.js 15 + Tailwind v4 | `web/` |

---

## Cấp độ Rules

### 1. Global Rules (`.cursor/rules/`)
Tất cả agents khi làm việc với project này **PHẢI tuân thủ**:

| Rule | Áp dụng | Mô tả |
|------|---------|--------|
| `general.mdc` | **Tất cả files** | Quy tắc chung |
| `typescript.mdc` | **Tất cả .ts/.tsx** | TypeScript strict typing |
| `ui-design.mdc` | **Tất cả .tsx** | Design system 2026 |

### 2. Contextual Rules (Auto-attach)
Tự động load khi edit files trong thư mục tương ứng:

| Rule | Globs | Mô tả |
|------|-------|--------|
| `backend.mdc` | `backend/**/*.py` | FastAPI conventions |
| `mobile.mdc` | `mobile/**/*` | React Native + Expo |
| `web.mdc` | `web/**/*` | Next.js 15 + Admin |

---

## Skills có sẵn

### Bắt buộc đọc khi cần

| Skill | Khi nào dùng |
|-------|--------------|
| `fastapi-master-2026` | Backend API, database models |
| `modern-ui-2026` | Mobile UI components |
| `neuralearn-admin-ui` | Web admin pages |

### Đọc thêm

| Skill | Mô tả |
|-------|--------|
| `nextjs-architecture-2026` | Next.js App Router patterns |
| `react-native-architecture` | React Native patterns |
| `typescript-expert` | Advanced TypeScript |

---

## Workflow Standards

### 1. Backend Feature (FastAPI)

```
1. Schema (Pydantic V2) → schemas/{module}.py
2. Model (SQLAlchemy 2.0) → models/{module}.py
3. Service (Business Logic) → services/{module}.py
4. Router (Thin Layer) → api/v1/{module}.py
```

**Nguyên tắc**: Router chỉ gọi Service, không chứa business logic.

### 2. Mobile Feature (React Native)

```
1. Feature component → components/features/{feature}/
2. Screen → app/(app)/{feature}/
3. Store (Zustand) → src/stores/{feature}.store.ts
4. Service (API) → src/services/{feature}.service.ts
```

**Nguyên tắc**: Max 150 lines/file. Tách component khi quá lớn.

### 3. Web Admin Feature (Next.js)

```
1. Page (thin) → app/[locale]/(admin)/{module}/page.tsx
2. View → features/admin-{module}/components/{Module}View.tsx
3. Table/Cards → features/admin-{module}/components/{Component}.tsx
```

**Nguyên tắc**: page.tsx chỉ là wrapper, logic trong features/.

---

## Error Handling

### Backend (Python)

```python
class ErrorCodes:
    USER_NOT_FOUND = "USER_NOT_FOUND"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    # ...

raise HTTPException(
    status_code=404,
    detail={"code": ErrorCodes.USER_NOT_FOUND, "message": "..."}
)
```

### Frontend (TypeScript)

```typescript
try {
  await api.post('/auth/login', credentials);
} catch (error) {
  if (error instanceof ApiError) {
    switch (error.code) {
      case 'INVALID_CREDENTIALS':
        showToast(t('errors.invalidCredentials'));
        break;
    }
  }
}
```

---

## Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Variables | camelCase | `userData`, `isLoading` |
| Functions | camelCase | `getUserById` |
| Classes | PascalCase | `UserService` |
| Files (TS) | kebab-case | `user-service.ts` |
| Files (Py) | snake_case | `user_service.py` |
| Tables | snake_case plural | `users`, `course_categories` |
| API endpoints | kebab-case | `/api/v1/course-categories` |

---

## Design System Checklist

Mỗi khi tạo UI component mới:

- [ ] **Icons**: Lucide + Emerald monochrome + `strokeWidth={2.5}`
- [ ] **Cards**: `rounded-[48px]` + Glassmorphism
- [ ] **Buttons**: `rounded-full` + Emerald primary
- [ ] **Inputs**: `rounded-full` + Focus border
- [ ] **Shadows**: Cấm! Dùng border thay thế
- [ ] **Animation**: Spring physics (`type: 'spring'`)
- [ ] **Press**: `scale: 0.98` khi nhấn
- [ ] **i18n**: Không hardcode text

---

## Performance Rules

### Backend
- [ ] 100% async/await cho IO operations
- [ ] Pagination cho list endpoints
- [ ] Redis caching cho expensive queries
- [ ] Connection pooling

### Mobile
- [ ] Images: CDN + WebP + lazy load
- [ ] Lists: `FlashList` hoặc optimized FlatList
- [ ] Memo: `useCallback`, `useMemo`
- [ ] No inline styles

### Web
- [ ] Server Components by default
- [ ] `next/image` cho tất cả images
- [ ] No SWR - dùng `useState` + `useEffect`
- [ ] Streaming với `loading.tsx`

---

## Commit Convention

Format: `type(scope): description`

```
feat(mobile): add profile edit screen
fix(backend): resolve token refresh race condition
refactor(web): extract admin dashboard components
docs(api): add user endpoints documentation
chore(deps): upgrade pydantic to v2.5
```

Types: `feat`, `fix`, `refactor`, `docs`, `chore`, `test`, `perf`

---

## Anti-Patterns

### KHÔNG BAO GIỜ

1. ❌ `any` type trong TypeScript
2. ❌ `requests` library trong async Python
3. ❌ Business logic trong Router (Backend)
4. ❌ Logic trong page.tsx (Web)
5. ❌ File > 150 lines (Mobile)
6. ❌ Hardcoded text (i18n required)
7. ❌ `shadow-*` trong UI components
8. ❌ Console.log trong production
9. ❌ Magic numbers - dùng constants
10. ❌ Dead code - xóa unused

---

## Getting Started

Khi bắt đầu làm việc trên project:

1. Đọc `general.mdc` - hiểu project structure
2. Đọc rule tương ứng với platform đang làm
3. Đọc design system (`ui-design.mdc`)
4. Tham khảo skills liên quan

---

## Questions?

Nếu không chắc chắn về:
- Architecture decision → hỏi lại
- Design system → đọc `ui-design.mdc`
- Backend patterns → đọc `backend.mdc`
- TypeScript → đọc `typescript.mdc`

---

> _"NeuralEarn 2026: Minimalist, Ultra-Rounded, and butter smooth."_
