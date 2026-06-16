'use client';

import React, { useState } from 'react';
import { Wallet as WalletIcon, TrendingUp, ArrowUpRight, Search } from 'lucide-react';
import type { Wallet } from '@/types/admin';

const MOCK: Wallet[] = Array.from({ length: 12 }, (_, i) => ({
  id: String(i + 1),
  user_id: String(i + 1),
  user_name: ['Nguyễn Văn A', 'Trần Thị B', 'Lê Văn C', 'Phạm Thị D'][i % 4],
  user_email: `user${i + 1}@example.com`,
  balance: Math.floor(Math.random() * 5_000_000),
  total_earned: Math.floor(Math.random() * 50_000_000) + 10_000_000,
  total_withdrawn: Math.floor(Math.random() * 20_000_000),
  updated_at: new Date(Date.now() - i * 3600_000).toISOString(),
}));

const fmtVND = (n: number) => new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND', maximumFractionDigits: 0 }).format(n);
const fmtShort = (n: number) => n >= 1_000_000 ? `${(n / 1_000_000).toFixed(1)}M` : `${(n / 1_000).toFixed(0)}K`;

export function WalletsView() {
  const [search, setSearch] = useState('');
  const filtered = MOCK.filter((w) =>
    w.user_name.toLowerCase().includes(search.toLowerCase()) || w.user_email.includes(search)
  );
  const totalBalance = MOCK.reduce((s, w) => s + w.balance, 0);
  const totalEarned = MOCK.reduce((s, w) => s + w.total_earned, 0);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-black text-slate-900 dark:text-white tracking-tight">Quản lý Ví</h1>
        <p className="text-slate-500 font-semibold mt-1">{MOCK.length} ví đang hoạt động</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        {[
          { label: 'Tổng số dư', value: fmtVND(totalBalance), icon: WalletIcon, color: 'bg-emerald-500' },
          { label: 'Tổng thu nhập', value: fmtVND(totalEarned), icon: TrendingUp, color: 'bg-blue-500' },
          { label: 'Chờ rút', value: '14 yêu cầu', icon: ArrowUpRight, color: 'bg-amber-500' },
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

      <div className="premium-card">
        <div className="relative max-w-md">
          <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Tìm người dùng..."
            className="w-full pl-10 pr-4 py-3 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/8 rounded-2xl text-sm font-semibold outline-none focus:border-emerald-400 transition-colors"
          />
        </div>
      </div>

      <div className="premium-card p-0 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-100 dark:border-white/5">
              {['#', 'Người dùng', 'Số dư', 'Tổng thu', 'Đã rút', 'Tỷ lệ rút', 'Cập nhật'].map((col) => (
                <th key={col} className="px-6 py-4 text-left text-[10px] font-black text-slate-400 uppercase tracking-[2px]">{col}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50 dark:divide-white/3">
            {filtered.map((w, idx) => {
              const pct = w.total_earned > 0 ? (w.total_withdrawn / w.total_earned) * 100 : 0;
              return (
                <tr key={w.id} className="hover:bg-slate-50/50 dark:hover:bg-white/2 transition-colors">
                  <td className="px-6 py-4 text-sm font-bold text-slate-400">{idx + 1}</td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-white font-black text-sm">
                        {w.user_name[0]}
                      </div>
                      <div>
                        <p className="font-bold text-sm text-slate-900 dark:text-white">{w.user_name}</p>
                        <p className="text-xs text-slate-400">{w.user_email}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 font-black text-emerald-600 text-sm">{fmtVND(w.balance)}</td>
                  <td className="px-6 py-4 font-bold text-sm text-slate-700 dark:text-slate-300">{fmtShort(w.total_earned)} ₫</td>
                  <td className="px-6 py-4 font-bold text-sm text-slate-500">{fmtShort(w.total_withdrawn)} ₫</td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 bg-slate-100 dark:bg-white/10 rounded-full overflow-hidden">
                        <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${pct}%` }} />
                      </div>
                      <span className="text-xs font-bold text-slate-400">{pct.toFixed(0)}%</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-xs text-slate-400">{new Date(w.updated_at).toLocaleDateString('vi-VN')}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
