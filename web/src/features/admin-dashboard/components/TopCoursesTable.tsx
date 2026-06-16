import React from 'react';
import { BookOpen } from 'lucide-react';
import type { TopCourse } from '@/types/admin';
import { fmtShort } from '../types';

interface Props {
  courses: TopCourse[];
}

export function TopCoursesTable({ courses }: Props) {
  return (
    <div className="premium-card">
      <div className="mb-6">
        <h3 className="text-lg font-black text-slate-900 dark:text-white tracking-tight">Khóa học nổi bật</h3>
        <p className="text-xs font-bold text-slate-400 uppercase tracking-[2px] mt-1">Top doanh thu</p>
      </div>
      <div className="space-y-3">
        {courses.map((c, i) => (
          <div
            key={c.id}
            className="flex items-center gap-4 p-3 rounded-2xl hover:bg-slate-50 dark:hover:bg-white/3 transition-colors group"
          >
            <span className="w-7 h-7 rounded-xl bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 font-black text-xs flex items-center justify-center shrink-0">
              {i + 1}
            </span>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center shrink-0">
              <BookOpen size={16} className="text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-bold text-sm text-slate-900 dark:text-white truncate">{c.title}</p>
              <p className="text-xs text-slate-400 font-medium">{c.instructor_name}</p>
            </div>
            <div className="text-right shrink-0">
              <p className="font-black text-sm text-emerald-600">{fmtShort(c.revenue)}</p>
              <p className="text-xs text-slate-400">{c.enrollment_count.toLocaleString('vi-VN')} học viên</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
