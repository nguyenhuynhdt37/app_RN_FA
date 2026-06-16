'use client';

import React from 'react';
import { Key, Shield, Users, Plus } from 'lucide-react';

const ROLES = [
  { id: '1', name: 'Admin', description: 'Toàn quyền quản trị hệ thống', users: 3, color: 'bg-red-500', permissions: ['Quản lý người dùng', 'Quản lý tài chính', 'Cài đặt hệ thống', 'Xem báo cáo'] },
  { id: '2', name: 'Lecturer', description: 'Giảng viên tạo và quản lý khóa học', users: 82, color: 'bg-violet-500', permissions: ['Tạo khóa học', 'Quản lý học viên', 'Xem doanh thu', 'Rút tiền'] },
  { id: '3', name: 'Moderator', description: 'Kiểm duyệt nội dung và bình luận', users: 12, color: 'bg-amber-500', permissions: ['Duyệt khóa học', 'Kiểm duyệt bình luận', 'Báo cáo vi phạm'] },
  { id: '4', name: 'Support', description: 'Hỗ trợ người dùng và xử lý khiếu nại', users: 8, color: 'bg-blue-500', permissions: ['Xem thông tin người dùng', 'Xử lý hoàn tiền', 'Hỗ trợ chat'] },
  { id: '5', name: 'Finance', description: 'Quản lý tài chính và giao dịch', users: 4, color: 'bg-emerald-500', permissions: ['Duyệt rút tiền', 'Quản lý ví', 'Xuất báo cáo tài chính'] },
  { id: '6', name: 'Student', description: 'Học viên học các khóa học', users: 12_740, color: 'bg-slate-400', permissions: ['Mua khóa học', 'Xem nội dung', 'Đánh giá khóa học'] },
];

export function RolesView() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-black text-slate-900 dark:text-white tracking-tight">Quyền hạn</h1>
          <p className="text-slate-500 font-semibold mt-1">{ROLES.length} vai trò trong hệ thống</p>
        </div>
        <button className="flex items-center gap-2 px-5 py-2.5 bg-emerald-500 text-white font-bold text-sm rounded-2xl hover:bg-emerald-600 shadow-lg shadow-emerald-500/20 transition-all hover:scale-105 active:scale-95">
          <Plus size={16} />Thêm vai trò
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
        {ROLES.map((role) => (
          <div key={role.id} className="premium-card group">
            <div className="flex items-start gap-4 mb-5">
              <div className={`w-12 h-12 ${role.color} rounded-2xl flex items-center justify-center shadow-lg shrink-0 group-hover:scale-110 transition-transform`}>
                <Key size={20} className="text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-black text-slate-900 dark:text-white text-lg">{role.name}</h3>
                <p className="text-sm text-slate-500 mt-0.5">{role.description}</p>
              </div>
            </div>
            <div className="flex items-center gap-2 mb-4 pb-4 border-b border-slate-100 dark:border-white/5">
              <Users size={14} className="text-slate-400" />
              <span className="text-sm font-bold text-slate-700 dark:text-slate-300">
                {role.users.toLocaleString('vi-VN')} người dùng
              </span>
            </div>
            <div className="space-y-1.5">
              {role.permissions.map((perm) => (
                <div key={perm} className="flex items-center gap-2 text-xs font-semibold text-slate-600 dark:text-slate-400">
                  <Shield size={11} className="text-emerald-500 shrink-0" />
                  {perm}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
