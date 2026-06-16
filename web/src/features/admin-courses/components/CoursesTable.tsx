'use client';

import React from 'react';
import { Edit3, ExternalLink, Globe, Trash2, Users } from 'lucide-react';
import { BookOpen } from 'lucide-react';
import { cn } from '@/lib/utils';
import {
  AdminCourse,
  CourseCategory,
  COURSE_LEVEL_LABELS,
  formatCurrency,
  formatNumber,
  getCourseTitle,
} from '../types';

interface Props {
  data: AdminCourse[];
  categories: CourseCategory[];
  onEdit: (course: AdminCourse) => void;
  onDelete: (course: AdminCourse) => void;
}

const COLS = ['Khóa học', 'Danh mục', 'Cấp độ', 'Học viên', 'Doanh thu', 'Trạng thái', 'Thao tác'];

export function CoursesTable({ data, categories, onEdit, onDelete }: Props) {
  const getCatNames = (ids: string[]) =>
    ids
      .map(id => {
        const cat = categories.find(c => c.id === id);
        if (!cat) return null;
        const t = cat.translations as Record<string, { name?: string }>;
        return t?.vi?.name ?? t?.en?.name ?? null;
      })
      .filter(Boolean);

  const title = (course: AdminCourse) =>
    getCourseTitle(course, 'vi') || course.slug || 'Untitled';

  const lang = (course: AdminCourse) =>
    (course.translations as Record<string, { subtitle?: string }> | null)?.vi?.subtitle ?? course.language ?? 'vi';

  return (
    <div className="premium-card p-0 overflow-hidden border border-slate-100 dark:border-white/5 bg-white dark:bg-[#0A0A0A]">
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="border-b border-slate-50 dark:border-white/5 bg-slate-50/50 dark:bg-white/[0.02]">
              {COLS.map((col) => (
                <th key={col} className="px-5 py-4 text-left text-[10px] font-black text-slate-400 uppercase tracking-[2px]">
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50 dark:divide-white/3">
            {data.length === 0 ? (
              <tr>
                <td colSpan={COLS.length} className="px-6 py-20 text-center">
                  <div className="w-16 h-16 rounded-[24px] bg-slate-100 dark:bg-white/5 flex items-center justify-center mx-auto mb-4">
                    <BookOpen size={24} className="text-slate-400" />
                  </div>
                  <p className="font-bold text-slate-500">Chưa có khóa học nào</p>
                  <p className="text-xs text-slate-400 font-semibold mt-1">Tạo khóa học đầu tiên ngay</p>
                </td>
              </tr>
            ) : (
              data.map((course) => {
                const catNames = getCatNames(course.category_ids);
                return (
                  <tr key={course.id} className="hover:bg-slate-50/50 dark:hover:bg-white/[0.01] transition-colors group">
                    {/* Course info */}
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-14 h-9 rounded-xl bg-slate-100 dark:bg-white/5 overflow-hidden shrink-0 border border-slate-100 dark:border-white/5">
                          {course.thumbnail_url ? (
                            <img src={course.thumbnail_url} alt="" className="w-full h-full object-cover" />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center text-slate-300">
                              <BookOpen size={14} />
                            </div>
                          )}
                        </div>
                        <div className="min-w-0">
                          <p className="font-bold text-sm text-slate-900 dark:text-white truncate max-w-[200px]">
                            {title(course)}
                          </p>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="flex items-center gap-1 text-[10px] font-bold text-slate-400 uppercase">
                              <Globe size={10} />{lang(course)}
                            </span>
                            <span className="w-1 h-1 rounded-full bg-slate-200 dark:bg-white/10" />
                            <span className="text-[10px] font-bold text-slate-400">{formatNumber(course.views)} views</span>
                          </div>
                        </div>
                      </div>
                    </td>

                    {/* Categories */}
                    <td className="px-5 py-4">
                      <div className="flex flex-wrap gap-1 max-w-[120px]">
                        {catNames.length > 0 ? (
                          catNames.slice(0, 2).map(n => (
                            <span key={n} className="px-2 py-0.5 rounded-lg bg-violet-50 dark:bg-violet-500/10 text-violet-600 dark:text-violet-400 text-[10px] font-bold truncate max-w-[100px]">
                              {n}
                            </span>
                          ))
                        ) : (
                          <span className="text-xs text-slate-400 font-semibold">—</span>
                        )}
                        {catNames.length > 2 && (
                          <span className="text-[10px] font-bold text-slate-400">+{catNames.length - 2}</span>
                        )}
                      </div>
                    </td>

                    {/* Level */}
                    <td className="px-5 py-4">
                      <span className={cn(
                        "px-2.5 py-1 rounded-lg text-[10px] font-black uppercase whitespace-nowrap",
                        course.level === 'BEGINNER' && "bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400",
                        course.level === 'INTERMEDIATE' && "bg-amber-50 dark:bg-amber-500/10 text-amber-600 dark:text-amber-400",
                        course.level === 'ADVANCED' && "bg-rose-50 dark:bg-rose-500/10 text-rose-600 dark:text-rose-400"
                      )}>
                        {COURSE_LEVEL_LABELS[course.level]}
                      </span>
                    </td>

                    {/* Students */}
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-2">
                        <Users size={14} className="text-slate-400" />
                        <span className="text-sm font-bold text-slate-700 dark:text-slate-300">
                          {formatNumber(course.total_enrolls)}
                        </span>
                      </div>
                    </td>

                    {/* Revenue */}
                    <td className="px-5 py-4">
                      <span className="text-sm font-black text-emerald-600 dark:text-emerald-400 whitespace-nowrap">
                        {formatCurrency(course.revenue)}
                      </span>
                    </td>

                    {/* Status */}
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-2">
                        <div className={cn(
                          "w-2 h-2 rounded-full",
                          course.is_published ? "bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" : "bg-slate-300 dark:bg-white/20"
                        )} />
                        <span className="text-xs font-bold text-slate-600 dark:text-slate-400 whitespace-nowrap">
                          {course.is_published ? 'Đã đăng' : 'Bản nháp'}
                        </span>
                      </div>
                    </td>

                    {/* Actions */}
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-all duration-200">
                        <button
                          onClick={() => onEdit(course)}
                          title="Chỉnh sửa"
                          className="p-2 rounded-xl hover:bg-emerald-50 dark:hover:bg-emerald-500/10 text-slate-400 hover:text-emerald-600 transition-colors"
                        >
                          <Edit3 size={15} />
                        </button>
                        <a
                          href={`/courses/${course.slug}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          title="Xem trước"
                          className="p-2 rounded-xl hover:bg-blue-50 dark:hover:bg-blue-500/10 text-slate-400 hover:text-blue-500 transition-colors"
                        >
                          <ExternalLink size={15} />
                        </a>
                        <button
                          onClick={() => onDelete(course)}
                          title="Xóa"
                          className="p-2 rounded-xl hover:bg-red-50 dark:hover:bg-red-500/10 text-slate-400 hover:text-red-500 transition-colors"
                        >
                          <Trash2 size={15} />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
