'use client';

import React from 'react';
import { PieChart, Pie, Cell, Legend, Tooltip, ResponsiveContainer } from 'recharts';
import { MOCK_CATEGORIES, PIE_COLORS } from '../types';

export function CategoryChart() {
  const data = MOCK_CATEGORIES.map((c, i) => ({
    name: c.name,
    value: c.course_count,
    fill: PIE_COLORS[i % PIE_COLORS.length],
  }));

  return (
    <div className="premium-card">
      <h3 className="text-lg font-black text-slate-900 dark:text-white tracking-tight mb-1">Danh mục</h3>
      <p className="text-xs font-bold text-slate-400 uppercase tracking-[2px] mb-6">Phân bổ khóa học</p>
      <div className="h-52">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={50}
              outerRadius={80}
              dataKey="value"
              paddingAngle={3}
            >
              {data.map((entry, i) => (
                <Cell key={i} fill={entry.fill} />
              ))}
            </Pie>
            <Legend
              formatter={(v) => (
                <span style={{ fontSize: 11, fontWeight: 700, color: '#64748b' }}>{v}</span>
              )}
              iconType="circle"
              iconSize={8}
            />
            <Tooltip
              contentStyle={{ background: '#0f172a', border: 'none', borderRadius: 12, color: '#fff', fontSize: 12 }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
