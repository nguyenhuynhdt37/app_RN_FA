'use client';

import { BookOpen, Folder, Layers, TrendingUp } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { formatCategoryNumber } from '../types';

interface CategoryStatsCardsProps {
  totalCategories: number;
  activeCategories: number;
  emptyCategories: number;
  totalCourses: number;
  locale: string;
}

export function CategoryStatsCards({
  totalCategories,
  activeCategories,
  emptyCategories,
  totalCourses,
  locale,
}: CategoryStatsCardsProps) {
  const t = useTranslations('Admin.categories.stats');

  const cards = [
    {
      key: 'total',
      label: t('total'),
      value: totalCategories,
      icon: Folder,
      tone: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/15',
    },
    {
      key: 'active',
      label: t('active'),
      value: activeCategories,
      icon: Layers,
      tone: 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/15',
    },
    {
      key: 'courses',
      label: t('courses'),
      value: totalCourses,
      icon: BookOpen,
      tone: 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/15',
    },
    {
      key: 'empty',
      label: t('empty'),
      value: emptyCategories,
      icon: TrendingUp,
      tone: 'bg-slate-500/10 text-slate-600 dark:text-slate-300 border-slate-500/15',
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
      {cards.map((card) => (
        <div key={card.key} className="premium-card flex items-center gap-4">
          <div className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl border ${card.tone}`}>
            <card.icon size={22} strokeWidth={2.5} />
          </div>
          <div className="min-w-0">
            <p className="text-[10px] font-black uppercase tracking-[2px] text-slate-400">
              {card.label}
            </p>
            <p className="mt-1 text-2xl font-black text-slate-900 dark:text-white">
              {formatCategoryNumber(card.value, locale)}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
