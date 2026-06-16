---
name: neuralearn-admin-ui
description: >
  Chuẩn hóa toàn bộ giao diện Admin cho NeuralEarn Web (Next.js 15 + Tailwind v4).
  Sử dụng khi: tạo trang admin mới, sửa layout, thêm bảng CRUD, thêm chart, thêm modal.
  Áp dụng design system emerald/dark, clean code không SWR, dùng recharts.
---

# NeuralEarn Admin UI — Agent Skill

## Phạm vi

Skill này điều hành toàn bộ công việc liên quan đến Admin Interface trong `web/src/app/[locale]/(admin)/` và `web/src/components/admin/`.

---

## Stack

| Layer | Tech |
|---|---|
| Framework | Next.js 15 App Router |
| Styling | Tailwind CSS v4 |
| Charts | recharts |
| State | useState / useEffect (NO SWR, NO TanStack Query) |
| Icons | lucide-react (monochrome only) |
| Animation | framer-motion (micro-interactions) |
| I18n | next-intl |
| Font | Be Vietnam Pro |

---

## Kiến trúc thư mục (FSD-Light)

> **Quy tắc vàng**: `page.tsx` chỉ là thin wrapper — không chứa logic, không chứa JSX phức tạp.
> Toàn bộ logic, state, components phải nằm trong `features/`.

```
web/src/
├── app/[locale]/(admin)/
│   ├── layout.tsx               ← server layout (nhẹ)
│   ├── layout-client.tsx        ← sidebar + header collapse state
│   ├── dashboard/page.tsx       ← chỉ: import DashboardView; export default DashboardView;
│   ├── users/page.tsx           ← chỉ: import UsersView; export default UsersView;
│   ├── lecturers/page.tsx
│   ├── categories/page.tsx
│   ├── topics/page.tsx
│   ├── roles/page.tsx
│   ├── wallets/page.tsx
│   ├── transactions/page.tsx
│   ├── discounts/page.tsx
│   ├── refunds/page.tsx
│   ├── withdraws/page.tsx
│   ├── notifications/page.tsx
│   └── settings/page.tsx
│
├── features/                    ← TẤT CẢ logic ở đây (FSD)
│   ├── admin-dashboard/
│   │   ├── components/
│   │   │   ├── DashboardView.tsx    ← root client component (state, layout)
│   │   │   ├── StatCard.tsx
│   │   │   ├── RevenueChart.tsx
│   │   │   ├── CategoryChart.tsx
│   │   │   ├── TopCoursesTable.tsx
│   │   │   └── TopInstructorsTable.tsx
│   │   └── types.ts
│   ├── admin-users/
│   │   ├── components/
│   │   │   ├── UsersView.tsx        ← root client component
│   │   │   ├── UsersTable.tsx
│   │   │   ├── UserFilters.tsx
│   │   │   ├── StatusBadge.tsx
│   │   │   └── BanModal.tsx
│   │   └── types.ts
│   ├── admin-categories/
│   │   └── components/
│   │       ├── CategoriesView.tsx
│   │       └── CategoryCard.tsx
│   ├── admin-topics/
│   │   └── components/
│   │       ├── TopicsView.tsx
│   │       └── TopicCard.tsx
│   ├── admin-lecturers/
│   │   └── components/
│   │       ├── LecturersView.tsx
│   │       └── LecturerCard.tsx
│   ├── admin-transactions/
│   │   └── components/
│   │       └── TransactionsView.tsx
│   ├── admin-wallets/
│   │   └── components/
│   │       └── WalletsView.tsx
│   ├── admin-discounts/
│   │   └── components/
│   │       ├── DiscountsView.tsx
│   │       └── DiscountCard.tsx
│   ├── admin-refunds/
│   │   └── components/
│   │       └── RefundsView.tsx
│   ├── admin-withdraws/
│   │   └── components/
│   │       └── WithdrawsView.tsx
│   ├── admin-notifications/
│   │   └── components/
│   │       └── NotificationsView.tsx
│   ├── admin-settings/
│   │   └── components/
│   │       └── SettingsView.tsx
│   └── admin-roles/
│       └── components/
│           └── RolesView.tsx
│
├── components/admin/
│   ├── sidebar.tsx              ← layout component
│   └── header.tsx              ← layout component
└── types/admin.ts              ← shared types
```

### Convention đặt tên
- **View**: Root component của feature (có state, layout), ví dụ: `DashboardView.tsx`
- **Card**: Component hiển thị 1 item trong grid, ví dụ: `CategoryCard.tsx`
- **Table**: Component bảng data, ví dụ: `UsersTable.tsx`
- **Modal**: Component dialog, ví dụ: `BanModal.tsx`
- **Filters**: Component thanh lọc, ví dụ: `UserFilters.tsx`

