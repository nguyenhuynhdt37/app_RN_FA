import { apiFetch } from '@/lib/api';
import type {
  AdminCategory,
  AdminCategoryCourseSummary,
  AdminCategoryCourseTranslation,
  AdminCategoryDetail,
  AdminCategoryDetailStats,
  AdminCategoryListResponse,
  AdminCategoryStats,
  AdminCategoryStatsResponse,
  CategoryTranslationFull,
  CreateCategoryPayload,
  ListCategoriesParams,
  UpdateCategoryPayload,
} from '../types';

export class CategoryApiError extends Error {
  code: string;
  status: number;

  constructor(code: string, status: number) {
    super(code);
    this.name = 'CategoryApiError';
    this.code = code;
    this.status = status;
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}

function parseTranslation(value: unknown): { lang: string; name: string; description: string | null } {
  if (!isRecord(value)) {
    return { lang: '', name: '', description: null };
  }

  return {
    lang: typeof value.lang === 'string' ? value.lang : '',
    name: typeof value.name === 'string' ? value.name : '',
    description: typeof value.description === 'string' ? value.description : null,
  };
}

function parseTranslationFull(value: unknown): CategoryTranslationFull {
  const translation = parseTranslation(value);
  if (!isRecord(value)) {
    throw new Error('INVALID_CATEGORY_TRANSLATION_PAYLOAD');
  }

  return {
    ...translation,
    id: typeof value.id === 'string' ? value.id : '',
    category_id: typeof value.category_id === 'string' ? value.category_id : '',
    is_auto_translated: typeof value.is_auto_translated === 'boolean' ? value.is_auto_translated : false,
    created_at: typeof value.created_at === 'string' ? value.created_at : '',
    updated_at: typeof value.updated_at === 'string' ? value.updated_at : '',
  };
}

function parseCategory(value: unknown): AdminCategory {
  if (!isRecord(value)) {
    throw new Error('INVALID_CATEGORY_PAYLOAD');
  }

  const rawTranslations = isRecord(value.translations) ? value.translations : {};
  const translations = Object.entries(rawTranslations).reduce<Record<string, ReturnType<typeof parseTranslation>>>(
    (acc, [key, translation]) => {
      acc[key] = parseTranslation(translation);
      return acc;
    },
    {},
  );

  return {
    id: typeof value.id === 'string' ? value.id : '',
    icon: typeof value.icon === 'string' ? value.icon : null,
    created_at: typeof value.created_at === 'string' ? value.created_at : '',
    updated_at: typeof value.updated_at === 'string' ? value.updated_at : '',
    translations,
    course_count: typeof value.course_count === 'number' ? value.course_count : 0,
  };
}

function parseCourseTranslation(value: unknown): AdminCategoryCourseTranslation {
  if (!isRecord(value)) {
    return { lang: '', title: '', subtitle: null, description: null, slug: null };
  }

  return {
    lang: typeof value.lang === 'string' ? value.lang : '',
    title: typeof value.title === 'string' ? value.title : '',
    subtitle: typeof value.subtitle === 'string' ? value.subtitle : null,
    description: typeof value.description === 'string' ? value.description : null,
    slug: typeof value.slug === 'string' ? value.slug : null,
  };
}

function parseCourseSummary(value: unknown): AdminCategoryCourseSummary {
  if (!isRecord(value)) {
    throw new Error('INVALID_CATEGORY_COURSE_PAYLOAD');
  }

  const rawTranslations = isRecord(value.translations) ? value.translations : {};
  const translations = Object.entries(rawTranslations).reduce<Record<string, AdminCategoryCourseTranslation>>(
    (acc, [key, translation]) => {
      acc[key] = parseCourseTranslation(translation);
      return acc;
    },
    {},
  );

  return {
    id: typeof value.id === 'string' ? value.id : '',
    default_slug: typeof value.default_slug === 'string' ? value.default_slug : null,
    thumbnail_url: typeof value.thumbnail_url === 'string' ? value.thumbnail_url : null,
    level: typeof value.level === 'string' ? value.level : '',
    is_published: typeof value.is_published === 'boolean' ? value.is_published : false,
    approval_status: typeof value.approval_status === 'string' ? value.approval_status : null,
    base_price: typeof value.base_price === 'number' ? value.base_price : 0,
    currency: typeof value.currency === 'string' ? value.currency : 'VND',
    estimated_duration: typeof value.estimated_duration === 'number' ? value.estimated_duration : null,
    lessons_count: typeof value.lessons_count === 'number' ? value.lessons_count : 0,
    views: typeof value.views === 'number' ? value.views : 0,
    total_enrolls: typeof value.total_enrolls === 'number' ? value.total_enrolls : 0,
    revenue: typeof value.revenue === 'number' ? value.revenue : 0,
    rating_avg: typeof value.rating_avg === 'number' ? value.rating_avg : 0,
    created_at: typeof value.created_at === 'string' ? value.created_at : '',
    updated_at: typeof value.updated_at === 'string' ? value.updated_at : '',
    translations,
  };
}

function parseDetailStats(value: unknown): AdminCategoryDetailStats {
  if (!isRecord(value)) {
    return {
      total_courses: 0,
      published_courses: 0,
      draft_courses: 0,
      total_enrolls: 0,
      total_revenue: 0,
      total_views: 0,
      avg_rating: 0,
    };
  }

  return {
    total_courses: typeof value.total_courses === 'number' ? value.total_courses : 0,
    published_courses: typeof value.published_courses === 'number' ? value.published_courses : 0,
    draft_courses: typeof value.draft_courses === 'number' ? value.draft_courses : 0,
    total_enrolls: typeof value.total_enrolls === 'number' ? value.total_enrolls : 0,
    total_revenue: typeof value.total_revenue === 'number' ? value.total_revenue : 0,
    total_views: typeof value.total_views === 'number' ? value.total_views : 0,
    avg_rating: typeof value.avg_rating === 'number' ? value.avg_rating : 0,
  };
}

function parseCategoryDetail(payload: unknown): AdminCategoryDetail {
  if (!isRecord(payload)) {
    throw new Error('INVALID_CATEGORY_DETAIL_PAYLOAD');
  }

  return {
    ...parseCategory(payload),
    translations_full: Array.isArray(payload.translations_full)
      ? payload.translations_full.map(parseTranslationFull)
      : [],
    stats: parseDetailStats(payload.stats),
    courses: Array.isArray(payload.courses) ? payload.courses.map(parseCourseSummary) : [],
    generated_at: typeof payload.generated_at === 'string' ? payload.generated_at : '',
  };
}

function parseCategoryListResponse(payload: unknown): AdminCategoryListResponse {
  if (!isRecord(payload) || !Array.isArray(payload.items)) {
    throw new Error('INVALID_CATEGORY_LIST_PAYLOAD');
  }

  return {
    items: payload.items.map(parseCategory),
    total: typeof payload.total === 'number' ? payload.total : 0,
    page: typeof payload.page === 'number' ? payload.page : 1,
    page_size: typeof payload.page_size === 'number' ? payload.page_size : 20,
    total_pages: typeof payload.total_pages === 'number' ? payload.total_pages : 1,
    has_next: typeof payload.has_next === 'boolean' ? payload.has_next : false,
    has_prev: typeof payload.has_prev === 'boolean' ? payload.has_prev : false,
  };
}

function parseCategoryStats(value: unknown): AdminCategoryStats {
  if (!isRecord(value)) {
    throw new Error('INVALID_CATEGORY_STATS_PAYLOAD');
  }

  return {
    category_id: typeof value.category_id === 'string' ? value.category_id : '',
    total_courses: typeof value.total_courses === 'number' ? value.total_courses : 0,
    total_enrolls: typeof value.total_enrolls === 'number' ? value.total_enrolls : 0,
    total_revenue: typeof value.total_revenue === 'number' ? value.total_revenue : 0,
  };
}

function parseCategoryStatsResponse(payload: unknown): AdminCategoryStatsResponse {
  if (!isRecord(payload) || !Array.isArray(payload.stats)) {
    throw new Error('INVALID_CATEGORY_STATS_RESPONSE');
  }

  return {
    stats: payload.stats.map(parseCategoryStats),
    generated_at: typeof payload.generated_at === 'string' ? payload.generated_at : '',
  };
}

async function getErrorCode(response: Response, fallback: string): Promise<string> {
  try {
    const payload: unknown = await response.json();
    if (!isRecord(payload)) return fallback;
    const detail = payload.detail;
    if (isRecord(detail) && typeof detail.code === 'string') {
      return detail.code;
    }
    if (typeof payload.code === 'string') {
      return payload.code;
    }
    return fallback;
  } catch {
    return fallback;
  }
}

export const adminCategoryService = {
  async getCategories(params: ListCategoriesParams = {}): Promise<AdminCategoryListResponse> {
    const sp = new URLSearchParams();

    if (params.lang) sp.set('lang', params.lang);
    if (params.page) sp.set('page', String(params.page));
    if (params.page_size) sp.set('page_size', String(params.page_size));
    if (params.search) sp.set('search', params.search);
    if (typeof params.has_courses === 'boolean') sp.set('has_courses', String(params.has_courses));
    if (typeof params.min_course_count === 'number') sp.set('min_course_count', String(params.min_course_count));
    if (params.sort_by) sp.set('sort_by', params.sort_by);
    if (params.sort_order) sp.set('sort_order', params.sort_order);

    const suffix = sp.toString();
    const response = await apiFetch(`/categories${suffix ? `?${suffix}` : ''}`);

    if (!response.ok) {
      throw new Error('CATEGORY_LIST_REQUEST_FAILED');
    }

    return parseCategoryListResponse(await response.json());
  },

  async createCategory(payload: CreateCategoryPayload): Promise<AdminCategory> {
    const response = await apiFetch('/categories', {
      method: 'POST',
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new CategoryApiError(
        await getErrorCode(response, 'CATEGORY_CREATE_FAILED'),
        response.status,
      );
    }

    return parseCategory(await response.json());
  },

  async getStats(): Promise<AdminCategoryStatsResponse> {
    const response = await apiFetch('/categories/stats');

    if (!response.ok) {
      throw new Error('CATEGORY_STATS_REQUEST_FAILED');
    }

    return parseCategoryStatsResponse(await response.json());
  },

  async getCategoryDetail(id: string, courseLimit = 20): Promise<AdminCategoryDetail> {
    const sp = new URLSearchParams({ lang: 'vi', course_limit: String(courseLimit) });
    const response = await apiFetch(`/categories/${id}?${sp.toString()}`);

    if (!response.ok) {
      throw new CategoryApiError(
        await getErrorCode(response, 'CATEGORY_DETAIL_FAILED'),
        response.status,
      );
    }

    return parseCategoryDetail(await response.json());
  },

  async updateCategory(id: string, payload: UpdateCategoryPayload, courseLimit = 20): Promise<AdminCategoryDetail> {
    const sp = new URLSearchParams({ lang: 'vi', course_limit: String(courseLimit) });
    const response = await apiFetch(`/categories/${id}?${sp.toString()}`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new CategoryApiError(
        await getErrorCode(response, 'CATEGORY_UPDATE_FAILED'),
        response.status,
      );
    }

    return parseCategoryDetail(await response.json());
  },

  async deleteCategory(id: string): Promise<void> {
    const response = await apiFetch(`/categories/${id}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new CategoryApiError(
        await getErrorCode(response, 'CATEGORY_DELETE_FAILED'),
        response.status,
      );
    }
  },
};
