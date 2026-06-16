'use client';

import { ArrowLeft, BookOpen, Globe2, Languages, Pencil, RefreshCw, Star, Trash2, Users, Wallet } from 'lucide-react';
import { useLocale, useTranslations } from 'next-intl';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link } from '@/i18n/routing';
import { adminCategoryService, CategoryApiError } from '../services/categories';
import { CategoryDeleteModal } from './CategoryDeleteModal';
import { CategoryEditModal } from './CategoryEditModal';
import type { AdminCategoryDetail } from '../types';
import {
  formatCategoryCurrency,
  formatCategoryDate,
  formatCategoryNumber,
  getCategoryTranslation,
} from '../types';

interface CategoryDetailViewProps {
  categoryId: string;
}

const ADMIN_CATEGORY_LANG = 'vi';

function getErrorMessage(code: string, t: ReturnType<typeof useTranslations>): string {
  if (code === 'CATEGORY_NOT_FOUND') return t('errors.CATEGORY_NOT_FOUND');
  if (code === 'CATEGORY_DETAIL_FAILED') return t('errors.CATEGORY_DETAIL_FAILED');
  return t('errors.loadFailed');
}

export function CategoryDetailView({ categoryId }: CategoryDetailViewProps) {
  const locale = useLocale();
  const t = useTranslations('Admin.categories');
  const [detail, setDetail] = useState<AdminCategoryDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [updateErrorCode, setUpdateErrorCode] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteErrorCode, setDeleteErrorCode] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchDetail = useCallback(async (): Promise<void> => {
    try {
      const nextDetail = await adminCategoryService.getCategoryDetail(categoryId);
      setDetail(nextDetail);
      setError(null);
    } catch (requestError) {
      const code = requestError instanceof CategoryApiError ? requestError.code : 'CATEGORY_DETAIL_FAILED';
      setError(getErrorMessage(code, t));
    } finally {
      setIsLoading(false);
    }
  }, [categoryId, t]);

  const refreshDetail = async (): Promise<void> => {
    setIsLoading(true);
    await fetchDetail();
  };

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      void fetchDetail();
    }, 0);

    return () => window.clearTimeout(timeoutId);
  }, [fetchDetail]);

  const translation = useMemo(() => {
    if (!detail) return null;
    return getCategoryTranslation(detail, ADMIN_CATEGORY_LANG);
  }, [detail]);

  const handleUpdate = async (payload: { name?: string; description?: string }): Promise<void> => {
    setIsUpdating(true);
    setUpdateErrorCode(null);

    try {
      const updatedDetail = await adminCategoryService.updateCategory(categoryId, payload);
      setDetail(updatedDetail);
      setIsEditOpen(false);
    } catch (requestError) {
      const code = requestError instanceof CategoryApiError ? requestError.code : 'CATEGORY_UPDATE_FAILED';
      setUpdateErrorCode(code);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleDelete = async (): Promise<void> => {
    if (!detail) return;
    setIsDeleting(true);
    setDeleteErrorCode(null);

    try {
      await adminCategoryService.deleteCategory(categoryId);
      window.location.href = '/categories';
    } catch (requestError) {
      const code = requestError instanceof CategoryApiError ? requestError.code : 'CATEGORY_DELETE_FAILED';
      setDeleteErrorCode(code);
      setIsDeleting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-28 animate-pulse rounded-[32px] border border-slate-200 bg-white dark:border-white/10 dark:bg-slate-900" />
        <div className="grid gap-4 md:grid-cols-4">
          {Array.from({ length: 4 }).map((_, index) => (
            <div
              key={index}
              className="h-32 animate-pulse rounded-[28px] border border-slate-200 bg-white dark:border-white/10 dark:bg-slate-900"
            />
          ))}
        </div>
      </div>
    );
  }

  if (error || !detail || !translation) {
    return (
      <div className="premium-card flex min-h-[360px] flex-col items-center justify-center text-center">
        <div className="flex h-14 w-14 items-center justify-center rounded-[22px] border border-red-500/15 bg-red-500/10 text-red-500">
          <BookOpen size={24} strokeWidth={2.5} />
        </div>
        <h1 className="mt-5 text-2xl font-black text-slate-900 dark:text-white">
          {error ?? t('errors.CATEGORY_DETAIL_FAILED')}
        </h1>
        <div className="mt-6 flex flex-wrap justify-center gap-3">
          <Link
            href="/categories"
            className="inline-flex items-center gap-2 rounded-2xl border border-slate-200 px-4 py-2.5 text-sm font-black text-slate-700 transition hover:border-emerald-400 dark:border-white/10 dark:text-slate-200"
          >
            <ArrowLeft size={16} strokeWidth={2.5} />
            {t('detail.back')}
          </Link>
          <button
            type="button"
            onClick={() => void refreshDetail()}
            className="inline-flex items-center gap-2 rounded-2xl bg-emerald-500 px-4 py-2.5 text-sm font-black text-white transition hover:bg-emerald-600 active:scale-95"
          >
            <RefreshCw size={16} strokeWidth={2.5} />
            {t('actions.retry')}
          </button>
        </div>
      </div>
    );
  }

  const statItems = [
    { label: t('detail.stats.totalCourses'), value: formatCategoryNumber(detail.stats.total_courses, locale), icon: BookOpen },
    { label: t('detail.stats.published'), value: formatCategoryNumber(detail.stats.published_courses, locale), icon: Globe2 },
    { label: t('detail.stats.enrolls'), value: formatCategoryNumber(detail.stats.total_enrolls, locale), icon: Users },
    { label: t('detail.stats.revenue'), value: formatCategoryCurrency(detail.stats.total_revenue, locale), icon: Wallet },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <Link
            href="/categories"
            className="inline-flex items-center gap-2 rounded-2xl border border-slate-200 px-3 py-2 text-xs font-black text-slate-500 transition hover:border-emerald-400 hover:text-emerald-600 dark:border-white/10 dark:text-slate-300"
          >
            <ArrowLeft size={15} strokeWidth={2.5} />
            {t('detail.back')}
          </Link>
          <h1 className="mt-4 text-3xl font-black tracking-tight text-slate-900 dark:text-white">
            {translation.name || t('untitled')}
          </h1>
          <p className="mt-2 max-w-3xl text-sm font-semibold leading-6 text-slate-500">
            {translation.description || t('noDescription')}
          </p>
        </div>
        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            onClick={() => {
              setUpdateErrorCode(null);
              setIsEditOpen(true);
            }}
            className="inline-flex items-center justify-center gap-2 rounded-2xl bg-emerald-500 px-4 py-2.5 text-sm font-black text-white transition hover:bg-emerald-600 active:scale-95"
          >
            <Pencil size={16} strokeWidth={2.5} />
            {t('actions.edit')}
          </button>
          {detail.stats.total_courses === 0 && (
            <button
              type="button"
              onClick={() => {
                setDeleteErrorCode(null);
              }}
              className="inline-flex items-center justify-center gap-2 rounded-2xl border border-red-500/30 px-4 py-2.5 text-sm font-black text-red-400 transition hover:border-red-500 hover:bg-red-500/10 active:scale-95"
            >
              <Trash2 size={16} strokeWidth={2.5} />
              {t('actions.delete')}
            </button>
          )}
          <button
            type="button"
            onClick={() => void refreshDetail()}
            className="inline-flex items-center justify-center gap-2 rounded-2xl border border-slate-200 px-4 py-2.5 text-sm font-black text-slate-700 transition hover:border-emerald-400 dark:border-white/10 dark:text-slate-200"
          >
            <RefreshCw size={16} strokeWidth={2.5} />
            {t('actions.refresh')}
          </button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {statItems.map((item) => (
          <div key={item.label} className="premium-card">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-[10px] font-black uppercase tracking-[2px] text-slate-400">{item.label}</p>
                <p className="mt-2 text-2xl font-black text-slate-900 dark:text-white">{item.value}</p>
              </div>
              <div className="flex h-12 w-12 items-center justify-center rounded-[20px] border border-emerald-500/15 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
                <item.icon size={22} strokeWidth={2.5} />
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <section className="premium-card">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-[10px] font-black uppercase tracking-[2px] text-slate-400">
                {t('detail.translations')}
              </p>
              <h2 className="mt-1 text-xl font-black text-slate-900 dark:text-white">
                {formatCategoryNumber(detail.translations_full.length, locale)} {t('detail.languages')}
              </h2>
            </div>
            <Languages className="text-emerald-500" size={24} strokeWidth={2.5} />
          </div>

          <div className="mt-5 space-y-3">
            {detail.translations_full.map((item) => (
              <div key={item.id} className="rounded-[24px] border border-slate-200 p-4 dark:border-white/10">
                <div className="flex items-center justify-between gap-3">
                  <h3 className="text-sm font-black text-slate-900 dark:text-white">{item.name}</h3>
                  <span className="rounded-full bg-emerald-500/10 px-2.5 py-1 text-[10px] font-black uppercase tracking-[1px] text-emerald-700 dark:text-emerald-300">
                    {item.lang}
                  </span>
                </div>
                <p className="mt-2 text-sm font-semibold leading-5 text-slate-500">
                  {item.description || t('noDescription')}
                </p>
                <p className="mt-3 text-[10px] font-black uppercase tracking-[2px] text-slate-400">
                  {item.is_auto_translated ? t('detail.autoTranslated') : t('detail.manual')}
                </p>
              </div>
            ))}
          </div>
        </section>

        <section className="premium-card">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-[10px] font-black uppercase tracking-[2px] text-slate-400">
                {t('detail.courses')}
              </p>
              <h2 className="mt-1 text-xl font-black text-slate-900 dark:text-white">
                {formatCategoryNumber(detail.courses.length, locale)} {t('courseUnit')}
              </h2>
            </div>
            <div className="flex items-center gap-2 rounded-full border border-slate-200 px-3 py-1.5 text-xs font-black text-slate-500 dark:border-white/10 dark:text-slate-300">
              <Star size={14} strokeWidth={2.5} />
              {detail.stats.avg_rating.toFixed(1)}
            </div>
          </div>

          <div className="mt-5 space-y-3">
            {detail.courses.length === 0 ? (
              <div className="rounded-[24px] border border-dashed border-slate-200 p-6 text-center text-sm font-bold text-slate-500 dark:border-white/10">
                {t('detail.noCourses')}
              </div>
            ) : (
              detail.courses.map((course) => {
                const courseTranslation = course.translations.vi ?? Object.values(course.translations)[0];

                return (
                  <article key={course.id} className="rounded-[24px] border border-slate-200 p-4 dark:border-white/10">
                    <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                      <div className="min-w-0">
                        <h3 className="line-clamp-2 text-sm font-black text-slate-900 dark:text-white">
                          {courseTranslation?.title || t('untitled')}
                        </h3>
                        <p className="mt-1 line-clamp-2 text-xs font-semibold leading-5 text-slate-500">
                          {courseTranslation?.subtitle || course.default_slug || course.id}
                        </p>
                      </div>
                      <span className="w-fit rounded-full bg-slate-100 px-2.5 py-1 text-[10px] font-black uppercase tracking-[1px] text-slate-600 dark:bg-white/5 dark:text-slate-300">
                        {course.level}
                      </span>
                    </div>
                    <div className="mt-4 grid grid-cols-3 gap-3">
                      <Metric label={t('detail.courseMetrics.enrolls')} value={formatCategoryNumber(course.total_enrolls, locale)} />
                      <Metric label={t('detail.courseMetrics.views')} value={formatCategoryNumber(course.views, locale)} />
                      <Metric label={t('detail.courseMetrics.revenue')} value={formatCategoryCurrency(course.revenue, locale, course.currency)} />
                    </div>
                  </article>
                );
              })
            )}
          </div>
        </section>
      </div>

      <p className="text-xs font-bold text-slate-400">
        {t('detail.generatedAt')}: {detail.generated_at ? formatCategoryDate(detail.generated_at, locale) : t('unknown')}
      </p>

      {isEditOpen && (
        <CategoryEditModal
          isOpen={isEditOpen}
          initialName={translation.name}
          initialDescription={translation.description ?? ''}
          isSubmitting={isUpdating}
          errorCode={updateErrorCode}
          onClose={() => setIsEditOpen(false)}
          onSubmit={handleUpdate}
        />
      )}

      {detail.stats.total_courses === 0 && (
        <CategoryDeleteModal
          isOpen
          categoryName={translation.name || t('untitled')}
          isSubmitting={isDeleting}
          errorCode={deleteErrorCode}
          onClose={() => {
            setDeleteErrorCode(null);
            setIsDeleting(false);
          }}
          onConfirm={handleDelete}
        />
      )}
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0 rounded-2xl bg-slate-50 px-3 py-2 dark:bg-white/5">
      <p className="truncate text-[10px] font-black uppercase tracking-[1px] text-slate-400">{label}</p>
      <p className="mt-1 truncate text-xs font-black text-slate-900 dark:text-white">{value}</p>
    </div>
  );
}
