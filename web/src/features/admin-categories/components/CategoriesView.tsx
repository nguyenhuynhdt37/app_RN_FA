'use client';

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { ChevronLeft, ChevronRight, Grid3X3, List, Plus, RefreshCw, Search, X } from 'lucide-react';
import { useLocale, useTranslations } from 'next-intl';
import { toast } from 'sonner';
import { adminCategoryService, CategoryApiError } from '../services/categories';
import type {
  AdminCategory,
  AdminCategoryStats,
  CategorySortBy,
  CoursePresenceFilter,
  CreateCategoryPayload,
  SortOrder,
} from '../types';
import {
  CATEGORY_PAGE_SIZE,
  formatCategoryNumber,
  getCategoryTranslation,
} from '../types';
import { CategoryCard } from './CategoryCard';
import { CategoryCreateModal } from './CategoryCreateModal';
import { CategoryDeleteModal } from './CategoryDeleteModal';
import { CategoryStatsCards } from './CategoryStatsCards';
import { CategoriesTable } from './CategoriesTable';

type ViewMode = 'grid' | 'table';
const ADMIN_CATEGORY_LANG = 'vi';

const SORT_OPTIONS: Array<{ value: CategorySortBy; order: SortOrder; key: string }> = [
  { value: 'created_at', order: 'desc', key: 'newest' },
  { value: 'updated_at', order: 'desc', key: 'updated' },
  { value: 'course_count', order: 'desc', key: 'mostCourses' },
  { value: 'name', order: 'asc', key: 'nameAsc' },
  { value: 'name', order: 'desc', key: 'nameDesc' },
];

