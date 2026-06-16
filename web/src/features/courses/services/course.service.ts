import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export interface Course {
  id: string;
  thumbnail_url: string | null;
  level: string;
  base_price: number;
  currency: string;
  rating_avg: number;
  total_enrolls: number;
  lessons_count: number;
  title: string;
  subtitle: string | null;
  slug: string | null;
  price_coin: number;
  instructor?: {
    full_name: string;
    avatar_url: string | null;
  };
  categories: Array<{
    id: string;
    name: string;
    icon: string | null;
  }>;
}

export interface CourseListResponse {
  items: Course[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export const courseService = {
  async getCourses(params: {
    page?: number;
    page_size?: number;
    category_id?: string;
    level?: string;
    search?: string;
    sort?: string;
    lang?: string;
  } = {}) {
    const response = await axios.get<CourseListResponse>(`${API_URL}/courses`, {
      params,
    });
    return response.data;
  },
};
