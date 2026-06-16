'use client';

import React, { useState } from 'react';
import { Plus, Search, Edit2, Trash2, GraduationCap, Star, BookOpen, Users } from 'lucide-react';
import type { Lecturer } from '@/types/admin';

const MOCK: Lecturer[] = [
  { id: '1', fullname: 'Nguyễn Văn Anh', email: 'anh.nguyen@edu.vn', avatar: null, total_courses: 12, total_students: 4820, total_revenue: 245_000_000, rating: 4.9, is_verified: true, created_at: '2024-01-10T00:00:00Z' },
  { id: '2', fullname: 'Trần Thị Bình', email: 'binh.tran@edu.vn', avatar: null, total_courses: 8, total_students: 3214, total_revenue: 187_000_000, rating: 4.8, is_verified: true, created_at: '2024-02-01T00:00:00Z' },
  { id: '3', fullname: 'Lê Minh Châu', email: 'chau.le@edu.vn', avatar: null, total_courses: 5, total_students: 1876, total_revenue: 98_000_000, rating: 4.6, is_verified: false, created_at: '2024-03-15T00:00:00Z' },
  { id: '4', fullname: 'Phạm Quốc Dũng', email: 'dung.pham@edu.vn', avatar: null, total_courses: 9, total_students: 2540, total_revenue: 132_000_000, rating: 4.7, is_verified: true, created_at: '2024-04-01T00:00:00Z' },
];

const fmtVND = (n: number) => n >= 1_000_000 ? `${(n / 1_000_000).toFixed(1)}M ₫` : `${n} ₫`;

function LecturerCard({ l }: { l: Lecturer }) {
  return (
    <div className="premium-card group">
      <div className="flex items-start gap-4 mb-5">
        <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-violet-400 to-purple-500 flex items-center justify-center text-white font-black text-xl shrink-0">
          {l.fullname[0]}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="font-black text-slate-900 dark:text-white truncate">{l.fullname}</h3>
            {l.is_verified && (
              <span className="w-5 h-5 rounded-full bg-emerald-500 flex items-center justify-center shrink-0">
                <GraduationCap size={10} className="text-white" />
              </span>
            )}
          </div>
          <p className="text-xs text-slate-400 truncate">{l.email}</p>
        </div>
        <button className="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-white/5 text-slate-400 hover:text-emerald-600 opacity-0 group-hover:opacity-100 transition-all">
          <Edit2 size={14} />
        </button>
      </div>

      <div className="grid grid-cols-3 gap-3 mb-4">
        {[
          { icon: BookOpen, label: 'Khóa học', value: l.total_courses },
          { icon: Users, label: 'Học viên', value: l.total_students.toLocaleString('vi-VN') },
          { icon: Star, label: 'Đánh giá', value: l.rating.toFixed(1) },
        ].map((s) => (
          <div key={s.label} className="bg-slate-50 dark:bg-white/3 rounded-xl p-3 text-center">
            <s.icon size={14} className="text-emerald-500 mx-auto mb-1" />
            <p className="font-black text-slate-900 dark:text-white text-sm">{s.value}</p>
            <p className="text-[9px] text-slate-400 font-semibold uppercase tracking-wider">{s.label}</p>
          </div>
        ))}
      </div>

      <div className="pt-4 border-t border-slate-100 dark:border-white/5 flex items-center justify-between">
        <span className="text-xs text-slate-400 font-semibold">Doanh thu</span>
        <span className="font-black text-emerald-600 text-sm">{fmtVND(l.total_revenue)}</span>
      </div>
    </div>
  );
}

export function LecturersView() {
  const [search, setSearch] = useState('');
  const filtered = MOCK.filter((l) =>
    l.fullname.toLowerCase().includes(search.toLowerCase()) || l.email.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-black text-slate-900 dark:text-white tracking-tight">Giảng viên</h1>
          <p className="text-slate-500 font-semibold mt-1">{MOCK.length} giảng viên đang hoạt động</p>
        </div>
        <button className="flex items-center gap-2 px-5 py-2.5 bg-emerald-500 text-white font-bold text-sm rounded-2xl hover:bg-emerald-600 shadow-lg shadow-emerald-500/20 transition-all hover:scale-105 active:scale-95">
          <Plus size={16} />Thêm giảng viên
        </button>
      </div>

      <div className="premium-card">
        <div className="relative max-w-md">
          <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Tìm giảng viên..."
            className="w-full pl-10 pr-4 py-3 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/8 rounded-2xl text-sm font-semibold outline-none focus:border-emerald-400 transition-colors"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
        {filtered.map((l) => <LecturerCard key={l.id} l={l} />)}
      </div>
    </div>
  );
}
