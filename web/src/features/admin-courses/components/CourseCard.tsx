'use client';

import React from 'react';
import {
  BookOpen,
  Users,
  Eye,
  Star,
  MoreVertical,
  Pencil,
  BarChart2,
  Trash2,
  ExternalLink,
} from 'lucide-react';
import { AdminCourse, COURSE_LEVEL_LABELS, LEVEL_COLORS, formatCurrency, formatNumber, getCourseTitle } from '../types';
import { cn } from '@/lib/utils';

interface Props {
  course: AdminCourse;
  onEdit: (course: AdminCourse) => void;
  onDelete: (course: AdminCourse) => void;
  onStats?: (course: AdminCourse) => void;
}

export function CourseCard({ course, onEdit, onDelete, onStats }: Props) {
  const [menuOpen, setMenuOpen] = React.useState(false);

  const levelColor = LEVEL_COLORS[course.level] ?? 'slate';
  const levelLabel = COURSE_LEVEL_LABELS[course.level];
  const title = getCourseTitle(course, 'vi');
  const sectionsCount = course.sections?.length ?? 0;

  return (
    <div className="premium-card group overflow-hidden flex flex-col hover:shadow-xl transition-all duration-300">
      {/* Thumbnail */}
      <div className="relative h-48 bg-gradient-to-br from-slate-100 to-slate-200 dark:from-white/5 dark:to-white/10 overflow-hidden">
        {course.thumbnail_url ? (
          <img
            src={course.thumbnail_url}
            alt={title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <BookOpen size={40} className="text-slate-300 dark:text-white/10" />
          </div>
        )}

        {/* Status badge */}
        <div className="absolute top-3 left-3 flex flex-col gap-1.5">
          <span className={cn(
            "inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-black uppercase tracking-wider",
            course.is_published
              ? "bg-emerald-500/90 text-white shadow-lg"
              : "bg-white/90 dark:bg-black/60 text-slate-700 dark:text-white backdrop-blur-sm shadow-sm"
          )}>
            {course.is_published ? 'Đã đăng' : 'Nháp'}
          </span>
          {course.approval_status && course.approval_status !== 'approved' && (
            <span className={cn(
              "inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-black uppercase tracking-wider",
              course.approval_status === 'pending'
                ? "bg-amber-500/90 text-white shadow-lg"
                : "bg-red-500/90 text-white shadow-lg"
            )}>
              {course.approval_status === 'pending' ? 'Chờ duyệt' : 'Bị từ chối'}
            </span>
          )}
        </div>

        {/* More menu */}
        <div className="absolute top-3 right-3 z-10">
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="w-8 h-8 bg-white/90 dark:bg-black/60 backdrop-blur-sm rounded-xl flex items-center justify-center hover:bg-white transition-colors"
          >
            <MoreVertical size={16} className="text-slate-600 dark:text-white" />
          </button>

          {menuOpen && (
            <>
              <div className="fixed inset-0 z-0" onClick={() => setMenuOpen(false)} />
              <div className="absolute right-0 top-10 w-48 bg-white dark:bg-[#12131e] rounded-2xl shadow-2xl border border-slate-100 dark:border-white/8 py-1 z-20">
                {[
                  { icon: Pencil, label: 'Chỉnh sửa', on: () => { onEdit(course); setMenuOpen(false); } },
                  { icon: BarChart2, label: 'Thống kê', on: () => { onStats?.(course); setMenuOpen(false); } },
                  { icon: ExternalLink, label: 'Xem trước', on: () => { window.open(`/courses/${course.slug}`, '_blank'); setMenuOpen(false); } },
                ].map((item) => (
                  <button
                    key={item.label}
                    onClick={item.on}
                    className="w-full flex items-center gap-3 px-4 py-2.5 text-sm font-semibold text-slate-700 dark:text-slate-300 hover:bg-emerald-50 dark:hover:bg-emerald-500/10 hover:text-emerald-600 transition-colors"
                  >
                    <item.icon size={16} className="text-slate-400" />
                    {item.label}
                  </button>
                ))}
                <div className="border-t border-slate-100 dark:border-white/5 my-1" />
                <button
                  onClick={() => { onDelete(course); setMenuOpen(false); }}
                  className="w-full flex items-center gap-3 px-4 py-2.5 text-sm font-semibold text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors"
                >
                  <Trash2 size={16} />
                  Xóa khóa học
                </button>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="p-5 flex flex-col gap-3 flex-1">
        {/* Title */}
        <h3 className="font-black text-sm text-slate-900 dark:text-white line-clamp-2 leading-tight">
          {title || 'Untitled Course'}
        </h3>

        {/* Instructor */}
        {course.instructor && (
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-emerald-500/10 flex items-center justify-center overflow-hidden">
              {course.instructor.avatar_url ? (
                <img src={course.instructor.avatar_url} alt="" className="w-full h-full object-cover" />
              ) : (
                <Users size={12} className="text-emerald-500" />
              )}
            </div>
            <span className="text-[11px] font-bold text-slate-500 truncate">
              {course.instructor.full_name}
            </span>
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-2 gap-2">
          {[
            { icon: Users, value: formatNumber(course.total_enrolls), label: 'HV' },
            { icon: Eye, value: formatNumber(course.views), label: 'Lượt xem' },
            { icon: Star, value: course.rating_avg > 0 ? course.rating_avg.toFixed(1) : '—', label: 'Đánh giá' },
            { icon: BookOpen, value: `${sectionsCount}/${course.lessons_count}`, label: 'Chương/Bài' },
          ].map((stat) => (
            <div key={stat.label} className="bg-slate-50 dark:bg-white/5 rounded-xl p-2.5 flex items-center gap-2">
              <stat.icon size={14} className="text-slate-400 shrink-0" />
              <span className="text-sm font-black text-slate-700 dark:text-white">{stat.value}</span>
              <span className="text-[10px] font-semibold text-slate-400">{stat.label}</span>
            </div>
          ))}
        </div>

        {/* Price */}
        <div className="flex items-center justify-between pt-2 border-t border-slate-50 dark:border-white/5">
          <span className="text-lg font-black text-emerald-600 dark:text-emerald-400">
            {course.base_price === 0 ? 'Miễn phí' : formatCurrency(course.base_price, course.currency)}
          </span>
          <span className={cn(
            "px-2 py-0.5 rounded-lg text-[10px] font-black uppercase",
            levelColor === 'emerald' && "bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400",
            levelColor === 'amber' && "bg-amber-50 dark:bg-amber-500/10 text-amber-600 dark:text-amber-400",
            levelColor === 'rose' && "bg-rose-50 dark:bg-rose-500/10 text-rose-600 dark:text-rose-400",
          )}>
            {levelLabel}
          </span>
        </div>

        {/* Revenue */}
        <div className="flex items-center justify-between">
          <span className="text-[10px] font-bold text-slate-400">Doanh thu</span>
          <span className="text-sm font-black text-emerald-600 dark:text-emerald-400">
            {formatCurrency(course.revenue)}
          </span>
        </div>
      </div>
    </div>
  );
}
