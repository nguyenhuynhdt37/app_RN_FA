import React from 'react';
import { Eye, GraduationCap, Ban, UserCheck, Trash2, Search, ChevronLeft, ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { AdminUser } from '@/types/admin';
import { StatusBadge } from './StatusBadge';
import { fmtDate, fmtRelative, PAGE_SIZE } from '../types';

interface Props {
  data: AdminUser[];
  page: number;
  totalPages: number;
  onPageChange: (p: number) => void;
  onBan: (user: AdminUser) => void;
  totalFiltered: number;
}

const COLS = ['#', 'Người dùng', 'Vai trò', 'Khóa học', 'Trạng thái', 'Lần cuối đăng nhập', 'Thao tác'];

export function UsersTable({ data, page, totalPages, onPageChange, onBan, totalFiltered }: Props) {
  return (
    <div className="premium-card p-0 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-100 dark:border-white/5">
              {COLS.map((col) => (
                <th key={col} className="px-6 py-4 text-left text-[10px] font-black text-slate-400 uppercase tracking-[2px]">
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50 dark:divide-white/3">
            {data.length === 0 ? (
              <tr>
                <td colSpan={COLS.length} className="px-6 py-16 text-center">
                  <div className="w-16 h-16 rounded-3xl bg-slate-100 dark:bg-white/5 flex items-center justify-center mx-auto mb-4">
                    <Search size={24} className="text-slate-400" />
                  </div>
                  <p className="font-bold text-slate-500">Không tìm thấy người dùng</p>
                </td>
              </tr>
            ) : (
              data.map((user, idx) => (
                <tr
                  key={user.id}
                  className="hover:bg-slate-50/50 dark:hover:bg-white/2 transition-colors group"
                >
                  <td className="px-6 py-4 text-sm font-bold text-slate-400">
                    {(page - 1) * PAGE_SIZE + idx + 1}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-blue-400 to-indigo-500 flex items-center justify-center text-white font-black text-sm shrink-0">
                        {user.fullname.charAt(0)}
                      </div>
                      <div>
                        <p className="font-bold text-sm text-slate-900 dark:text-white">{user.fullname}</p>
                        <p className="text-xs text-slate-400">{user.email}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-wrap gap-1">
                      {user.roles.map((r) => (
                        <span key={r} className="px-2.5 py-1 rounded-full text-[10px] font-black bg-blue-50 dark:bg-blue-500/10 text-blue-700 dark:text-blue-400 uppercase tracking-wider">
                          {r}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-center">
                    <span className="px-3 py-1 rounded-full bg-slate-100 dark:bg-white/5 text-slate-700 dark:text-slate-300 text-xs font-black">
                      {user.total_courses}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <StatusBadge user={user} />
                  </td>
                  <td className="px-6 py-4">
                    <p className="text-sm font-semibold text-slate-700 dark:text-slate-300">{fmtRelative(user.last_login_at)}</p>
                    <p className="text-xs text-slate-400">{fmtDate(user.last_login_at)}</p>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button title="Xem" className="p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-white/5 text-slate-400 hover:text-emerald-600 transition-colors">
                        <Eye size={15} />
                      </button>
                      {!user.roles.includes('lecturer') && (
                        <button title="Cấp giảng viên" className="p-2 rounded-xl hover:bg-amber-50 dark:hover:bg-amber-500/10 text-slate-400 hover:text-amber-600 transition-colors">
                          <GraduationCap size={15} />
                        </button>
                      )}
                      <button
                        title={user.is_banned ? 'Bỏ cấm' : 'Cấm'}
                        onClick={() => !user.is_banned && onBan(user)}
                        className={cn(
                          'p-2 rounded-xl transition-colors',
                          user.is_banned
                            ? 'hover:bg-emerald-50 dark:hover:bg-emerald-500/10 text-red-400 hover:text-emerald-600'
                            : 'hover:bg-red-50 dark:hover:bg-red-500/10 text-slate-400 hover:text-red-600'
                        )}
                      >
                        {user.is_banned ? <UserCheck size={15} /> : <Ban size={15} />}
                      </button>
                      {!user.is_verified_email && (
                        <button title="Xóa" className="p-2 rounded-xl hover:bg-red-50 dark:hover:bg-red-500/10 text-slate-400 hover:text-red-600 transition-colors">
                          <Trash2 size={15} />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="px-6 py-5 border-t border-slate-100 dark:border-white/5 flex items-center justify-between">
        <p className="text-sm font-semibold text-slate-500">
          {totalFiltered} kết quả · Trang {page}/{totalPages}
        </p>
        <div className="flex items-center gap-2">
          <button
            onClick={() => onPageChange(Math.max(1, page - 1))}
            disabled={page === 1}
            className="p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-white/5 text-slate-500 disabled:opacity-30 transition-all"
          >
            <ChevronLeft size={18} />
          </button>
          {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
            const pg = page <= 3 ? i + 1 : page - 2 + i;
            if (pg > totalPages) return null;
            return (
              <button
                key={pg}
                onClick={() => onPageChange(pg)}
                className={cn(
                  'w-9 h-9 rounded-xl text-sm font-bold transition-all',
                  pg === page
                    ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/20'
                    : 'hover:bg-slate-100 dark:hover:bg-white/5 text-slate-500'
                )}
              >
                {pg}
              </button>
            );
          })}
          <button
            onClick={() => onPageChange(Math.min(totalPages, page + 1))}
            disabled={page === totalPages}
            className="p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-white/5 text-slate-500 disabled:opacity-30 transition-all"
          >
            <ChevronRight size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}
