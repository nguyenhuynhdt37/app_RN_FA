'use client';

import { BookOpen, Folder, Loader2, Trash2 } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { Link } from '@/i18n/routing';
import type { AdminCategory } from '../types';
import { formatCategoryDate, formatCategoryNumber, getCategoryTranslation } from '../types';

interface CategoriesTableProps {
  data: AdminCategory[];
  locale: string;
  onDelete?: (category: AdminCategory) => void;
  deletingId?: string | null;
}

const ADMIN_CATEGORY_LANG = 'vi';

export function CategoriesTable({ data, locale, onDelete, deletingId }: CategoriesTableProps) {
  const t = useTranslations('Admin.categories');

  return (
    <div className="premium-card overflow-hidden p-0">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[760px]">
          <thead>
            <tr className="border-b border-slate-100 dark:border-white/5">
              <th className="px-6 py-4 text-left text-[10px] font-black uppercase tracking-[2px] text-slate-400">
                {t('table.category')}
              </th>
              <th className="px-6 py-4 text-left text-[10px] font-black uppercase tracking-[2px] text-slate-400">
                {t('table.description')}
              </th>
              <th className="px-6 py-4 text-left text-[10px] font-black uppercase tracking-[2px] text-slate-400">
                {t('table.courses')}
              </th>
              <th className="px-6 py-4 text-left text-[10px] font-black uppercase tracking-[2px] text-slate-400">
                {t('table.translations')}
              </th>
              <th className="px-6 py-4 text-left text-[10px] font-black uppercase tracking-[2px] text-slate-400">
                {t('table.updated')}
              </th>
              {onDelete && (
                <th className="px-6 py-4 text-left text-[10px] font-black uppercase tracking-[2px] text-slate-400">
                  {t('table.action')}
                </th>
              )}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50 dark:divide-white/5">
            {data.map((category) => {
              const translation = getCategoryTranslation(category, ADMIN_CATEGORY_LANG);

              return (
                <tr
                  key={category.id}
                  className="group transition-colors hover:bg-slate-50/70 dark:hover:bg-white/[0.03]"
                >
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl border border-emerald-500/15 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
                        <Folder size={18} strokeWidth={2.5} />
                      </div>
                      <div className="min-w-0">
                        <Link
                          href={`/categories/${category.id}`}
                          className="block max-w-[220px] truncate text-sm font-black text-slate-900 transition hover:text-emerald-600 dark:text-white dark:hover:text-emerald-300"
                        >
                          {translation.name}
                        </Link>
                        <p className="mt-0.5 max-w-[220px] truncate text-xs font-semibold text-slate-400">
                          {category.id}
                        </p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <p className="line-clamp-2 max-w-[280px] text-sm font-semibold leading-5 text-slate-500">
                      {translation.description || t('noDescription')}
                    </p>
                  </td>
                  <td className="px-6 py-4">
                    <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-black text-emerald-700 dark:text-emerald-300">
                      <BookOpen size={13} strokeWidth={2.5} />
                      {formatCategoryNumber(category.course_count, locale)}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-wrap gap-1.5">
                      {Object.keys(category.translations).map((lang) => (
                        <span
                          key={lang}
                          className="rounded-full border border-slate-200 px-2 py-0.5 text-[10px] font-black uppercase tracking-[1px] text-slate-500 dark:border-white/10 dark:text-slate-300"
                        >
                          {lang}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm font-bold text-slate-500">
                    {category.updated_at ? formatCategoryDate(category.updated_at, locale) : t('unknown')}
                  </td>
                  {onDelete && (
                    <td className="px-6 py-4">
                      <button
                        type="button"
                        onClick={() => onDelete(category)}
                        disabled={deletingId === category.id}
                        className="inline-flex items-center justify-center gap-1.5 rounded-2xl border border-red-500/15 px-3 py-2 text-xs font-black text-red-400 transition-all hover:border-red-500/30 hover:bg-red-500/10 hover:text-red-500 active:scale-95 disabled:cursor-not-allowed disabled:opacity-40"
                        aria-label={t('actions.delete')}
                      >
                        {deletingId === category.id ? (
                          <Loader2 size={14} strokeWidth={2.5} className="animate-spin" />
                        ) : (
                          <Trash2 size={14} strokeWidth={2.5} />
                        )}
                        {t('actions.delete')}
                      </button>
                    </td>
                  )}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
