import React from 'react';
import { Ban, Clock, CheckCircle } from 'lucide-react';
import type { AdminUser } from '@/types/admin';

interface Props {
  user: AdminUser;
}

export function StatusBadge({ user }: Props) {
  if (user.is_banned) {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-black bg-red-50 text-red-600">
        <Ban size={10} />Bị cấm
      </span>
    );
  }
  if (!user.is_verified_email) {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-black bg-amber-50 text-amber-600">
        <Clock size={10} />Chưa xác thực
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-black bg-emerald-50 text-emerald-600">
      <CheckCircle size={10} />Hoạt động
    </span>
  );
}
