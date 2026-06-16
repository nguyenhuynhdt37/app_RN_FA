'use client';

import React, { useState } from 'react';
import { CreditCard, TrendingUp, TrendingDown, Search, ChevronLeft, ChevronRight } from 'lucide-react';
import type { Transaction } from '@/types/admin';

const MOCK: Transaction[] = Array.from({ length: 30 }, (_, i) => ({
  id: String(i + 1),
  user_id: String(i + 1),
  user_name: ['Nguyễn Văn A', 'Trần Thị B', 'Lê Văn C', 'Phạm Thị D'][i % 4],
  type: (['purchase', 'refund', 'withdrawal', 'deposit'] as const)[i % 4],
  amount: [350_000, 99_000, 500_000, 200_000][i % 4],
  status: (['completed', 'pending', 'failed', 'completed'] as const)[i % 4],
  description: ['Mua khóa học React', 'Hoàn tiền', 'Rút tiền', 'Nạp ví'][i % 4],
  created_at: new Date(Date.now() - i * 86400_000).toISOString(),
}));

const STATUS_STYLES: Record<string, string> = {
  completed: 'bg-emerald-50 text-emerald-600',
  pending: 'bg-amber-50 text-amber-600',
  failed: 'bg-red-50 text-red-600',
  cancelled: 'bg-slate-100 text-slate-500',
};
const STATUS_LABELS: Record<string, string> = { completed: 'Hoàn thành', pending: 'Chờ xử lý', failed: 'Thất bại', cancelled: 'Đã hủy' };
const TYPE_LABELS: Record<string, string> = { purchase: 'Mua hàng', refund: 'Hoàn tiền', withdrawal: 'Rút tiền', deposit: 'Nạp tiền' };
const fmtVND = (n: number) => new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND', maximumFractionDigits: 0 }).format(n);
const fmtDate = (s: string) => new Date(s).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });

const PAGE_SIZE = 10;

export function TransactionsView() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('');

  const filtered = MOCK.filter((t) => {
    if (search && !t.user_name.toLowerCase().includes(search.toLowerCase())) return false;
    if (typeFilter && t.type !== typeFilter) return false;
    return true;
  });

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const pageData = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  const totalRevenue = MOCK.filter((t) => t.type === 'purchase' && t.status === 'completed').reduce((s, t) => s + t.amount, 0);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-black text-slate-900 dark:text-white tracking-tight">Giao dịch</h1>
        <p className="text-slate-500 font-semibold mt-1">{MOCK.length} giao dịch</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        {[
          { label: 'Tổng doanh thu', value: fmtVND(totalRevenue), icon: TrendingUp, color: 'bg-emerald-500' },
          { label: 'Chờ xử lý', value: String(MOCK.filter((t) => t.status === 'pending').length), icon: CreditCard, color: 'bg-amber-500' },
          { label: 'Thất bại', value: String(MOCK.filter((t) => t.status === 'failed').length), icon: TrendingDown, color: 'bg-red-500' },
        ].map((s) => (
          <div key={s.label} className="premium-card flex items-center gap-4">
            <div className={`w-12 h-12 ${s.color} rounded-2xl flex items-center justify-center shrink-0`}>
              <s.icon size={20} className="text-white" />
            </div>
            <div>
              <p className="text-[10px] font-black text-slate-400 uppercase tracking-[2px]">{s.label}</p>
              <p className="text-xl font-black text-slate-900 dark:text-white">{s.value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="premium-card flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-48">
          <Search size={15} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Tìm người dùng..."
            className="w-full pl-10 pr-4 py-2.5 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/8 rounded-2xl text-sm font-semibold outline-none focus:border-emerald-400 transition-colors"
          />
        </div>
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="px-4 py-2.5 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/8 rounded-2xl text-sm font-semibold outline-none focus:border-emerald-400 transition-colors"
        >
          <option value="">Tất cả loại</option>
          <option value="purchase">Mua hàng</option>
          <option value="refund">Hoàn tiền</option>
          <option value="withdrawal">Rút tiền</option>
          <option value="deposit">Nạp tiền</option>
        </select>
      </div>

      {/* Table */}
      <div className="premium-card p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-100 dark:border-white/5">
                {['#', 'Người dùng', 'Loại', 'Số tiền', 'Mô tả', 'Trạng thái', 'Ngày'].map((col) => (
                  <th key={col} className="px-6 py-4 text-left text-[10px] font-black text-slate-400 uppercase tracking-[2px]">{col}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50 dark:divide-white/3">
              {pageData.map((t, idx) => (
                <tr key={t.id} className="hover:bg-slate-50/50 dark:hover:bg-white/2 transition-colors">
                  <td className="px-6 py-4 text-sm font-bold text-slate-400">{(page - 1) * PAGE_SIZE + idx + 1}</td>
                  <td className="px-6 py-4 font-bold text-sm text-slate-900 dark:text-white">{t.user_name}</td>
                  <td className="px-6 py-4">
                    <span className="px-3 py-1 rounded-full text-[10px] font-black bg-blue-50 dark:bg-blue-500/10 text-blue-700 dark:text-blue-400 uppercase tracking-wider">{TYPE_LABELS[t.type]}</span>
                  </td>
                  <td className={`px-6 py-4 font-black text-sm ${t.type === 'refund' || t.type === 'withdrawal' ? 'text-red-500' : 'text-emerald-600'}`}>
                    {t.type === 'refund' || t.type === 'withdrawal' ? '-' : '+'}{fmtVND(t.amount)}
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-500">{t.description}</td>
                  <td className="px-6 py-4">
                    <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider ${STATUS_STYLES[t.status]}`}>{STATUS_LABELS[t.status]}</span>
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-400 font-medium">{fmtDate(t.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="px-6 py-5 border-t border-slate-100 dark:border-white/5 flex items-center justify-between">
          <p className="text-sm font-semibold text-slate-500">{filtered.length} kết quả · Trang {page}/{totalPages}</p>
          <div className="flex items-center gap-2">
            <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1} className="p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-white/5 text-slate-500 disabled:opacity-30 transition-all"><ChevronLeft size={18} /></button>
            <button onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page === totalPages} className="p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-white/5 text-slate-500 disabled:opacity-30 transition-all"><ChevronRight size={18} /></button>
          </div>
        </div>
      </div>
    </div>
  );
}
