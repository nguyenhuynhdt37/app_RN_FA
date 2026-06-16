export interface CategoryTranslationSummary {
  lang: string;
  name: string;
  description: string | null;
}

export interface AdminCategory {
  id: string;
  icon: string | null;
  created_at: string;
  updated_at: string;
  translations: Record<string, CategoryTranslationSummary>;
  course_count: number;
}

export interface CategoryTranslationFull extends CategoryTranslationSummary {
  id: string;
  category_id: string;
  is_auto_translated: boolean;
  created_at: string;
  updated_at: string;
}

export interface AdminCategoryCourseTranslation {
  lang: string;
  title: string;
  subtitle: string | null;
  description: string | null;
  slug: string | null;
}

export interface AdminCategoryCourseSummary {
  id: string;
  default_slug: string | null;
  thumbnail_url: string | null;
  level: string;
  is_published: boolean;
  approval_status: string | null;
  base_price: number;
  currency: string;
  estimated_duration: number | null;
  lessons_count: number;
  views: number;
  total_enrolls: number;
  revenue: number;
  rating_avg: number;
  created_at: string;
  updated_at: string;
  translations: Record<string, AdminCategoryCourseTranslation>;
}

export interface AdminCategoryDetailStats {
  total_courses: number;
  published_courses: number;
  draft_courses: number;
  total_enrolls: number;
  total_revenue: number;
  total_views: number;
  avg_rating: number;
}

export interface AdminCategoryDetail extends AdminCategory {
  translations_full: CategoryTranslationFull[];
  stats: AdminCategoryDetailStats;
  courses: AdminCategoryCourseSummary[];
  generated_at: string;
}

export interface AdminCategoryListResponse {
  items: AdminCategory[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface AdminCategoryStats {
  category_id: string;
  total_courses: number;
  total_enrolls: number;
  total_revenue: number;
}

export interface AdminCategoryStatsResponse {
  stats: AdminCategoryStats[];
  generated_at: string;
}

export interface CreateCategoryPayload {
  name: string;
  description?: string;
  auto_translate_en: true;
}

export interface UpdateCategoryPayload {
  name?: string;
  description?: string;
}

export type CategorySortBy = 'created_at' | 'updated_at' | 'name' | 'course_count';
export type SortOrder = 'asc' | 'desc';
export type CoursePresenceFilter = 'all' | 'with-courses' | 'empty';

export interface ListCategoriesParams {
  lang?: string;
  page?: number;
  page_size?: number;
  search?: string;
  has_courses?: boolean;
  min_course_count?: number;
  sort_by?: CategorySortBy;
  sort_order?: SortOrder;
}

export const CATEGORY_PAGE_SIZE = 10;

export function getCategoryTranslation(
  category: AdminCategory,
  lang: string,
): CategoryTranslationSummary {
  return (
    category.translations[lang] ??
    category.translations.vi ??
    Object.values(category.translations)[0] ?? {
      lang,
      name: '',
      description: null,
    }
  );
}

export function formatCategoryDate(value: string, locale: string): string {
  return new Intl.DateTimeFormat(locale, {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(new Date(value));
}

export function formatCategoryNumber(value: number, locale: string): string {
  return new Intl.NumberFormat(locale).format(value);
}

export function formatCategoryCurrency(value: number, locale: string, currency = 'VND'): string {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
    maximumFractionDigits: 0,
  }).format(value);
}
