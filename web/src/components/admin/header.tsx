'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Search, Bell, Settings, LogOut, User, ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAuthStore } from '@/store/auth-store';
import { useRouter } from 'next/navigation';
import { usePathname } from '@/i18n/routing';
import { logoutAction } from '@/features/auth/actions/auth-actions';

interface HeaderProps {
  isCollapsed: boolean;
}

const PAGE_TITLES: Record<string, string> = {
  '/dashboard': 'Tổng quan',
  '/dashboard/users': 'Người dùng',
  '/dashboard/lecturers': 'Giảng viên',
  '/dashboard/courses': 'Khóa học',
  '/categories': 'Danh mục',
  '/dashboard/categories': 'Danh mục',
  '/dashboard/topics': 'Chủ đề',
  '/dashboard/roles': 'Quyền hạn',
  '/dashboard/wallets': 'Quản lý Ví',
  '/dashboard/transactions': 'Giao dịch',
  '/dashboard/discounts': 'Mã giảm giá',
  '/dashboard/refunds': 'Hoàn tiền',
  '/dashboard/withdraws': 'Rút tiền',
  '/dashboard/notifications': 'Thông báo',
  '/dashboard/settings': 'Cài đặt',
};

export default function Header({ isCollapsed }: HeaderProps) {
  const pathname = usePathname();
  const router = useRouter();
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const pageTitle = PAGE_TITLES[pathname] ?? 'Admin';

  // Close dropdown on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const handleLogout = async () => {
    await logoutAction();
    logout();
    router.push('/login');
    router.refresh();
  };

  const initials = user?.fullName
    ? user.fullName.split(' ').map((n) => n[0]).slice(0, 2).join('').toUpperCase()
    : 'A';

  return (
    <header
      className={cn(
        'fixed top-0 right-0 h-24 bg-white/80 dark:bg-[#0b0c14]/80 backdrop-blur-xl z-40',
        'transition-all duration-500 ease-[cubic-bezier(0.23,1,0.32,1)]',
        'flex items-center justify-between px-8 border-b border-slate-100 dark:border-white/5',
        'hidden lg:flex', // desktop only — mobile has no persistent header
        isCollapsed ? 'left-[72px]' : 'left-72'
      )}
    >
      {/* Left: Page Title */}
      <div>
        <h2 className="text-xl font-black text-slate-900 dark:text-white tracking-tight">
          {pageTitle}
        </h2>
        <p className="text-xs font-semibold text-slate-400 mt-0.5">
          {new Date().toLocaleDateString('vi-VN', { weekday: 'long', day: '2-digit', month: 'long', year: 'numeric' })}
        </p>
      </div>

      {/* Center: Search */}
      <div className="flex-1 max-w-md mx-10">
        <div className="relative group">
          <Search
            size={16}
            className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-emerald-500 transition-colors"
          />
          <input
            type="text"
            placeholder="Tìm kiếm người dùng, khóa học..."
            className={cn(
              'w-full bg-slate-100/80 dark:bg-white/5 rounded-2xl py-3 pl-11 pr-5',
              'text-sm font-medium text-slate-700 dark:text-slate-300 placeholder:text-slate-400',
              'outline-none border border-transparent',
              'focus:border-emerald-500/30 focus:bg-white dark:focus:bg-white/10 focus:ring-2 focus:ring-emerald-500/10',
              'transition-all duration-200'
            )}
          />
        </div>
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-3">
        {/* Notification bell */}
        <button className="relative p-3 text-slate-500 hover:text-emerald-500 hover:bg-emerald-50 dark:hover:bg-emerald-500/10 rounded-xl transition-all">
          <Bell size={18} />
          <span className="absolute top-2.5 right-2.5 w-2 h-2 bg-emerald-500 rounded-full ring-2 ring-white dark:ring-[#0b0c14]" />
        </button>

        <div className="w-px h-8 bg-slate-200 dark:bg-white/10" />

        {/* User Dropdown */}
        <div className="relative" ref={dropdownRef}>
          <button
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            className="flex items-center gap-3 pl-1 pr-3 py-1 rounded-2xl hover:bg-slate-100 dark:hover:bg-white/5 transition-all group"
          >
            {user?.avatarUrl ? (
              <img
                src={user.avatarUrl}
                alt={user.fullName}
                className="w-10 h-10 rounded-xl object-cover border-2 border-white shadow-md"
              />
            ) : (
              <div className="w-10 h-10 rounded-xl bg-emerald-500 flex items-center justify-center shadow-md">
                <span className="text-white font-black text-sm">{initials}</span>
              </div>
            )}
            <div className="text-left hidden md:block">
              <p className="text-sm font-black text-slate-900 dark:text-white leading-none">
                {user?.fullName ?? 'Admin'}
              </p>
              <p className="text-[10px] font-bold text-emerald-500 uppercase tracking-wider mt-1">
                {user?.role ?? 'admin'}
              </p>
            </div>
            <ChevronDown
              size={14}
              className={cn(
                'text-slate-400 transition-transform duration-200',
                isDropdownOpen && 'rotate-180'
              )}
            />
          </button>

          {/* Dropdown */}
          {isDropdownOpen && (
            <div className={cn(
              'absolute right-0 top-full mt-2 w-64',
              'bg-white dark:bg-[#12131e] rounded-2xl shadow-2xl shadow-black/10 dark:shadow-black/40',
              'border border-slate-100 dark:border-white/8',
              'py-2 z-50 animate-in fade-in slide-in-from-top-2 duration-150'
            )}>
              {/* User info */}
              <div className="px-5 py-4 border-b border-slate-100 dark:border-white/5">
                <div className="flex items-center gap-3">
                  {user?.avatarUrl ? (
                    <img src={user.avatarUrl} alt="" className="w-12 h-12 rounded-xl object-cover" />
                  ) : (
                    <div className="w-12 h-12 rounded-xl bg-emerald-500 flex items-center justify-center">
                      <span className="text-white font-black">{initials}</span>
                    </div>
                  )}
                  <div className="flex-1 min-w-0">
                    <p className="font-bold text-slate-900 dark:text-white truncate">
                      {user?.fullName ?? 'Admin'}
                    </p>
                    <p className="text-xs text-slate-500 truncate">{user?.email}</p>
                  </div>
                </div>
              </div>

              {/* Menu items */}
              <div className="py-1">
                {[
                  { icon: User, label: 'Hồ sơ', action: () => router.push('/dashboard/settings') },
                  { icon: Settings, label: 'Cài đặt', action: () => router.push('/dashboard/settings') },
                ].map((item) => (
                  <button
                    key={item.label}
                    onClick={() => { item.action(); setIsDropdownOpen(false); }}
                    className="w-full flex items-center gap-3 px-5 py-3 text-sm font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-white/5 hover:text-emerald-600 transition-colors"
                  >
                    <item.icon size={16} className="text-slate-400" />
                    {item.label}
                  </button>
                ))}
              </div>

              <div className="border-t border-slate-100 dark:border-white/5 py-1">
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-3 px-5 py-3 text-sm font-semibold text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors"
                >
                  <LogOut size={16} />
                  Đăng xuất
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
