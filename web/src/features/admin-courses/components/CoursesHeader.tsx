import React from 'react';
import { RefreshCw, Plus } from 'lucide-react';
import { Link } from '@/i18n/routing';
import { cn } from '@/lib/utils';

interface CoursesHeaderProps {
  loading: boolean;
  onRefresh: () => void;
}

export function CoursesHeader({ loading, onRefresh }: CoursesHeaderProps) {
  return (
    <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
      <div>
        <h1 className="text-3xl font-black text-slate-900 dark:text-white tracking-tight">
          Quản lý Khóa học
        </h1>
        <p className="text-slate-500 font-semibold mt-1">
          Thiết kế lộ trình học tập tối ưu cho người dùng.
        </p>
      </div>
      <div className="flex items-center gap-2">
        <button
          onClick={onRefresh}
          className="p-2.5 rounded-2xl bg-white dark:bg-[#0A0A0A] border border-slate-100 dark:border-white/5 text-slate-500 hover:text-emerald-500 hover:border-emerald-200 dark:hover:border-emerald-500/30 transition-all"
          title="Làm mới"
        >
          <RefreshCw size={20} className={loading ? 'animate-spin' : ''} />
        </button>
        <Link
          href="/courses/new"
          className="flex items-center gap-2 px-6 py-3 bg-emerald-500 text-white font-bold text-sm rounded-2xl hover:bg-emerald-600 shadow-lg shadow-emerald-500/20 transition-all hover:scale-105 active:scale-95"
        >
          <Plus size={18} />
          Tạo khóa học mới
        </Link>
      </div>
    </div>
  );
}
