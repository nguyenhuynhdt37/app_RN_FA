import type { AdminUser } from '@/types/admin';

// ── Mock data ──────────────────────────────────────────────────────────────────
const NAMES = ['Nguyễn Văn An', 'Trần Thị Bình', 'Lê Văn Cường', 'Phạm Thị Dung', 'Hoàng Văn Em'];

export const MOCK_USERS: AdminUser[] = Array.from({ length: 52 }, (_, i) => ({
  id: String(i + 1),
  fullname: NAMES[i % 5],
  email: `user${i + 1}@example.com`,
  avatar: null,
  roles: i % 5 === 2 ? ['lecturer', 'user'] : ['user'],
  is_verified_email: i % 4 !== 0,
  is_banned: i % 7 === 0,
  banned_reason: i % 7 === 0 ? 'Vi phạm điều khoản' : null,
  banned_until: null,
  total_courses: Math.floor(Math.random() * 12),
  last_login_at: new Date(Date.now() - Math.random() * 7 * 86_400_000).toISOString(),
  created_at: new Date(Date.now() - Math.random() * 365 * 86_400_000).toISOString(),
  updated_at: new Date().toISOString(),
}));

// ── Helpers ────────────────────────────────────────────────────────────────────
export const PAGE_SIZE = 10;

export const fmtDate = (s: string) =>
  new Date(s).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' });

export const fmtRelative = (s: string) => {
  const h = Math.floor((Date.now() - new Date(s).getTime()) / 3_600_000);
  if (h < 1) return 'Vừa xong';
  if (h < 24) return `${h}h trước`;
  return `${Math.floor(h / 24)}d trước`;
};
