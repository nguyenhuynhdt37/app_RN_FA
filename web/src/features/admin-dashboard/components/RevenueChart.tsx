'use client';

import React, { useState } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import type { RevenueStats, RevenuePeriod } from '@/types/admin';
import { fmtShort, fmt } from '../types';

interface Props {
  data: RevenueStats;
}

const PERIODS: { key: RevenuePeriod; label: string }[] = [
  { key: 'day', label: 'Ngày' },
  { key: 'week', label: 'Tuần' },
  { key: 'month', label: 'Tháng' },
  { key: 'year', label: 'Năm' },
];

export function RevenueChart({ data }: Props) {
  const [period, setPeriod] = useState<RevenuePeriod>('month');

  const chartData = data.data.map((d) => ({
    name: new Date(d.date + '-01').toLocaleDateString('vi-VN', { month: 'short' }),
    revenue: d.amount,
  }));

  return (
    <div className="premium-card">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h3 className="text-lg font-black text-slate-900 dark:text-white tracking-tight">Doanh thu</h3>
          <p className="text-xs font-bold text-slate-400 uppercase tracking-[2px] mt-1">
            Tổng: {fmtShort(data.total)}
          </p>
        </div>
        <div className="flex gap-1 bg-slate-100 dark:bg-white/5 p-1 rounded-xl">
          {PERIODS.map((p) => (
            <button
              key={p.key}
              onClick={() => setPeriod(p.key)}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                period === p.key
                  ? 'bg-white dark:bg-emerald-500 text-emerald-600 dark:text-white shadow-sm'
                  : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Summary pills */}
      <div className="flex gap-3 mb-6">
        {[
          { label: 'Nền tảng', value: fmtShort(data.platform_income), style: 'text-emerald-600 bg-emerald-50 dark:bg-emerald-500/10 dark:text-emerald-400' },
          { label: 'Giảng viên', value: fmtShort(data.instructor_payout), style: 'text-blue-600 bg-blue-50 dark:bg-blue-500/10 dark:text-blue-400' },
        ].map((s) => (
          <div key={s.label} className={`flex-1 rounded-2xl px-4 py-3 ${s.style}`}>
            <p className="text-xs font-semibold opacity-70">{s.label}</p>
            <p className="font-black text-sm mt-0.5">{s.value}</p>
          </div>
        ))}
      </div>

      <div className="h-52">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis
              dataKey="name"
              tick={{ fontSize: 11, fill: '#94a3b8', fontWeight: 600 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tick={{ fontSize: 11, fill: '#94a3b8', fontWeight: 600 }}
              axisLine={false}
              tickLine={false}
              tickFormatter={fmtShort}
            />
            <Tooltip
              contentStyle={{ background: '#0f172a', border: 'none', borderRadius: 12, color: '#fff', fontSize: 12 }}
              formatter={(v) => [fmt(Number(v ?? 0)), 'Doanh thu']}
            />
            <Line
              type="monotone"
              dataKey="revenue"
              stroke="#10b981"
              strokeWidth={3}
              dot={{ fill: '#10b981', r: 4, strokeWidth: 2, stroke: '#fff' }}
              activeDot={{ r: 6, fill: '#10b981', stroke: '#fff', strokeWidth: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
