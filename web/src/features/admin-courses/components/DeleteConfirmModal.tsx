'use client';

import React from 'react';
import { AlertCircle, AlertTriangle, Trash2, X } from 'lucide-react';
import { AdminCourse, getCourseTitle } from '../types';

interface Props {
  isOpen: boolean;
  course: AdminCourse | null;
  reason?: string;
  onReasonChange?: (v: string) => void;
  onClose: () => void;
  onConfirm: () => void;
}

export function DeleteConfirmModal({ isOpen, course, reason = '', onReasonChange, onClose, onConfirm }: Props) {
  const hasEnrolls = course ? course.total_enrolls > 0 : false;

  if (!isOpen || !course) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div className="relative w-full max-w-md bg-white dark:bg-[#12131e] rounded-[28px] shadow-2xl border border-slate-100 dark:border-white/8 p-8">
        <button onClick={onClose}
          className="absolute right-5 top-5 p-2 rounded-2xl hover:bg-slate-100 dark:hover:bg-white/5 text-slate-400 transition-colors">
          <X size={20} />
        </button>

        <div className="flex flex-col items-center text-center mb-6">
          <div className="w-16 h-16 rounded-full bg-red-500/10 flex items-center justify-center mb-4">
            <AlertTriangle size={28} className="text-red-500" />
          </div>
          <h3 className="text-xl font-black text-slate-900 dark:text-white mb-2">
            Xóa khóa học?
          </h3>
          <p className="text-sm text-slate-500 font-semibold">
            Khóa học <span className="font-black text-slate-700 dark:text-white">"{getCourseTitle(course, 'vi')}"</span> sẽ bị xóa vĩnh viễn. Hành động này không thể hoàn tác.
          </p>
        </div>

        {hasEnrolls ? (
          /* Cannot delete */
          <div className="bg-red-50 border-4 border-red-400 rounded-2xl p-6 mb-4">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 bg-red-500 rounded-full flex items-center justify-center flex-shrink-0">
                <AlertCircle size={20} className="text-white" />
              </div>
              <div className="text-left">
                <div className="text-lg font-black text-red-900 mb-2">
                  KHÔNG THỂ XÓA KHÓA HỌC NÀY!
                </div>
                <div className="text-sm text-red-800 space-y-2 font-semibold">
                  <div>Khóa học đã có <span className="text-2xl font-black text-red-900">{course.total_enrolls}</span> học viên đăng ký.</div>
                  <div className="p-3 bg-red-100 border border-red-300 rounded-xl text-sm">
                    Để đảm bảo quyền lợi học viên, bạn cần liên hệ <span className="font-black">Quản trị viên</span> để được hỗ trợ xóa.
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* Can delete with reason */
          <div className="space-y-4 mb-6">
            <div>
              <label className="block text-sm font-bold text-slate-700 dark:text-slate-300 mb-2">
                Lý do xóa <span className="text-red-500">*</span>
              </label>
              <textarea
                value={reason}
                onChange={e => onReasonChange?.(e.target.value)}
                placeholder="Ví dụ: Khóa học không còn phù hợp, cần thay thế bằng khóa học mới..."
                rows={3}
                className="w-full px-4 py-3 border-2 border-slate-200 dark:border-white/8 rounded-2xl text-sm font-semibold outline-none focus:border-red-400 transition-colors resize-none bg-slate-50 dark:bg-white/5"
              />
            </div>
            <div className="bg-red-50 border border-red-200 rounded-2xl p-4 text-sm text-red-800 space-y-1 font-semibold">
              <div className="font-black text-red-900 mb-2">CẢNH BÁO:</div>
              <div>• Khóa học sẽ bị xóa vĩnh viễn</div>
              <div>• Tất cả bài học và tài liệu sẽ bị mất</div>
              <div>• Không thể khôi phục sau khi xóa</div>
            </div>
          </div>
        )}

        <div className="flex items-center gap-3">
          <button onClick={onClose}
            className="flex-1 px-6 py-3 rounded-2xl font-bold text-sm text-slate-600 dark:text-slate-400 bg-slate-100 dark:bg-white/5 hover:bg-slate-200 dark:hover:bg-white/10 transition-all">
            {hasEnrolls ? 'Đóng' : 'Hủy'}
          </button>
          {!hasEnrolls && (
            <button
              onClick={onConfirm}
              disabled={!reason.trim()}
              className="flex-1 flex items-center justify-center gap-2 px-6 py-3 rounded-2xl font-bold text-sm text-white bg-red-500 hover:bg-red-600 shadow-lg shadow-red-500/20 transition-all active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <Trash2 size={16} />
              Xác nhận xóa
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
