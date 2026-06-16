'use client';

import React from 'react';
import { BookOpen, Users, Currency, Star } from 'lucide-react';
import { formatCurrency, formatNumber } from '../types';

interface Props {
  totalCourses: number;
  totalEnrolls: number;
  totalRevenue: number;
  avgRating: number;
}

export function CourseStatsCards({ totalCourses, totalEnrolls, totalRevenue, avgRating }: Props) {
  const stats = [
    {
      label: 'Tổng khóa học',
      value: totalCourses,
      icon: BookOpen,
      gradient: 'from-green-400 to-emerald-500',
    },
    {
      label: 'Tổng học viên',
      value: formatNumber(totalEnrolls),
      icon: Users,
      gradient: 'from-emerald-400 to-teal-500',
    },
    {
      label: 'Tổng doanh thu',
      value: formatCurrency(totalRevenue),
      icon: Currency,
      gradient: 'from-teal-400 to-cyan-500',
    },
    {
      label: 'Đánh giá TB',
      value: avgRating > 0 ? avgRating.toFixed(1) : '—',
      icon: Star,
      gradient: 'from-cyan-400 to-blue-500',
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
      {stats.map((stat) => (
        <div
          key={stat.label}
          className="premium-card group flex flex-col gap-4"
        >
          <div
            className={`w-12 h-12 rounded-2xl bg-gradient-to-br ${stat.gradient} flex items-center justify-center shadow-lg transition-transform group-hover:scale-110`}
          >
            <stat.icon size={22} className="text-white" />
          </div>
          <div>
            <p className="text-[10px] font-black text-slate-400 uppercase tracking-[2px] mb-1.5">
              {stat.label}
            </p>
            <p className="text-2xl font-black text-slate-900 dark:text-white tracking-tight">
              {stat.value}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
