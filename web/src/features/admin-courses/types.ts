// ─── Translation Types ─────────────────────────────────────────────────────────

export type SupportedLang = 'vi' | 'en' | 'jp' | 'kr' | 'fr';

export interface CourseTranslation {
  title: string;
  subtitle?: string;
  description?: string;
  learning_outcomes: string[];
  prerequisites: string[];
  slug?: string;
}

export interface SectionTranslation {
  title: string;
}

export interface CategoryTranslation {
  name: string;
  description?: string;
}

// ─── Course Types ─────────────────────────────────────────────────────────────

export type CourseLevel = 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED';
export type ApprovalStatus = 'pending' | 'approved' | 'rejected';

export interface AdminCourse {
  id: string;
  // Translations dict - kiến trúc mới (Netflix/Spotify style)
  translations: Record<SupportedLang, CourseTranslation>;
  // Base fields
  slug?: string;
  thumbnail_url?: string;
  preview_video_type: number;
  level: CourseLevel;
  language: string;
  is_published: boolean;
  category_ids: string[];
  instructor_id?: string;
  tags: string[];
  difficulty_score: number;
  estimated_duration?: number;
  // Stats
  base_price: number;
  currency: string;
  views: number;
  rating_avg: number;
  total_enrolls: number;
  revenue: number;
  lessons_count: number;
  // Approval
  approval_status?: ApprovalStatus;
  approval_note?: string | null;
  approved_by?: string | null;
  approved_at?: string | null;
  review_round?: number;
  // Timestamps
  created_at: string;
  updated_at: string;
  // Related
  instructor?: {
    full_name: string;
    avatar_url?: string;
  };
  sections?: AdminSection[];
}

export interface AdminSection {
  id: string;
  position: number;
  translations: Record<SupportedLang, SectionTranslation>;
  units?: AdminUnit[];
}

export interface AdminUnit {
  id: string;
  title: string;
  position: number;
  is_free: boolean;
  base_exp: number;
}

// ─── Category Types ──────────────────────────────────────────────────────────

export interface CourseCategory {
  id: string;
  translations: Record<SupportedLang, CategoryTranslation>;
  icon_url?: string;
  position: number;
  parent_id?: string;
}

// ─── AI Analysis Types ──────────────────────────────────────────────────────

export interface AIAnalysisResult {
  suggested_category_ids: string[];
  new_categories: Array<{ name_vi: string; name_en: string }>;
  // Translation output - new format
  translations: {
    vi: CourseTranslation;
    en: CourseTranslation;
  };
  suggested_tags: string[];
  suggested_level: CourseLevel;
  difficulty_score: number;
  confidence_score: number;
}

// ─── Form Types ─────────────────────────────────────────────────────────────

export interface CourseFormData {
  translations: {
    vi: Partial<CourseTranslation>;
    en: Partial<CourseTranslation>;
  };
  slug?: string;
  thumbnail_url?: string;
  preview_video_type: number;
  level: CourseLevel;
  language: string;
  tags: string[];
  difficulty_score: number;
  estimated_duration?: number;
  base_price: number;
  currency: string;
  category_ids: string[];
  instructor_id?: string;
  is_published: boolean;
}

// ─── Response Types ─────────────────────────────────────────────────────────

export interface AdminCoursesResponse {
  courses: AdminCourse[];
  pagination: {
    page: number;
    page_size: number;
    total: number;
    total_pages: number;
  };
}

export interface AdminCourseStats {
  total_courses: number;
  total_enrolls: number;
  total_revenue: number;
  avg_rating: number;
}

// ─── Helper Functions ────────────────────────────────────────────────────────

export const COURSE_LEVEL_LABELS: Record<CourseLevel, string> = {
  BEGINNER: 'Cơ bản',
  INTERMEDIATE: 'Trung cấp',
  ADVANCED: 'Nâng cao',
};

export const LEVEL_COLORS: Record<CourseLevel, string> = {
  BEGINNER: 'emerald',
  INTERMEDIATE: 'amber',
  ADVANCED: 'rose',
};

export const APPROVAL_LABELS: Record<ApprovalStatus, string> = {
  approved: 'Đã duyệt',
  pending: 'Chờ duyệt',
  rejected: 'Bị từ chối',
};

export const APPROVAL_COLORS: Record<ApprovalStatus, string> = {
  approved: 'emerald',
  pending: 'amber',
  rejected: 'rose',
};

/**
 * Get course title in specified language, fallback to any available language
 */
export function getCourseTitle(course: AdminCourse, lang: SupportedLang = 'vi'): string {
  return course.translations?.[lang]?.title 
    || course.translations?.vi?.title 
    || Object.values(course.translations || {})[0]?.title 
    || '';
}

/**
 * Get category name in specified language
 */
export function getCategoryName(category: CourseCategory, lang: SupportedLang = 'vi'): string {
  return category.translations?.[lang]?.name 
    || category.translations?.vi?.name 
    || Object.values(category.translations || {})[0]?.name 
    || '';
}

/**
 * Format currency
 */
export function formatCurrency(amount: number, currency = 'VND'): string {
  if (currency === 'USD') {
    return `$${amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  }
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
    maximumFractionDigits: 0,
  }).format(amount);
}

/**
 * Format large numbers
 */
export function formatNumber(num: number): string {
  if (num >= 1_000_000) return (num / 1_000_000).toFixed(1) + 'M';
  if (num >= 1_000) return (num / 1_000).toFixed(1) + 'K';
  return num.toString();
}

/**
 * Create empty translation for a language
 */
export function createEmptyTranslation(): CourseTranslation {
  return {
    title: '',
    subtitle: '',
    description: '',
    learning_outcomes: [],
    prerequisites: [],
  };
}

/**
 * Create empty form data
 */
export function createEmptyCourseForm(): CourseFormData {
  return {
    translations: {
      vi: createEmptyTranslation(),
      en: createEmptyTranslation(),
    },
    preview_video_type: 1,
    level: 'BEGINNER',
    language: 'vi',
    tags: [],
    difficulty_score: 5,
    base_price: 0,
    currency: 'VND',
    category_ids: [],
    is_published: false,
  };
}
