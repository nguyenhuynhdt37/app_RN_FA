import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface CoursesPaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export function CoursesPagination({ currentPage, totalPages, onPageChange }: CoursesPaginationProps) {
  if (totalPages <= 1) return null;

  return (
    <div className="flex items-center justify-center gap-2">
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        className="w-10 h-10 rounded-2xl bg-white dark:bg-[#0A0A0A] border border-slate-100 dark:border-white/5 text-slate-500 font-bold text-sm hover:border-emerald-300 disabled:opacity-40 transition-all"
      >
        <ChevronLeft size={16} className="mx-auto" />
      </button>
      <span className="px-4 py-2 rounded-full bg-slate-100 dark:bg-white/5 text-xs font-black text-slate-500 dark:text-slate-300">
        {currentPage} / {totalPages}
      </span>
      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        className="w-10 h-10 rounded-2xl bg-white dark:bg-[#0A0A0A] border border-slate-100 dark:border-white/5 text-slate-500 font-bold text-sm hover:border-emerald-300 disabled:opacity-40 transition-all"
      >
        <ChevronRight size={16} className="mx-auto" />
      </button>
    </div>
  );
}
