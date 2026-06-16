import { apiFetch } from "@/lib/api";
import { AdminCourse, AdminCourseStats } from "../types";

export interface ListCoursesParams {
  page?: number;
  page_size?: number;
  search?: string;
  sort_by?: 'created_at' | 'views' | 'total_enrolls' | 'revenue' | 'rating_avg' | 'name' | 'updated_at';
  sort_order?: 'asc' | 'desc';
  status?: 'all' | 'published' | 'draft';
  level?: string;
  category_id?: string;
  lang?: string;
}

interface PaginatedResponse {
  items: AdminCourse[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export class CourseApiError extends Error {
  code: string;
  status: number;

  constructor(code: string, status: number) {
    super(code);
    this.name = "CourseApiError";
    this.code = code;
    this.status = status;
  }
}

async function getErrorCode(response: Response, fallback: string): Promise<string> {
  try {
    const payload = (await response.json()) as Record<string, unknown>;
    const detail = payload.detail as Record<string, unknown> | undefined;
    if (detail && typeof detail.code === "string") {
      return detail.code;
    }
    if (typeof payload.code === "string") {
      return payload.code;
    }
    return fallback;
  } catch {
    return fallback;
  }
}

export const adminCourseService = {
  async getCourses(params: ListCoursesParams = {}): Promise<PaginatedResponse> {
    const sp = new URLSearchParams();
    if (params.lang) sp.set("lang", params.lang);
    if (params.page) sp.set("page", String(params.page));
    if (params.page_size) sp.set("page_size", String(params.page_size));
    if (params.search) sp.set("search", params.search);
    if (params.sort_by) sp.set("sort_by", params.sort_by);
    if (params.sort_order) sp.set("sort_order", params.sort_order);
    if (params.status && params.status !== "all") sp.set("status", params.status);
    if (params.level) sp.set("level", params.level);
    if (params.category_id) sp.set("category_id", params.category_id);

    const suffix = sp.toString();
    const response = await apiFetch(`/admin/courses${suffix ? `?${suffix}` : ""}`);

    if (!response.ok) {
      throw new CourseApiError(
        await getErrorCode(response, "COURSE_LIST_FAILED"),
        response.status,
      );
    }

    return response.json() as Promise<PaginatedResponse>;
  },

  async getAllCourses(): Promise<AdminCourse[]> {
    const response = await apiFetch("/admin/courses/all");

    if (!response.ok) {
      throw new CourseApiError(
        await getErrorCode(response, "COURSE_LIST_FAILED"),
        response.status,
      );
    }

    return response.json() as Promise<AdminCourse[]>;
  },

  async getCourseStats(): Promise<{ stats: AdminCourseStats; generated_at: string }> {
    const response = await apiFetch("/admin/courses/stats");

    if (!response.ok) {
      throw new CourseApiError(
        await getErrorCode(response, "COURSE_STATS_FAILED"),
        response.status,
      );
    }

    return response.json() as Promise<{ stats: AdminCourseStats; generated_at: string }>;
  },

  async getCategories(): Promise<any[]> {
    const response = await apiFetch("/categories/all");

    if (!response.ok) {
      throw new CourseApiError(
        await getErrorCode(response, "CATEGORY_LIST_FAILED"),
        response.status,
      );
    }

    return response.json() as Promise<any[]>;
  },

  async createCourse(data: Partial<AdminCourse>): Promise<AdminCourse> {
    const response = await apiFetch("/admin/courses", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new CourseApiError(
        await getErrorCode(response, "COURSE_CREATE_FAILED"),
        response.status,
      );
    }
    return response.json() as Promise<AdminCourse>;
  },

  async updateCourse(id: string, data: Partial<AdminCourse>): Promise<AdminCourse> {
    const response = await apiFetch(`/admin/courses/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new CourseApiError(
        await getErrorCode(response, "COURSE_UPDATE_FAILED"),
        response.status,
      );
    }
    return response.json() as Promise<AdminCourse>;
  },

  async deleteCourse(id: string, reason?: string): Promise<boolean> {
    const response = await apiFetch(`/admin/courses/${id}`, {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reason }),
    });
    return response.ok;
  },

  async analyzeCourse(title: string, description: string): Promise<any> {
    const response = await apiFetch("/admin/courses/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, description }),
    });
    if (!response.ok) {
      throw new CourseApiError(
        await getErrorCode(response, "AI_ANALYSIS_FAILED"),
        response.status,
      );
    }
    return response.json();
  },

  async uploadThumbnail(courseId: string, file: File): Promise<{ thumbnail_url: string }> {
    const formData = new FormData();
    formData.append("file", file);
    const response = await apiFetch(`/admin/courses/${courseId}/thumbnail`, {
      method: "POST",
      body: formData,
    } as RequestInit);
    if (!response.ok) {
      throw new CourseApiError(
        await getErrorCode(response, "UPLOAD_FAILED"),
        response.status,
      );
    }
    return response.json() as Promise<{ thumbnail_url: string }>;
  },
};
