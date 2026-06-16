'use client';

import React, { useState } from 'react';
import { Check, X, Clock, AlertCircle, Search, CheckCircle, XCircle } from 'lucide-react';
import type { Refund } from '@/types/admin';

const MOCK: Refund[] = Array.from({ length: 15 }, (_, i) => ({
  id: String(i + 1),
  user_id: String(i + 1),
  user_name: ['Nguyễn Văn A', 'Trần Thị B', 'Lê Văn C'][i % 3],
  course_title: ['React Native Mastery', 'FastAPI Pro', 'UI/UX Fundamentals', 'Python Data Science'][i % 4],
  amount: [350_000, 199_000, 499_000][i % 3],
  reason: ['Nội dung không phù hợp', 'Lỗi thanh toán', 'Đã mua nhầm'][i % 3],
  status: (['pending', 'approved', 'rejected', 'pending'] as const)[i % 4],
  created_at: new Date(Date.now() - i * 86400_000).toISOString(),
}));

const STATUS_CFG: Record<string, { label: string; style: string; icon: React.ElementType }> = {
  pending: { label: 'Chờ duyệt', style: 'bg-amber-50 text-amber-600 dark:bg-amber-500/10 dark:text-amber-400', icon: Clock },
  approved: { label: 'Đã duyệt', style: 'bg-emerald-50 text-emerald-600 dark:bg-emerald-500/10 dark:text-emerald-400', icon: CheckCircle },
  rejected: { label: 'Từ chối', style: 'bg-red-50 text-red-600 dark:bg-red-500/10 dark:text-red-400', icon: XCircle },
};

const fmtVND = (n: number) =>
  new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND', maximumFractionDigits: 0 }).format(n);

const fmtDate = (s: string) => new Date(s).toLocaleDateString('vi-VN');

export function RefundsView() {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  const pending = MOCK.filter((r) => r.status === 'pending');
  const totalPending = pending.reduce((s, r) => s + r.amount, 0);

  const filtered = MOCK.filter((r) => {
    if (
      search &&
      !r.user_name.toLowerCase().includes(search.toLowerCase()) &&
      !r.course_title.toLowerCase().includes(search.toLowerCase())
    ) {
      return false;
    }
    if (statusFilter && r.status !== statusFilter) return false;
    return true;
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-black text-slate-900 dark:text-white tracking-tight">Hoàn tiền</h1>
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

      <div className="premium-card flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-48">
          <Search size={15} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Tìm người dùng, khóa học..."
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
          <option value="rejected">Từ chối</option>
        </select>
      </div>

      <div className="space-y-3">
        {filtered.map((r) => {
          const cfg = STATUS_CFG[r.status];
          return (
            <div key={r.id} className="premium-card flex items-center gap-4 group">
              <div className={`w-10 h-10 rounded-2xl flex items-center justify-center shrink-0 ${cfg.style}`}>
                <cfg.icon size={18} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <p className="font-bold text-slate-900 dark:text-white text-sm">{r.user_name}</p>
                    <p className="text-xs text-slate-400 truncate">{r.course_title}</p>
                    <p className="text-xs text-slate-500 mt-1 italic">"{r.reason}"</p>
                  </div>
                  <div className="text-right shrink-0">
                    <p className="font-black text-red-500 text-sm">{fmtVND(r.amount)}</p>
                    <p className="text-xs text-slate-400">{fmtDate(r.created_at)}</p>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider ${cfg.style}`}>
                  {cfg.label}
                </span>
                {r.status === 'pending' && (
                  <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button className="px-3 py-1.5 rounded-xl bg-emerald-500 text-white text-xs font-bold hover:bg-emerald-600 transition-colors flex items-center gap-1">
                      <Check size={12} />Duyệt
                    </button>
                    <button className="px-3 py-1.5 rounded-xl bg-red-50 dark:bg-red-500/10 text-red-600 text-xs font-bold hover:bg-red-100 transition-colors flex items-center gap-1">
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