---

## Design System Tokens

### Colors
```
Primary / Accent: emerald-500 (#10b981)
Dark Sidebar: #0b0c14
Light Background: #f8fafc
Card BG: white (light) / slate-900 (dark)
Danger: red-500
Warning: amber-500
Info: blue-500
```

### Typography
```
Font: Be Vietnam Pro (loaded in layout.tsx)
Page titles: text-3xl font-black tracking-tight
Section titles: text-lg / text-xl font-black
Labels: text-[10px] font-black uppercase tracking-[2px] text-slate-400
Body: text-sm font-semibold
```

### Spacing & Radii
```
Cards: rounded-[24px]  (via .premium-card class)
Buttons: rounded-2xl
Inputs: rounded-2xl
Nav items: rounded-xl
Modals: rounded-[28px]
```

---

## Component Patterns

### 1. Trang CRUD chuẩn

Mỗi trang admin phải có cấu trúc:

```tsx
'use client';

export default function XxxPage() {
  // 1. Local state only: useState
  const [data, setData] = useState(MOCK_OR_API_DATA);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);

  // 2. Filter/paginate in-memory
  const filtered = data.filter(...)
  const pageData = filtered.slice(...)

  return (
    <div className="space-y-6">
      {/* Header: title + action button */}
      {/* Filter bar: premium-card */}
      {/* Main content: table OR card grid */}
      {/* Pagination if table */}
      {/* Modal if needed */}
    </div>
  );
}
```

### 2. Page Header Pattern

```tsx
<div className="flex items-center justify-between">
  <div>
    <h1 className="text-3xl font-black text-slate-900 dark:text-white tracking-tight">
      {pageTitle}
    </h1>
    <p className="text-slate-500 font-semibold mt-1">{subtitle}</p>
  </div>
  <button className="flex items-center gap-2 px-5 py-2.5 bg-emerald-500 text-white font-bold text-sm rounded-2xl hover:bg-emerald-600 shadow-lg shadow-emerald-500/20 transition-all hover:scale-105 active:scale-95">
    <Plus size={16} />{actionLabel}
  </button>
</div>
```

### 3. Filter Bar Pattern

```tsx
<div className="premium-card">
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
    {/* Search input */}
    <div className="relative group">
      <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-emerald-500 transition-colors" />
      <input className="w-full pl-10 pr-4 py-3 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/8 rounded-2xl text-sm font-semibold outline-none focus:border-emerald-400 transition-colors" />
    </div>
    {/* Select filters */}
    <select className="px-4 py-3 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/8 rounded-2xl text-sm font-semibold outline-none focus:border-emerald-400 transition-colors" />
  </div>
</div>
```

### 4. Data Table Pattern

```tsx
<div className="premium-card p-0 overflow-hidden">
  <div className="overflow-x-auto">
    <table className="w-full">
      <thead>
        <tr className="border-b border-slate-100 dark:border-white/5">
          {COLS.map((col) => (
            <th key={col} className="px-6 py-4 text-left text-[10px] font-black text-slate-400 uppercase tracking-[2px]">
              {col}
            </th>
          ))}
        </tr>
      </thead>
      <tbody className="divide-y divide-slate-50 dark:divide-white/3">
        {pageData.map((row) => (
          <tr className="hover:bg-slate-50/50 dark:hover:bg-white/2 transition-colors group">
            {/* cells */}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
  {/* Pagination */}
</div>
```

### 5. Card Grid Pattern

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
  {items.map((item) => (
    <div key={item.id} className="premium-card group">
      {/* icon + actions */}
      {/* title + description */}
      {/* stats row */}
    </div>
  ))}
</div>
```

### 6. Stat Card

```tsx
<div className="premium-card group flex flex-col gap-4">
  <div className={`w-12 h-12 rounded-2xl ${iconBg} flex items-center justify-center transition-transform group-hover:scale-110`}>
    <Icon size={22} className="text-white" />
  </div>
  <div>
    <p className="text-[10px] font-black text-slate-400 uppercase tracking-[2px] mb-1.5">{label}</p>
    <p className="text-2xl font-black text-slate-900 dark:text-white tracking-tight">{value}</p>
  </div>
</div>
```

### 7. Modal Pattern

```tsx
<div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
  <div className="bg-white dark:bg-[#12131e] rounded-[28px] shadow-2xl w-full max-w-md p-8 border border-slate-100 dark:border-white/8">
    {/* header + X button */}
    {/* content */}
    {/* footer: Cancel + Confirm */}
  </div>
