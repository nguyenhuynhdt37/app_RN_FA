'use client';

import { Code2, Folder, Languages, Megaphone, Palette, Trash2 } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { Link } from '@/i18n/routing';
import type { AdminCategory } from '../types';
import { formatCategoryDate, formatCategoryNumber, getCategoryTranslation } from '../types';

interface CategoryCardProps {
  category: AdminCategory;
  locale: string;
  onDelete?: (category: AdminCategory) => void;
}

const ADMIN_CATEGORY_LANG = 'vi';

function CategoryIcon({ icon }: { icon: string | null }) {
  if (!icon) return <Folder size={24} strokeWidth={2.5} />;

  const normalized = icon.toLowerCase();

  if (normalized.includes('code') || normalized.includes('program')) {
    return <Code2 size={24} strokeWidth={2.5} />;
  }

  if (normalized.includes('design') || normalized.includes('palette')) {
    return <Palette size={24} strokeWidth={2.5} />;
  }

  if (normalized.includes('market')) {
    return <Megaphone size={24} strokeWidth={2.5} />;
  }

  if (normalized.includes('lang')) {
    return <Languages size={24} strokeWidth={2.5} />;
  }

  return <Folder size={24} strokeWidth={2.5} />;
}

export function CategoryCard({ category, locale, onDelete }: CategoryCardProps) {
  const t = useTranslations('Admin.categories');
  const translation = getCategoryTranslation(category, ADMIN_CATEGORY_LANG);
  const translationCount = Object.keys(category.translations).length;

  return (
    <Link href={`/categories/${category.id}`} className="premium-card group flex h-full flex-col gap-5 transition hover:border-emerald-400/50">
      <div className="flex items-start justify-between gap-4">
        <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-[22px] border border-emerald-500/15 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
          <CategoryIcon icon={category.icon} />
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center rounded-full bg-slate-100 px-3 py-1 text-xs font-black text-slate-500 dark:bg-white/5 dark:text-slate-300">
            {formatCategoryNumber(category.course_count, locale)} {t('courseUnit')}
          </span>
          {onDelete && (
            <button
              type="button"
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                onDelete(category);
              }}
              className="flex h-9 w-9 items-center justify-center rounded-2xl border border-red-500/15 text-red-400 transition-all hover:border-red-500/30 hover:bg-red-500/10 hover:text-red-500 active:scale-95"
              aria-label={t('actions.delete')}
            >
              <Trash2 size={16} strokeWidth={2.5} />
            </button>
          )}
        </div>
      </div>

      <div className="min-w-0 flex-1">
        <h2 className="line-clamp-2 text-xl font-black text-slate-900 dark:text-white">
          {translation.name || t('untitled')}
        </h2>
        <p className="mt-2 line-clamp-3 min-h-[60px] text-sm font-semibold leading-5 text-slate-500">
          {translation.description || t('noDescription')}
        </p>
      </div>

      <div className="grid grid-cols-2 gap-3 border-t border-slate-100 pt-4 dark:border-white/5">
        <div>
          <p className="text-[10px] font-black uppercase tracking-[2px] text-slate-400">
            {t('card.translations')}
          </p>
          <p className="mt-1 text-sm font-black text-slate-900 dark:text-white">
            {formatCategoryNumber(translationCount, locale)}
          </p>
        </div>
        <div>
          <p className="text-[10px] font-black uppercase tracking-[2px] text-slate-400">
            {t('card.updated')}
          </p>
          <p className="mt-1 text-sm font-black text-slate-900 dark:text-white">
            {category.updated_at ? formatCategoryDate(category.updated_at, locale) : t('unknown')}
          </p>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {Object.keys(category.translations).map((lang) => (
          <span
            key={lang}
            className="rounded-full border border-slate-200 px-2.5 py-1 text-[10px] font-black uppercase tracking-[1px] text-slate-500 dark:border-white/10 dark:text-slate-300"
          >
            {lang}
          </span>
        ))}
      </div>
    </Link>
  );
}
