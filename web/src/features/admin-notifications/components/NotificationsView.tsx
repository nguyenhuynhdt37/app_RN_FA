'use client';

import React, { useState } from 'react';
import { Info, AlertTriangle, CheckCircle, XCircle, Check } from 'lucide-react';
import type { AdminNotification, NotificationLevel } from '@/types/admin';

const MOCK: AdminNotification[] = [
  { id: '1', title: 'Yêu cầu rút tiền mới', message: '3 giảng viên yêu cầu rút tiền với tổng giá trị 8.5M ₫', level: 'warning', is_read: false, created_at: new Date(Date.now() - 600_000).toISOString() },
  { id: '2', title: 'Người dùng bị cấm', message: 'user@example.com đã bị cấm vĩnh viễn do vi phạm điều khoản', level: 'error', is_read: false, created_at: new Date(Date.now() - 3600_000).toISOString() },
  { id: '3', title: 'Khóa học mới được duyệt', message: '"React Native Mastery 2025" đã được phê duyệt và đăng tải', level: 'success', is_read: true, created_at: new Date(Date.now() - 7200_000).toISOString() },
  { id: '4', title: 'Cập nhật hệ thống', message: 'Hệ thống sẽ bảo trì vào 2:00 AM ngày mai trong 30 phút', level: 'info', is_read: true, created_at: new Date(Date.now() - 86400_000).toISOString() },
  { id: '5', title: 'Yêu cầu hoàn tiền khẩn', message: 'Học viên Nguyễn Văn A khiếu nại về khóa học "Python for AI"', level: 'error', is_read: false, created_at: new Date(Date.now() - 1800_000).toISOString() },
];

const LEVEL_CFG: Record<NotificationLevel, { icon: React.ElementType; style: string; bg: string }> = {
  info: { icon: Info, style: 'text-blue-500', bg: 'bg-blue-50 dark:bg-blue-500/10' },
  warning: { icon: AlertTriangle, style: 'text-amber-500', bg: 'bg-amber-50 dark:bg-amber-500/10' },
  error: { icon: XCircle, style: 'text-red-500', bg: 'bg-red-50 dark:bg-red-500/10' },
  success: { icon: CheckCircle, style: 'text-emerald-500', bg: 'bg-emerald-50 dark:bg-emerald-500/10' },
};

const fmtRelative = (s: string) => {
  const m = Math.floor((Date.now() - new Date(s).getTime()) / 60_000);
  if (m < 1) return 'Vừa xong';
  if (m < 60) return `${m} phút trước`;
  if (m < 1440) return `${Math.floor(m / 60)} giờ trước`;
  return `${Math.floor(m / 1440)} ngày trước`;
};

export function NotificationsView() {
  const [items, setItems] = useState(MOCK);
  const unread = items.filter((n) => !n.is_read).length;

  const markRead = (id: string) =>
    setItems((prev) => prev.map((n) => (n.id === id ? { ...n, is_read: true } : n)));
  const markAllRead = () =>
    setItems((prev) => prev.map((n) => ({ ...n, is_read: true })));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-black text-slate-900 dark:text-white tracking-tight">Thông báo</h1>
          <p className="text-slate-500 font-semibold mt-1">
            {unread > 0
              ? <span className="text-emerald-600">{unread} chưa đọc</span>
              : 'Tất cả đã đọc'} · {items.length} tổng
          </p>
        </div>
        {unread > 0 && (
          <button
            onClick={markAllRead}
            className="flex items-center gap-2 px-5 py-2.5 bg-emerald-500 text-white font-bold text-sm rounded-2xl hover:bg-emerald-600 shadow-lg shadow-emerald-500/20 transition-all hover:scale-105 active:scale-95"
          >
            <Check size={16} />Đánh dấu tất cả đã đọc
          </button>
        )}
      </div>

      <div className="space-y-3">
        {items.map((n) => {
          const cfg = LEVEL_CFG[n.level];
          return (
            <div
              key={n.id}
              onClick={() => markRead(n.id)}
              className={`premium-card flex items-start gap-4 cursor-pointer transition-all hover:scale-[1.005] ${!n.is_read ? 'ring-2 ring-emerald-200 dark:ring-emerald-500/20' : 'opacity-70'}`}
            >
              <div className={`w-11 h-11 rounded-2xl ${cfg.bg} flex items-center justify-center shrink-0 mt-0.5`}>
                <cfg.icon size={20} className={cfg.style} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2">
                  <p className={`text-sm text-slate-900 dark:text-white ${!n.is_read ? 'font-black' : 'font-semibold'}`}>
                    {!n.is_read && <span className="inline-block w-2 h-2 bg-emerald-500 rounded-full mr-2 mb-0.5" />}
                    {n.title}
                  </p>
                  <span className="text-xs text-slate-400 shrink-0">{fmtRelative(n.created_at)}</span>
                </div>
                <p className="text-sm text-slate-500 mt-1">{n.message}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
