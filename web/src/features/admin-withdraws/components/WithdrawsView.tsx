'use client';

import React, { useState } from 'react';
import { ArrowUpRight, Check, X, Clock, AlertCircle, Search } from 'lucide-react';
import type { Withdrawal } from '@/types/admin';

const MOCK: Withdrawal[] = Array.from({ length: 14 }, (_, i) => ({
  id: String(i + 1),
  user_id: String(i + 1),
  user_name: ['Nguyễn Văn A', 'Trần Thị B', 'Lê Minh C'][i % 3],
  amount: [1_000_000, 2_500_000, 500_000, 5_000_000][i % 4],
  bank_account: `****${4000 + i}`,
  bank_name: ['Vietcombank', 'Techcombank', 'MB Bank'][i % 3],
  status: (['pending', 'approved', 'completed', 'rejected'] as const)[i % 4],
  created_at: new Date(Date.now() - i * 86400_000).toISOString(),
}));

const STATUS: Record<string, { label: string; style: string }> = {
  pending: { label: 'Chờ duyệt', style: 'bg-amber-50 text-amber-600 dark:bg-amber-500/10 dark:text-amber-400' },
  approved: { label: 'Đã duyệt', style: 'bg-blue-50 text-blue-600 dark:bg-blue-500/10 dark:text-blue-400' },
  completed: { label: 'Hoàn thành', style: 'bg-emerald-50 text-emerald-600 dark:bg-emerald-500/10 dark:text-emerald-400' },
  rejected: { label: 'Từ chối', style: 'bg-red-50 text-red-600 dark:bg-red-500/10 dark:text-red-400' },
};
const fmtVND = (n: number) => new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND', maximumFractionDigits: 0 }).format(n);

export function WithdrawsView() {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const pending = MOCK.filter((w) => w.status === 'pending');
  const totalPending = pending.reduce((s, w) => s + w.amount, 0);

  const filtered = MOCK.filter((w) => {
    if (search && !w.user_name.toLowerCase().includes(search.toLowerCase())) return false;
    if (statusFilter && w.status !== statusFilter) return false;
    return true;
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-black text-slate-900 dark:text-white tracking-tight">Yêu cầu rút tiền</h1>
          <p className="text-slate-500 font-semibold mt-1">{MOCK.length} yêu cầu</p>
        </div>
        {pending.length > 0 && (
          <div className="flex items-center gap-2 px-4 py-2 bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20 rounded-2xl">
            <AlertCircle size={16} className="text-amber-500" />
            <span className="text-sm font-bold text-amber-700 dark:text-amber-400">
              {pending.length} chờ duyệt · {fmtVND(totalPending)}
            </span>
          </div>
        )}
      </div>

      <div className="premium-card flex gap-3">
        <div className="relative flex-1">
          <Search size={15} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Tìm người dùng..."
            className="w-full pl-10 pr-4 py-2.5 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/8 rounded-2xl text-sm font-semibold outline-none focus:border-emerald-400 transition-colors"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-4 py-2.5 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/8 rounded-2xl text-sm font-semibold outline-none focus:border-emerald-400 transition-colors"
        >
          <option value="">Tất cả</option>
          <option value="pending">Chờ duyệt</option>
          <option value="approved">Đã duyệt</option>
          <option value="completed">Hoàn thành</option>
          <option value="rejected">Từ chối</option>
        </select>
      </div>

      <div className="space-y-3">
        {filtered.map((w) => {
          const s = STATUS[w.status];
          return (
            <div key={w.id} className="premium-card flex items-center gap-4 group">
              <div className="w-10 h-10 rounded-2xl bg-orange-50 dark:bg-orange-500/10 flex items-center justify-center shrink-0">
                <ArrowUpRight size={18} className="text-orange-500" />
              </div>
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-white font-black text-sm shrink-0">
                {w.user_name[0]}
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-bold text-sm text-slate-900 dark:text-white">{w.user_name}</p>
                <p className="text-xs text-slate-400">{w.bank_name} · {w.bank_account}</p>
              </div>
              <div className="text-right">
                <p className="font-black text-orange-500 text-sm">{fmtVND(w.amount)}</p>
                <p className="text-xs text-slate-400">{new Date(w.created_at).toLocaleDateString('vi-VN')}</p>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider ${s.style}`}>{s.label}</span>
                {w.status === 'pending' && (
                  <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button className="px-3 py-1.5 rounded-xl bg-emerald-500 text-white text-xs font-bold hover:bg-emerald-600 flex items-center gap-1">
                      <Check size={12} />Duyệt
                    </button>
                    <button className="px-3 py-1.5 rounded-xl bg-red-50 dark:bg-red-500/10 text-red-600 text-xs font-bold hover:bg-red-100 flex items-center gap-1">
                      <X size={12} />Từ chối
                    </button>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
