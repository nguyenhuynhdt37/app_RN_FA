import { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import { 
  adminCourseService, 
  CourseApiError, 
  ListCoursesParams 
} from '../services/courses';
import type { 
  AdminCourse, 
  CourseCategory, 
  CourseFormData 
} from '../types';

const PAGE_SIZE = 12;

export function useCoursesManagement() {
  const [courses, setCourses] = useState<AdminCourse[]>([]);
  const [categories, setCategories] = useState<CourseCategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [stats, setStats] = useState({ total_courses: 0, total_enrolls: 0, total_revenue: 0, avg_rating: 0 });

  const [viewMode, setViewMode] = useState<'grid' | 'table'>('grid');
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('created_at');
  const [statusFilter, setStatusFilter] = useState<'all' | 'published' | 'draft'>('all');
  const [levelFilter, setLevelFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [page, setPage] = useState(1);

  const [editingCourse, setEditingCourse] = useState<AdminCourse | null>(null);
  const [deletingCourse, setDeletingCourse] = useState<AdminCourse | null>(null);
  const [deleteReason, setDeleteReason] = useState('');

  const buildParams = useCallback((): ListCoursesParams => ({
    page,
    page_size: PAGE_SIZE,
    search: search.trim() || undefined,
    sort_by: sortBy as ListCoursesParams['sort_by'],
    sort_order: 'desc',
    status: statusFilter,
    level: levelFilter || undefined,
    category_id: categoryFilter || undefined,
    lang: 'vi',
  }), [page, search, sortBy, statusFilter, levelFilter, categoryFilter]);

  const fetchCourses = useCallback(async () => {
    setLoading(true);
    try {
      const response = await adminCourseService.getCourses(buildParams());
      setCourses(response.items);
      setTotal(response.total);
      setTotalPages(response.total_pages);
      setPage(response.page);
    } catch (err) {
      const code = err instanceof CourseApiError ? err.code : 'COURSE_LIST_FAILED';
      toast.error(`Không thể tải danh sách khóa học (${code})`);
    } finally {
      setLoading(false);
    }
  }, [buildParams]);

  const fetchStats = useCallback(async () => {
    try {
      const data = await adminCourseService.getCourseStats();
      setStats(data.stats);
    } catch { /* silent */ }
  }, []);

  const fetchCategories = useCallback(async () => {
    try {
      const raw = await adminCourseService.getCategories();
      const mapped = raw.map((item: any) => ({
        id: item.id,
        translations: item.translations || {},
        icon_url: item.icon,
        position: item.position || 0,
      }));
      setCategories(mapped);
    } catch { /* silent */ }
  }, []);

  useEffect(() => {
    fetchCourses();
  }, [fetchCourses]);

  useEffect(() => {
    fetchStats();
    fetchCategories();
  }, [fetchStats, fetchCategories]);

  const handleDelete = async () => {
    if (!deletingCourse) return;
    try {
      await adminCourseService.deleteCourse(deletingCourse.id, deleteReason);
      toast.success('Đã xóa khóa học!');
      setDeletingCourse(null);
      setDeleteReason('');
      fetchCourses();
      fetchStats();
    } catch {
      toast.error('Xóa khóa học thất bại.');
    }
  };

  const resetFilters = () => {
    setSearch('');
    setSortBy('created_at');
    setStatusFilter('all');
    setLevelFilter('');
    setCategoryFilter('');
    setPage(1);
  };

  const goToPage = (next: number) => setPage(Math.min(Math.max(next, 1), totalPages));

  return {
    // State
    courses,
    categories,
    loading,
    total,
    totalPages,
    stats,
    viewMode,
    search,
    sortBy,
    statusFilter,
    levelFilter,
    categoryFilter,
    page,
    editingCourse,
    deletingCourse,
    deleteReason,
    
    // Setters
    setViewMode,
    setSearch,
    setSortBy,
    setStatusFilter,
    setLevelFilter,
    setCategoryFilter,
    setPage,
    setEditingCourse,
    setDeletingCourse,
    setDeleteReason,

    // Actions
    fetchCourses,
    fetchStats,
    handleDelete,
    resetFilters,
    goToPage,
    
    // Computed
    hasFilters: search.trim() !== '' || statusFilter !== 'all' || levelFilter !== '' || categoryFilter !== '',
    currentPage: Math.min(page, totalPages)
  };
}
