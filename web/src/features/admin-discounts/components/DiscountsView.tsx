'use client';

import React, { useState } from 'react';
import { Plus, Tag, Edit2, Trash2, ToggleLeft, ToggleRight, Search } from 'lucide-react';
import type { Discount } from '@/types/admin';

const MOCK: Discount[] = [
  { id: '1', code: 'LAUNCH2025', type: 'percentage', value: 30, max_uses: 500, used_count: 234, expires_at: '2025-12-31T23:59:59Z', is_active: true, created_at: '2025-01-01T00:00:00Z' },
  { id: '2', code: 'SUMMER50K', type: 'fixed', value: 50_000, max_uses: 200, used_count: 87, expires_at: '2025-08-31T23:59:59Z', is_active: true, created_at: '2025-06-01T00:00:00Z' },
  { id: '3', code: 'NEWBIE', type: 'percentage', value: 20, max_uses: 1000, used_count: 543, expires_at: null, is_active: true, created_at: '2024-12-01T00:00:00Z' },
  { id: '4', code: 'HOLIDAY100K', type: 'fixed', value: 100_000, max_uses: 100, used_count: 100, expires_at: '2025-01-01T00:00:00Z', is_active: false, created_at: '2024-12-20T00:00:00Z' },
];

const fmtValue = (d: Discount) => d.type === 'percentage' ? `${d.value}%` : `${(d.value / 1000).toFixed(0)}K ₫`;
const fmtDate = (s: string | null) => s ? new Date(s).toLocaleDateString('vi-VN') : '∞';

function DiscountCard({ d }: { d: Discount }) {
  return (
    <div className={`premium-card group ${!d.is_active ? 'opacity-60' : ''}`}>
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`w-11 h-11 rounded-2xl flex items-center justify-center ${d.is_active ? 'bg-violet-50 dark:bg-violet-500/10' : 'bg-slate-100 dark:bg-white/5'}`}>
            <Tag size={18} className={d.is_active ? 'text-violet-500' : 'text-slate-400'} />
          </div>
          <div>
            <h3 className="font-black text-slate-900 dark:text-white font-mono tracking-wider">{d.code}</h3>
            <span className={`text-[10px] font-black px-2 py-0.5 rounded-full ${d.type === 'percentage' ? 'bg-violet-50 dark:bg-violet-500/10 text-violet-600 dark:text-violet-400' : 'bg-blue-50 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400'}`}>
              {d.type === 'percentage' ? 'Phần trăm' : 'Cố định'}
            </span>
          </div>
        </div>
        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button className="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-white/5 text-slate-400 hover:text-emerald-600 transition-colors"><Edit2 size={14} /></button>
          <button className="p-1.5 rounded-lg hover:bg-red-50 dark:hover:bg-red-500/10 text-slate-400 hover:text-red-500 transition-colors"><Trash2 size={14} /></button>
        </div>
      </div>

      <div className="flex items-center justify-between mb-4">
        <span className="text-3xl font-black text-violet-600 dark:text-violet-400">{fmtValue(d)}</span>
        {d.is_active ? <ToggleRight size={28} className="text-emerald-500 cursor-pointer" /> : <ToggleLeft size={28} className="text-slate-400 cursor-pointer" />}
      </div>

      <div className="grid grid-cols-3 gap-3 text-center mb-4">
        {[
          { label: 'Đã dùng', value: `${d.used_count}/${d.max_uses}` },
          { label: 'Hết hạn', value: fmtDate(d.expires_at) },
          { label: 'Còn lại', value: String(Math.max(0, d.max_uses - d.used_count)) },
        ].map((s) => (
          <div key={s.label} className="bg-slate-50 dark:bg-white/3 rounded-xl p-2">
            <p className="font-black text-slate-900 dark:text-white text-sm">{s.value}</p>
            <p className="text-[9px] text-slate-400 font-semibold uppercase tracking-wider">{s.label}</p>
          </div>
        ))}
      </div>

      <div className="w-full h-1.5 bg-slate-100 dark:bg-white/10 rounded-full overflow-hidden">
        <div
          className="h-full bg-violet-500 rounded-full transition-all"
          style={{ width: `${Math.min(100, (d.used_count / d.max_uses) * 100)}%` }}
        />
      </div>
    </div>
  );
}

export function DiscountsView() {
  const [search, setSearch] = useState('');
  const filtered = MOCK.filter((d) => d.code.toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-black text-slate-900 dark:text-white tracking-tight">Mã giảm giá</h1>
          <p className="text-slate-500 font-semibold mt-1">{MOCK.filter((d) => d.is_active).length} mã đang hoạt động</p>
        </div>
        <button className="flex items-center gap-2 px-5 py-2.5 bg-emerald-500 text-white font-bold text-sm rounded-2xl hover:bg-emerald-600 shadow-lg shadow-emerald-500/20 transition-all hover:scale-105 active:scale-95">
          <Plus size={16} />Tạo mã mới
        </button>
      </div>

      <div className="premium-card">
        <div className="relative max-w-md">
          <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Tìm mã..."
            className="w-full pl-10 pr-4 py-3 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/8 rounded-2xl text-sm font-semibold outline-none focus:border-emerald-400 transition-colors"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {filtered.map((d) => <DiscountCard key={d.id} d={d} />)}
      </div>
    </div>
  );
}
