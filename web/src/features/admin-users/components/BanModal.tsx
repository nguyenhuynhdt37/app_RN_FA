'use client';

import React, { useState } from 'react';
import { X, AlertTriangle } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { AdminUser } from '@/types/admin';

interface Props {
  user: AdminUser;
  onClose: () => void;
  onConfirm: (reason: string, until: string | null) => void;
}

export function BanModal({ user, onClose, onConfirm }: Props) {
  const [type, setType] = useState<'permanent' | 'temporary'>('temporary');
  const [reason, setReason] = useState('');
  const [until, setUntil] = useState('');

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-[#12131e] rounded-[28px] shadow-2xl w-full max-w-md p-8 border border-slate-100 dark:border-white/8">
        {/* Header */}
        <div className="flex items-start justify-between mb-6">
          <div>
            <div className="w-12 h-12 rounded-2xl bg-red-50 flex items-center justify-center mb-3">
              <AlertTriangle size={22} className="text-red-500" />
            </div>
            <h3 className="text-xl font-black text-slate-900 dark:text-white">Cấm người dùng</h3>
            <p className="text-sm text-slate-500 mt-1">{user.fullname} · {user.email}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-white/5 transition-colors"
          >
            <X size={18} className="text-slate-400" />
          </button>
        </div>

        <div className="space-y-4">
          {/* Type toggle */}
          <div className="flex gap-2 p-1 bg-slate-100 dark:bg-white/5 rounded-2xl">
            {(['temporary', 'permanent'] as const).map((t) => (
              <button
                key={t}
                onClick={() => setType(t)}
                className={cn(
                  'flex-1 py-2.5 rounded-xl text-sm font-bold transition-all',
                  type === t
                    ? 'bg-white dark:bg-[#1e2030] shadow text-slate-900 dark:text-white'
                    : 'text-slate-500 hover:text-slate-700'
                )}
              >
                {t === 'temporary' ? '⏳ Tạm thời' : '🚫 Vĩnh viễn'}
              </button>
            ))}
          </div>

          {/* Date picker for temporary */}
          {type === 'temporary' && (
            <div>
              <label className="text-xs font-black text-slate-400 uppercase tracking-wider mb-2 block">
                Đến ngày
              </label>
              <input
                type="datetime-local"
                value={until}
                onChange={(e) => setUntil(e.target.value)}
                className="w-full px-4 py-3 rounded-2xl bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/8 text-sm font-semibold text-slate-900 dark:text-white outline-none focus:border-emerald-400 transition-colors"
              />
            </div>
          )}

          {/* Reason */}
          <div>
            <label className="text-xs font-black text-slate-400 uppercase tracking-wider mb-2 block">
              Lý do
            </label>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              rows={3}
              placeholder="Nhập lý do cấm..."
              className="w-full px-4 py-3 rounded-2xl bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/8 text-sm font-semibold text-slate-900 dark:text-white placeholder:text-slate-400 outline-none focus:border-emerald-400 transition-colors resize-none"
            />
          </div>
        </div>

        {/* Footer */}
        <div className="flex gap-3 mt-6">
          <button
            onClick={onClose}
            className="flex-1 py-3 rounded-2xl bg-slate-100 dark:bg-white/5 text-slate-700 dark:text-slate-300 font-bold text-sm hover:bg-slate-200 dark:hover:bg-white/10 transition-colors"
          >
            Hủy
          </button>
          <button
            onClick={() => reason.trim() && onConfirm(reason, type === 'temporary' ? until : null)}
            disabled={!reason.trim()}
            className="flex-1 py-3 rounded-2xl bg-red-500 text-white font-bold text-sm hover:bg-red-600 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Xác nhận cấm
          </button>
        </div>
      </div>
    </div>
  );
}
