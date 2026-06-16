import type { OverviewStats, RevenueStats, TopCourse, TopInstructor } from '@/types/admin';

// ── Shared utilities ──────────────────────────────────────────────────────────
export const fmt = (n: number) =>
  new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND', maximumFractionDigits: 0 }).format(n);

export const fmtShort = (n: number) =>
  n >= 1_000_000 ? `${(n / 1_000_000).toFixed(1)}M ₫` : n >= 1_000 ? `${(n / 1_000).toFixed(0)}K ₫` : `${n} ₫`;

// ── Mock data (swap with real API calls) ──────────────────────────────────────
export const MOCK_STATS: OverviewStats = {
  total_users: 12_847,
  total_courses: 348,
  total_instructors: 82,
  total_revenue: 1_284_500_000,
  today_revenue: 4_350_000,
  pending_withdrawals: 14,
  pending_refunds: 7,
};

export const MOCK_REVENUE: RevenueStats = {
  total: 1_284_500_000,
  platform_income: 385_350_000,
  instructor_payout: 899_150_000,
  data: [
    { date: '2025-01', amount: 82_000_000, count: 94 },
    { date: '2025-02', amount: 95_000_000, count: 112 },
    { date: '2025-03', amount: 78_000_000, count: 88 },
    { date: '2025-04', amount: 110_000_000, count: 131 },
    { date: '2025-05', amount: 134_000_000, count: 152 },
    { date: '2025-06', amount: 121_000_000, count: 140 },
    { date: '2025-07', amount: 145_000_000, count: 168 },
    { date: '2025-08', amount: 162_000_000, count: 189 },
    { date: '2025-09', amount: 143_000_000, count: 164 },
    { date: '2025-10', amount: 178_000_000, count: 201 },
    { date: '2025-11', amount: 155_000_000, count: 178 },
    { date: '2025-12', amount: 198_000_000, count: 228 },
  ],
};

export const MOCK_CATEGORIES = [
  { name: 'Lập trình', course_count: 98 },
  { name: 'Thiết kế', course_count: 62 },
  { name: 'Marketing', course_count: 45 },
  { name: 'Kinh doanh', course_count: 71 },
  { name: 'Ngôn ngữ', course_count: 38 },
  { name: 'Khác', course_count: 34 },
];

export const PIE_COLORS = ['#10b981', '#059669', '#34d399', '#6ee7b7', '#a7f3d0', '#d1fae5'];

export const MOCK_TOP_COURSES: TopCourse[] = [
  { id: '1', title: 'React Native Mastery 2025', instructor_name: 'Nguyễn Văn A', enrollment_count: 1284, rating: 4.9, revenue: 98_500_000, thumbnail: null },
  { id: '2', title: 'FastAPI & PostgreSQL Pro', instructor_name: 'Trần Thị B', enrollment_count: 987, rating: 4.8, revenue: 74_200_000, thumbnail: null },
  { id: '3', title: 'UI/UX Design Fundamentals', instructor_name: 'Lê Văn C', enrollment_count: 854, rating: 4.7, revenue: 61_800_000, thumbnail: null },
  { id: '4', title: 'Python for Data Science', instructor_name: 'Phạm Thị D', enrollment_count: 762, rating: 4.6, revenue: 55_400_000, thumbnail: null },
];

export const MOCK_TOP_INSTRUCTORS: TopInstructor[] = [
  { id: '1', fullname: 'Nguyễn Văn A', avatar: null, total_courses: 12, total_students: 4820, total_revenue: 245_000_000, rating: 4.9 },
  { id: '2', fullname: 'Trần Thị B', avatar: null, total_courses: 8, total_students: 3214, total_revenue: 187_000_000, rating: 4.8 },
  { id: '3', fullname: 'Lê Văn C', avatar: null, total_courses: 6, total_students: 2654, total_revenue: 142_000_000, rating: 4.7 },
];