export function CategoriesView() {
  const t = useTranslations('Admin.categories');
  const locale = useLocale();
  const [categories, setCategories] = useState<AdminCategory[]>([]);
  const [stats, setStats] = useState<AdminCategoryStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [totalCount, setTotalCount] = useState(0);
  const [errorCode, setErrorCode] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [presenceFilter, setPresenceFilter] = useState<CoursePresenceFilter>('all');
  const [sortIndex, setSortIndex] = useState(0);
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [page, setPage] = useState(1);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [createErrorCode, setCreateErrorCode] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<AdminCategory | null>(null);
  const [deleteErrorCode, setDeleteErrorCode] = useState<string | null>(null);
  const [debouncedSearch, setDebouncedSearch] = useState(search);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(search);
    }, 400);
    return () => clearTimeout(handler);
  }, [search]);

  const selectedSort = SORT_OPTIONS[sortIndex] ?? SORT_OPTIONS[0];

  const fetchCategories = useCallback(async () => {
    setLoading(true);
    setErrorCode(null);

    try {
      const hasCourses =
        presenceFilter === 'with-courses' ? true :
        presenceFilter === 'empty' ? false : undefined;

      const [categoryResponse, statsResponse] = await Promise.all([
        adminCategoryService.getCategories({
          lang: ADMIN_CATEGORY_LANG,
          page: page,
          page_size: CATEGORY_PAGE_SIZE,
          search: debouncedSearch.trim() || undefined,
          has_courses: hasCourses,
          sort_by: selectedSort.value,
          sort_order: selectedSort.order,
        }),
        adminCategoryService.getStats(),
      ]);

      setCategories(categoryResponse.items);
      setTotalCount(categoryResponse.total);
      setStats(statsResponse.stats);
    } catch {
      setErrorCode('CATEGORY_LIST_REQUEST_FAILED');
    } finally {
      setLoading(false);
    }
  }, [page, debouncedSearch, presenceFilter, selectedSort.order, selectedSort.value]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      fetchCategories();
    }, 0);

    return () => window.clearTimeout(timer);
  }, [fetchCategories]);

  const pageData = categories;
  const totalPages = Math.max(1, Math.ceil(totalCount / CATEGORY_PAGE_SIZE));
  const currentPage = Math.min(page, totalPages);
  const hasFilters = search.trim().length > 0 || presenceFilter !== 'all';
  const totalCourses = stats.reduce((total, item) => total + item.total_courses, 0);
  const activeCategories = stats.filter((item) => item.total_courses > 0).length;
  const emptyCategories = Math.max(0, totalCount - activeCategories);
  const totalEnrolls = stats.reduce((total, item) => total + item.total_enrolls, 0);

  const resetFilters = () => {
    setSearch('');
    setPresenceFilter('all');
    setPage(1);
  };

  const handleSortChange = (value: string) => {
    setSortIndex(Number(value));
    setPage(1);
  };

  const handlePresenceChange = (value: CoursePresenceFilter) => {
    setPresenceFilter(value);
    setPage(1);
  };

  const goToPage = (nextPage: number) => {
    setPage(Math.min(Math.max(nextPage, 1), totalPages));
  };

  const handleCreateCategory = async (payload: CreateCategoryPayload) => {
    setIsCreating(true);
    setCreateErrorCode(null);

    try {
      await adminCategoryService.createCategory(payload);
      toast.success(t('create.success'));
      setIsCreateOpen(false);
      setSearch('');
      setPresenceFilter('all');
      setSortIndex(0);
      setPage(1);
      await fetchCategories();
    } catch (error) {
      const code = error instanceof CategoryApiError ? error.code : 'CATEGORY_CREATE_FAILED';
      setCreateErrorCode(code);
      toast.error(t(`errors.${code}`));
    } finally {
      setIsCreating(false);
    }
  };

  const handleDeleteCategory = async () => {
    if (!deleteTarget) return;
    setDeletingId(deleteTarget.id);
    setDeleteErrorCode(null);

    try {
      await adminCategoryService.deleteCategory(deleteTarget.id);
      toast.success(t('delete.success'));
      setDeleteTarget(null);
      setDeletingId(null);
      await fetchCategories();
    } catch (error) {
      const code = error instanceof CategoryApiError ? error.code : 'CATEGORY_DELETE_FAILED';
      setDeleteErrorCode(code);
      toast.error(t(`errors.${code}`));
      setDeletingId(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-black tracking-tight text-slate-900 dark:text-white">
            {t('title')}
          </h1>
          <p className="mt-1 text-sm font-semibold text-slate-500">
            {t('subtitle', {
              total: formatCategoryNumber(totalCount, locale),
              courses: formatCategoryNumber(totalCourses, locale),
            })}
          </p>
        </div>
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
          <button
            type="button"
            onClick={fetchCategories}
            className="inline-flex items-center justify-center gap-2 rounded-2xl border border-slate-200 bg-white px-5 py-2.5 text-sm font-black text-slate-600 transition-all hover:border-emerald-300 hover:text-emerald-600 active:scale-95 dark:border-white/10 dark:bg-slate-900 dark:text-slate-300 dark:hover:border-emerald-500/30"
          >
            <RefreshCw size={16} strokeWidth={2.5} className={loading ? 'animate-spin' : ''} />
            {t('actions.refresh')}
          </button>
          <button
            type="button"
            onClick={() => {
              setCreateErrorCode(null);
              setIsCreateOpen(true);
            }}
            className="inline-flex items-center justify-center gap-2 rounded-full bg-emerald-500 px-5 py-2.5 text-sm font-black text-white transition-colors hover:bg-emerald-600 active:scale-95"
          >
            <Plus size={16} strokeWidth={2.5} />
            {t('actions.create')}
          </button>
        </div>
      </div>

      <CategoryStatsCards
        totalCategories={categories.length}
        activeCategories={activeCategories}
        emptyCategories={emptyCategories}
        totalCourses={totalCourses}
        locale={locale}
      />

      <div className="premium-card">
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-5">
          <div className="group relative lg:col-span-2">
            <Search
              size={16}
              strokeWidth={2.5}
              className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 transition-colors group-focus-within:text-emerald-500"
            />
            <input
              type="search"
              value={search}
              onChange={(event) => {
                setSearch(event.target.value);
                setPage(1);
              }}
              placeholder={t('filters.search')}
              className="w-full rounded-2xl border border-slate-200 bg-slate-50 py-3 pl-10 pr-10 text-sm font-semibold outline-none transition-colors focus:border-emerald-400 dark:border-white/10 dark:bg-white/5"
            />
            {search && (
              <button
                type="button"
                onClick={() => {
                  setSearch('');
                  setPage(1);
                }}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 transition-colors hover:text-slate-600 dark:hover:text-white"
                aria-label={t('actions.clearSearch')}
              >
                <X size={14} strokeWidth={2.5} />
              </button>
            )}
          </div>

          <select
            value={presenceFilter}
            onChange={(event) => handlePresenceChange(event.target.value as CoursePresenceFilter)}
            className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-semibold outline-none transition-colors focus:border-emerald-400 dark:border-white/10 dark:bg-white/5"
          >
            <option value="all">{t('filters.all')}</option>
            <option value="with-courses">{t('filters.withCourses')}</option>
            <option value="empty">{t('filters.empty')}</option>
          </select>

          <select
            value={sortIndex}
            onChange={(event) => handleSortChange(event.target.value)}
            className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-semibold outline-none transition-colors focus:border-emerald-400 dark:border-white/10 dark:bg-white/5"
          >
            {SORT_OPTIONS.map((option, index) => (
              <option key={`${option.value}-${option.order}`} value={index}>
                {t(`sort.${option.key}`)}
              </option>
            ))}
          </select>

          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-1 rounded-2xl bg-slate-100 p-1 dark:bg-white/5">
              <button
                type="button"
                onClick={() => setViewMode('grid')}
                className={`rounded-xl p-2 transition-colors ${
                  viewMode === 'grid'
                    ? 'bg-white text-emerald-600 dark:bg-white/10 dark:text-emerald-400'
                    : 'text-slate-400 hover:text-slate-600 dark:hover:text-white'
                }`}
                aria-label={t('view.grid')}
              >
                <Grid3X3 size={16} strokeWidth={2.5} />
              </button>
              <button
                type="button"
                onClick={() => setViewMode('table')}
                className={`rounded-xl p-2 transition-colors ${
                  viewMode === 'table'
                    ? 'bg-white text-emerald-600 dark:bg-white/10 dark:text-emerald-400'
                    : 'text-slate-400 hover:text-slate-600 dark:hover:text-white'
                }`}
                aria-label={t('view.table')}
              >
                <List size={16} strokeWidth={2.5} />
              </button>
            </div>
            {hasFilters && (
              <button
                type="button"
                onClick={resetFilters}
                className="rounded-full px-3 py-2 text-xs font-black text-slate-400 transition-colors hover:text-red-500"
              >
                {t('actions.clearFilters')}
              </button>
            )}
          </div>
        </div>

        <div className="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 pt-4 dark:border-white/5">
          <p className="text-xs font-black uppercase tracking-[2px] text-slate-400">
            {t('resultSummary', {
              count: formatCategoryNumber(categories.length, locale),
              total: formatCategoryNumber(totalCount, locale),
            })}
          </p>
          <p className="text-xs font-bold text-slate-400">
            {t('enrollSummary', { count: formatCategoryNumber(totalEnrolls, locale) })}
          </p>
        </div>
      </div>

      {loading && categories.length === 0 ? (
        <div className="grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 6 }, (_, index) => (
            <div
              key={index}
              className="h-72 animate-pulse rounded-[24px] border border-slate-100 bg-slate-100 dark:border-white/5 dark:bg-white/5"
            />
          ))}
        </div>
      ) : errorCode ? (
        <div className="premium-card flex flex-col items-center justify-center px-6 py-16 text-center">
          <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-[22px] border border-red-500/15 bg-red-500/10 text-red-500">
            <X size={22} strokeWidth={2.5} />
          </div>
          <p className="text-base font-black text-slate-900 dark:text-white">{t('errors.loadFailed')}</p>
          <p className="mt-1 text-sm font-semibold text-slate-500">{errorCode}</p>
          <button
            type="button"
            onClick={fetchCategories}
            className="mt-5 rounded-full bg-emerald-500 px-6 py-3 text-sm font-black text-white transition-colors hover:bg-emerald-600 active:scale-95"
          >
            {t('actions.retry')}
          </button>
        </div>
      ) : pageData.length === 0 ? (
        <div className="premium-card flex flex-col items-center justify-center px-6 py-16 text-center">
          <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-[22px] border border-slate-200 bg-slate-100 text-slate-400 dark:border-white/10 dark:bg-white/5">
            <Search size={22} strokeWidth={2.5} />
          </div>
          <p className="text-base font-black text-slate-900 dark:text-white">{t('empty.title')}</p>
          <p className="mt-1 text-sm font-semibold text-slate-500">{t('empty.subtitle')}</p>
          {hasFilters && (
            <button
              type="button"
              onClick={resetFilters}
              className="mt-5 rounded-full bg-emerald-500 px-6 py-3 text-sm font-black text-white transition-colors hover:bg-emerald-600 active:scale-95"
            >
              {t('actions.clearFilters')}
            </button>
          )}
        </div>
      ) : viewMode === 'grid' ? (
        <div className="grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-3">
          {pageData.map((category) => (
            <CategoryCard
              key={category.id}
              category={category}
              locale={locale}
              onDelete={setDeleteTarget}
            />
          ))}
        </div>
      ) : (
        <CategoriesTable
          data={pageData}
          locale={locale}
          onDelete={setDeleteTarget}
          deletingId={deletingId}
        />
      )}

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button
            type="button"
            onClick={() => goToPage(currentPage - 1)}
            disabled={currentPage === 1}
            className="flex h-10 w-10 items-center justify-center rounded-2xl border border-slate-100 bg-white text-slate-500 transition-colors hover:border-emerald-300 hover:text-emerald-600 disabled:opacity-40 dark:border-white/10 dark:bg-slate-900"
            aria-label={t('pagination.previous')}
          >
            <ChevronLeft size={16} strokeWidth={2.5} />
          </button>
          <span className="rounded-full bg-slate-100 px-4 py-2 text-xs font-black text-slate-500 dark:bg-white/5 dark:text-slate-300">
            {t('pagination.page', { page: currentPage, total: totalPages })}
          </span>
          <button
            type="button"
            onClick={() => goToPage(currentPage + 1)}
            disabled={currentPage === totalPages}
            className="flex h-10 w-10 items-center justify-center rounded-2xl border border-slate-100 bg-white text-slate-500 transition-colors hover:border-emerald-300 hover:text-emerald-600 disabled:opacity-40 dark:border-white/10 dark:bg-slate-900"
            aria-label={t('pagination.next')}
          >
            <ChevronRight size={16} strokeWidth={2.5} />
          </button>
        </div>
      )}

      {isCreateOpen && (
        <CategoryCreateModal
          isOpen
          isSubmitting={isCreating}
          errorCode={createErrorCode}
          onClose={() => {
            setCreateErrorCode(null);
            setIsCreateOpen(false);
          }}
          onSubmit={handleCreateCategory}
        />
      )}

      {deleteTarget && (
        <CategoryDeleteModal
          isOpen
          categoryName={getCategoryTranslation(deleteTarget, ADMIN_CATEGORY_LANG).name || t('untitled')}
          isSubmitting={deletingId !== null}
          errorCode={deleteErrorCode}
          onClose={() => {
            setDeleteErrorCode(null);
            setDeleteTarget(null);
          }}
          onConfirm={handleDeleteCategory}
        />
      )}
    </div>
  );
}
