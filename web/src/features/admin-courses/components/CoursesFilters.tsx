import React from 'react';
import { Search, X, LayoutGrid, List } from 'lucide-react';
import { cn } from '@/lib/utils';
import { CourseCategory } from '../types';

interface CoursesFiltersProps {
  search: string;
  setSearch: (v: string) => void;
  sortBy: string;
  setSortBy: (v: string) => void;
  levelFilter: string;
  setLevelFilter: (v: string) => void;
  categoryFilter: string;
  setCategoryFilter: (v: string) => void;
  statusFilter: 'all' | 'published' | 'draft';
  setStatusFilter: (v: 'all' | 'published' | 'draft') => void;
  viewMode: 'grid' | 'table';
  setViewMode: (v: 'grid' | 'table') => void;
  categories: CourseCategory[];
  total: number;
  filteredCount: number;
  hasFilters: boolean;
  onReset: () => void;
}

const SORT_OPTIONS = [
  { value: 'created_at', label: 'Mới nhất' },
  { value: 'revenue', label: 'Doanh thu cao' },
  { value: 'views', label: 'Lượt xem' },
  { value: 'total_enrolls', label: 'Học viên' },
  { value: 'rating_avg', label: 'Đánh giá' },
];

export function CoursesFilters(props: CoursesFiltersProps) {
  const {
    search, setSearch, sortBy, setSortBy, levelFilter, setLevelFilter,
    categoryFilter, setCategoryFilter, statusFilter, setStatusFilter,
    viewMode, setViewMode, categories, total, filteredCount, hasFilters, onReset
  } = props;

  return (
    <div className="premium-card">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* Search */}
        <div className="relative group lg:col-span-2">
          <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-emerald-500 transition-colors" />
          <input
            type="text"
            placeholder="Tìm kiếm tên, slug, tag..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full pl-10 pr-10 py-3 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/8 rounded-2xl text-sm font-semibold outline-none focus:border-emerald-400 transition-colors"
          />
          {search && (
            <button
              onClick={() => setSearch('')}
              className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
            >
              <X size={14} />
            </button>
          )}
        </div>

        {/* Sort */}
        <select
          value={sortBy}
          onChange={e => setSortBy(e.target.value)}
          className="px-4 py-3 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/8 rounded-2xl text-sm font-semibold outline-none focus:border-emerald-400 transition-colors appearance-none"
        >
          {SORT_OPTIONS.map(o => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>

        {/* Level */}
        <select
          value={levelFilter}
          onChange={e => setLevelFilter(e.target.value)}
          className="px-4 py-3 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/8 rounded-2xl text-sm font-semibold outline-none focus:border-emerald-400 transition-colors appearance-none"
        >
          <option value="">Tất cả cấp độ</option>
          <option value="BEGINNER">Cơ bản</option>
          <option value="INTERMEDIATE">Trung cấp</option>
          <option value="ADVANCED">Nâng cao</option>
        </select>

        {/* Category */}
        <select
          value={categoryFilter}
          onChange={e => setCategoryFilter(e.target.value)}
          className="px-4 py-3 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/8 rounded-2xl text-sm font-semibold outline-none focus:border-emerald-400 transition-colors appearance-none"
        >
          <option value="">Tất cả danh mục</option>
          {categories.map(c => (
            <option key={c.id} value={c.id}>
              {(c.translations as any)?.vi?.name || (c.translations as any)?.en?.name || c.id}
            </option>
          ))}
        </select>
      </div>

      {/* Status + View toggle */}
      <div className="flex items-center justify-between mt-4 pt-4 border-t border-slate-100 dark:border-white/5">
        <div className="flex items-center gap-2 flex-wrap">
          {([
            { v: 'all' as const, l: 'Tất cả' },
            { v: 'published' as const, l: 'Đã đăng' },
            { v: 'draft' as const, l: 'Bản nháp' },
          ]).map(opt => (
            <button
              key={opt.v}
              onClick={() => setStatusFilter(opt.v)}
              className={cn(
                "px-4 py-1.5 rounded-xl text-xs font-bold transition-all",
                statusFilter === opt.v
                  ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/20'
                  : 'bg-slate-100 dark:bg-white/5 text-slate-500 hover:text-slate-700 dark:hover:text-white'
              )}
            >
              {opt.l}
            </button>
          ))}
          {hasFilters && (
            <button
              onClick={onReset}
              className="px-3 py-1.5 text-xs font-bold text-slate-400 hover:text-red-500 transition-colors"
            >
              <X size={12} className="inline" /> Xóa lọc
            </button>
          )}
          <span className="ml-2 text-xs font-bold text-slate-400">
            {filteredCount} / {total} khóa học
          </span>
        </div>

        <div className="flex items-center gap-1 p-1 bg-slate-100 dark:bg-white/5 rounded-2xl">
          {(['grid', 'table'] as const).map(mode => (
            <button
              key={mode}
              onClick={() => setViewMode(mode)}
              className={cn(
                "p-2 rounded-xl transition-all",
                viewMode === mode
                  ? 'bg-white dark:bg-white/10 shadow text-emerald-500'
                  : 'text-slate-400 hover:text-slate-600'
              )}
            >
              {mode === 'grid' ? <LayoutGrid size={16} /> : <List size={16} />}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
