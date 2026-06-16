// ─────────────────────────────────────────
// Admin Types — NeuralEarn Web
// ─────────────────────────────────────────

export interface AdminUser {
  id: string;
  fullname: string;
  email: string;
  avatar: string | null;
  roles: string[];
  is_verified_email: boolean;
  is_banned: boolean;
  banned_reason: string | null;
  banned_until: string | null;
  total_courses: number;
  last_login_at: string;
  created_at: string;
  updated_at: string;
}

export interface AdminUserDetail extends AdminUser {
  phone: string | null;
  bio: string | null;
}

export interface PaginatedResponse<T> {
  items: T[];
  total_items: number;
  total_pages: number;
  page: number;
  size: number;
}

// Stats
export interface OverviewStats {
  total_users: number;
  total_courses: number;
  total_instructors: number;
  total_revenue: number;
  today_revenue: number;
  pending_withdrawals: number;
  pending_refunds: number;
}

export type RevenuePeriod = 'day' | 'week' | 'month' | 'year';

export interface RevenuePoint {
  date: string;
  amount: number;
  count: number;
}

export interface RevenueStats {
  total: number;
  platform_income: number;
  instructor_payout: number;
  data: RevenuePoint[];
}

export interface CategoryStat {
  name: string;
  course_count: number;
  color?: string;
}

export interface TopCourse {
  id: string;
  title: string;
  instructor_name: string;
  enrollment_count: number;
  rating: number;
  revenue: number;
  thumbnail: string | null;
}

export interface TopInstructor {
  id: string;
  fullname: string;
  avatar: string | null;
  total_courses: number;
  total_students: number;
  total_revenue: number;
  rating: number;
}

// Category & Topic
export interface Category {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  course_count: number;
  created_at: string;
}

export interface Topic {
  id: string;
  name: string;
  category_id: string;
  category_name: string;
  course_count: number;
  created_at: string;
}

// Lecturer
export interface Lecturer {
  id: string;
  fullname: string;
  email: string;
  avatar: string | null;
  total_courses: number;
  total_students: number;
  total_revenue: number;
  rating: number;
  is_verified: boolean;
  created_at: string;
}

// Transaction
export type TransactionType = 'purchase' | 'refund' | 'withdrawal' | 'deposit';
export type TransactionStatus = 'pending' | 'completed' | 'failed' | 'cancelled';

export interface Transaction {
  id: string;
  user_id: string;
  user_name: string;
  type: TransactionType;
  amount: number;
  status: TransactionStatus;
  description: string;
  created_at: string;
}

// Wallet
export interface Wallet {
  id: string;
  user_id: string;
  user_name: string;
  user_email: string;
  balance: number;
  total_earned: number;
  total_withdrawn: number;
  updated_at: string;
}

// Discount
export type DiscountType = 'percentage' | 'fixed';

export interface Discount {
  id: string;
  code: string;
  type: DiscountType;
  value: number;
  max_uses: number;
  used_count: number;
  expires_at: string | null;
  is_active: boolean;
  created_at: string;
}

// Refund
export type RefundStatus = 'pending' | 'approved' | 'rejected';

export interface Refund {
  id: string;
  user_id: string;
  user_name: string;
  course_title: string;
  amount: number;
  reason: string;
  status: RefundStatus;
  created_at: string;
}

// Withdrawal
export type WithdrawalStatus = 'pending' | 'approved' | 'rejected' | 'completed';

export interface Withdrawal {
  id: string;
  user_id: string;
  user_name: string;
  amount: number;
  bank_account: string;
  bank_name: string;
  status: WithdrawalStatus;
  created_at: string;
}

// Notification
export type NotificationLevel = 'info' | 'warning' | 'error' | 'success';

export interface AdminNotification {
  id: string;
  title: string;
  message: string;
  level: NotificationLevel;
  is_read: boolean;
  created_at: string;
}
