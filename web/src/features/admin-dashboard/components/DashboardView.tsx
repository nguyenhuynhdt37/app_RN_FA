'use client';

import React, { useState } from 'react';
import { Download, RotateCcw, Users, BookOpen, GraduationCap, DollarSign, TrendingUp, ArrowUpRight, RefreshCw } from 'lucide-react';
import { StatCard } from './StatCard';
import { RevenueChart } from './RevenueChart';
import { CategoryChart } from './CategoryChart';
import { TopCoursesTable } from './TopCoursesTable';
import { TopInstructorsTable } from './TopInstructorsTable';
import { MOCK_STATS, MOCK_REVENUE, MOCK_TOP_COURSES, MOCK_TOP_INSTRUCTORS, fmtShort } from '../types';

export function DashboardView() {
  const [stats] = useState(MOCK_STATS);
  const [revenue] = useState(MOCK_REVENUE);

  const STAT_CARDS = [
    { label: 'Người dùng', value: stats.total_users.toLocaleString('vi-VN'), icon: Users, iconBg: 'bg-blue-500' },
    { label: 'Khóa học', value: stats.total_courses.toLocaleString('vi-VN'), icon: BookOpen, iconBg: 'bg-violet-500' },
    { label: 'Giảng viên', value: stats.total_instructors.toLocaleString('vi-VN'), icon: GraduationCap, iconBg: 'bg-amber-500' },
    { label: 'Tổng doanh thu', value: fmtShort(stats.total_revenue), icon: DollarSign, iconBg: 'bg-emerald-500' },
    { label: 'Doanh thu hôm nay', value: fmtShort(stats.today_revenue), icon: TrendingUp, iconBg: 'bg-emerald-600' },
    { label: 'Chờ rút tiền', value: stats.pending_withdrawals.toString(), icon: ArrowUpRight, iconBg: 'bg-orange-500', badge: { text: 'Cần duyệt' } },
    { label: 'Chờ hoàn tiền', value: stats.pending_refunds.toString(), icon: RefreshCw, iconBg: 'bg-red-500', badge: { text: 'Khẩn', urgent: true } },
  ] as const;

  return (
    <div className="space-y-8">
      {/* Hero banner */}
      <div className="relative overflow-hidden rounded-[32px] bg-gradient-to-br from-emerald-500 via-teal-500 to-cyan-500 p-8 text-white shadow-2xl shadow-emerald-500/20">
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-24 -right-24 w-64 h-64 bg-white/10 rounded-full blur-3xl" />
          <div className="absolute -bottom-16 -left-16 w-48 h-48 bg-white/10 rounded-full blur-2xl" />
        </div>
        <div className="relative z-10 flex items-center justify-between">
          <div>
            <p className="text-white/70 text-sm font-semibold mb-1">Chào buổi tối 👋</p>
            <h1 className="text-3xl font-black tracking-tighter mb-2">Tổng quan hệ thống</h1>
            <p className="text-white/80 text-base">Dashboard quản trị NeuralEarn — dữ liệu thời gian thực</p>
          </div>
          <div className="hidden md:flex items-center gap-3">
            <button className="flex items-center gap-2 bg-white/15 hover:bg-white/25 backdrop-blur-sm px-5 py-2.5 rounded-2xl transition-all font-semibold text-sm hover:scale-105 active:scale-95">
              <RotateCcw size={16} />Làm mới
            </button>
            <button className="flex items-center gap-2 bg-white/15 hover:bg-white/25 backdrop-blur-sm px-5 py-2.5 rounded-2xl transition-all font-semibold text-sm hover:scale-105 active:scale-95">
              <Download size={16} />Xuất báo cáo
            </button>
          </div>
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-7 gap-4">
        {STAT_CARDS.map((s) => (
          <StatCard key={s.label} {...s} />
        ))}
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <RevenueChart data={revenue} />
        </div>
        <CategoryChart />
      </div>

      {/* Tables row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <TopCoursesTable courses={MOCK_TOP_COURSES} />
        <TopInstructorsTable instructors={MOCK_TOP_INSTRUCTORS} />
      </div>
    </div>
  );
}