</div>
```

### 8. Recharts Pattern

```tsx
// Line Chart
<ResponsiveContainer width="100%" height="100%">
  <LineChart data={data}>
    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
    <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#94a3b8', fontWeight: 600 }} axisLine={false} tickLine={false} />
    <YAxis tick={{ fontSize: 11, fill: '#94a3b8', fontWeight: 600 }} axisLine={false} tickLine={false} />
    <Tooltip contentStyle={{ background: '#0f172a', border: 'none', borderRadius: 12, color: '#fff', fontSize: 12 }} />
    <Line type="monotone" dataKey="value" stroke="#10b981" strokeWidth={3} dot={{ fill: '#10b981', r: 4, strokeWidth: 2, stroke: '#fff' }} />
  </LineChart>
</ResponsiveContainer>

// Pie Chart
<ResponsiveContainer width="100%" height="100%">
  <PieChart>
    <Pie data={data} innerRadius={50} outerRadius={80} dataKey="value" paddingAngle={3}>
      {data.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
    </Pie>
    <Legend />
    <Tooltip contentStyle={{ background: '#0f172a', border: 'none', borderRadius: 12 }} />
  </PieChart>
</ResponsiveContainer>
```

---

## Data Fetching — Clean Pattern (NO SWR)

```tsx
// Sử dụng useEffect + useState thuần
const [data, setData] = useState<ApiType | null>(null);
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);

useEffect(() => {
  const controller = new AbortController();
  fetch('/api/admin/xxx', { signal: controller.signal })
    .then((r) => r.json())
    .then(setData)
    .catch((e) => { if (e.name !== 'AbortError') setError(e.message); })
    .finally(() => setLoading(false));
  return () => controller.abort();
}, [dependency]);
```

---

## Sidebar Menu Items (canonical order)

```
Tổng quan:
  - Dashboard           /dashboard
Nội dung:
  - Danh mục            /dashboard/categories
  - Chủ đề             /dashboard/topics
Thành viên:
  - Người dùng          /dashboard/users
  - Giảng viên          /dashboard/lecturers
  - Quyền hạn           /dashboard/roles
Tài chính:
  - Ví                  /dashboard/wallets
  - Giao dịch           /dashboard/transactions
  - Mã giảm giá         /dashboard/discounts
  - Hoàn tiền           /dashboard/refunds
  - Rút tiền            /dashboard/withdraws
Hệ thống:
  - Thông báo           /dashboard/notifications
  - Cài đặt             /dashboard/settings
```

---

## Checklist khi tạo trang admin mới

- [ ] `'use client';` ở đầu file
- [ ] Page title + subtitle + action button
- [ ] Filter bar (search + selects) trong `premium-card`
- [ ] Table hoặc grid dùng đúng pattern
- [ ] Hover actions (opacity-0 → opacity-100 on group-hover)
- [ ] Status badges với color đúng (emerald/amber/red/blue)
- [ ] Empty state đẹp (icon + message)
- [ ] Pagination cho bảng > 10 items
- [ ] Modal cho confirm actions
- [ ] Không dùng SWR, không hardcode text (dùng tiếng Việt)

---

## Quy tắc KHÔNG được vi phạm

1. **KHÔNG dùng SWR** — dùng `useState` + `useEffect` + `fetch`
2. **KHÔNG dùng plain string colors** (`red`, `blue`) — dùng Tailwind semantic
3. **KHÔNG hardcode màu inline** — dùng class Tailwind
4. **KHÔNG dùng icon màu** — icons phải monochrome (slate/white/emerald)
5. **KHÔNG tạo trang không có breadcrumb title** trong header
6. **KHÔNG bỏ qua dark mode** — luôn thêm `dark:` variant
7. **KHÔNG để loading state trống** — luôn có skeleton hoặc spinner

---

## Dependencies (web/)

```json
{
  "recharts": "^2.x",
  "framer-motion": "^12.x",
  "lucide-react": "^1.x",
  "zustand": "^5.x",
  "next-intl": "^4.x",
  "axios": "^1.x"
}
```

---

## Màu accent theo module

| Module | Accent |
|---|---|
| Users | blue-500 |
| Lecturers | violet-500 |
| Categories | emerald-500 |
| Topics | blue-400 |
| Wallets | emerald-500 |
| Transactions | slate-700 |
| Discounts | violet-500 |
| Refunds | red-500 |
| Withdraws | orange-500 |
| Notifications | amber-500 |
| Settings | slate-500 |
