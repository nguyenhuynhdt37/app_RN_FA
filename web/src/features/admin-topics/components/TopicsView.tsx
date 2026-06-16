'use client';

import React, { useState } from 'react';
import { Plus, Search, Edit2, Trash2, FileText, Folder } from 'lucide-react';
import type { Topic } from '@/types/admin';

const MOCK: Topic[] = [
  { id: '1', name: 'React Native', category_id: '1', category_name: 'Lập trình', course_count: 24, created_at: '2024-01-10T00:00:00Z' },
  { id: '2', name: 'Python', category_id: '1', category_name: 'Lập trình', course_count: 31, created_at: '2024-01-12T00:00:00Z' },
  { id: '3', name: 'FastAPI', category_id: '1', category_name: 'Lập trình', course_count: 18, created_at: '2024-02-01T00:00:00Z' },
  { id: '4', name: 'UI/UX Design', category_id: '2', category_name: 'Thiết kế', course_count: 22, created_at: '2024-01-15T00:00:00Z' },
  { id: '5', name: 'Figma', category_id: '2', category_name: 'Thiết kế', course_count: 14, created_at: '2024-02-10T00:00:00Z' },
  { id: '6', name: 'SEO', category_id: '3', category_name: 'Marketing', course_count: 19, created_at: '2024-03-01T00:00:00Z' },
];

export function TopicsView() {
  const [search, setSearch] = useState('');
  const filtered = MOCK.filter((t) =>
    t.name.toLowerCase().includes(search.toLowerCase()) ||
    t.category_name.toLowerCase().includes(search.toLowerCase())
  );

  const grouped = filtered.reduce<Record<string, Topic[]>>((acc, t) => {
    (acc[t.category_name] ??= []).push(t);
    return acc;
  }, {});

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-black text-slate-900 dark:text-white tracking-tight">Chủ đề</h1>
          <p className="text-slate-500 font-semibold mt-1">{MOCK.length} chủ đề</p>
        </div>
        <button className="flex items-center gap-2 px-5 py-2.5 bg-emerald-500 text-white font-bold text-sm rounded-2xl hover:bg-emerald-600 shadow-lg shadow-emerald-500/20 transition-all hover:scale-105 active:scale-95">
          <Plus size={16} />Thêm chủ đề
        </button>
      </div>

      <div className="premium-card">
        <div className="relative max-w-md">
          <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Tìm chủ đề hoặc danh mục..."
            className="w-full pl-10 pr-4 py-3 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/8 rounded-2xl text-sm font-semibold outline-none focus:border-emerald-400 transition-colors"
          />
        </div>
      </div>

      <div className="space-y-6">
        {Object.entries(grouped).map(([catName, topics]) => (
          <div key={catName}>
            <div className="flex items-center gap-2 mb-3">
              <Folder size={16} className="text-emerald-500" />
              <h3 className="font-black text-slate-700 dark:text-slate-300 text-sm uppercase tracking-[2px]">{catName}</h3>
              <div className="flex-1 h-px bg-slate-100 dark:bg-white/5" />
              <span className="text-xs font-bold text-slate-400">{topics.length}</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
              {topics.map((t) => (
                <div key={t.id} className="premium-card group flex items-center gap-3 p-4">
                  <div className="w-10 h-10 rounded-xl bg-blue-50 dark:bg-blue-500/10 flex items-center justify-center shrink-0 group-hover:scale-110 transition-transform">
                    <FileText size={16} className="text-blue-500" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-bold text-slate-900 dark:text-white text-sm truncate">{t.name}</p>
                    <p className="text-xs text-slate-400">{t.course_count} khóa học</p>
                  </div>
                  <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
                    <button className="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-white/5 text-slate-400 hover:text-emerald-600 transition-colors"><Edit2 size={13} /></button>
                    <button className="p-1.5 rounded-lg hover:bg-red-50 dark:hover:bg-red-500/10 text-slate-400 hover:text-red-500 transition-colors"><Trash2 size={13} /></button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
