import React from 'react';
import type { TopInstructor } from '@/types/admin';
import { fmtShort } from '../types';

interface Props {
  instructors: TopInstructor[];
}

export function TopInstructorsTable({ instructors }: Props) {
  return (
    <div className="premium-card">
      <div className="mb-6">
        <h3 className="text-lg font-black text-slate-900 dark:text-white tracking-tight">Giảng viên xuất sắc</h3>
        <p className="text-xs font-bold text-slate-400 uppercase tracking-[2px] mt-1">Top doanh thu & học viên</p>
      </div>
      <div className="space-y-3">
        {instructors.map((ins, i) => (
          <div
            key={ins.id}
            className="flex items-center gap-4 p-3 rounded-2xl hover:bg-slate-50 dark:hover:bg-white/3 transition-colors"
          >
            <span className="w-7 h-7 rounded-xl bg-violet-50 dark:bg-violet-500/10 text-violet-600 font-black text-xs flex items-center justify-center shrink-0">
              {i + 1}
            </span>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-400 to-purple-500 flex items-center justify-center shrink-0 text-white font-black text-sm">
              {ins.fullname[0]}
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-bold text-sm text-slate-900 dark:text-white truncate">{ins.fullname}</p>
              <p className="text-xs text-slate-400 font-medium">
                {ins.total_courses} khóa · {ins.total_students.toLocaleString('vi-VN')} học viên
              </p>
            </div>
            <div className="text-right shrink-0">
              <p className="font-black text-sm text-emerald-600">{fmtShort(ins.total_revenue)}</p>
              <p className="text-xs text-slate-400">⭐ {ins.rating}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
