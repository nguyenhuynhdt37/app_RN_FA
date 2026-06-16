'use client';

import React, { useState } from 'react';
import { Link, usePathname } from '@/i18n/routing';
import {
  LayoutGrid,
  Users,
  GraduationCap,
  Folder,
  Tag,
  Wallet,
  CreditCard,
  TicketPercent,
  RefreshCw,
  ArrowUpRight,
  Bell,
  Settings,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Shield,
  BookOpen,
  Menu,
  X,
  Key,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAuthStore } from '@/store/auth-store';

interface SidebarProps {
  isCollapsed: boolean;
  onToggle: () => void;
}

const MENU_GROUPS = [
  {
    label: 'Tổng quan',
    items: [
      { icon: LayoutGrid, label: 'Dashboard', href: '/dashboard' },
    ],
  },
  {
    label: 'Nội dung',
    items: [
      { icon: Folder, label: 'Danh mục', href: '/categories' },
      { icon: BookOpen, label: 'Khóa học', href: '/courses' },
      { icon: Tag, label: 'Chủ đề', href: '/topics' },
    ],
  },
  {
    label: 'Thành viên',
    items: [
      { icon: Users, label: 'Người dùng', href: '/users' },
      { icon: GraduationCap, label: 'Giảng viên', href: '/lecturers' },
      { icon: Key, label: 'Quyền hạn', href: '/roles' },
    ],
  },
  {
    label: 'Tài chính',
    items: [
      { icon: Wallet, label: 'Ví', href: '/wallets' },
      { icon: CreditCard, label: 'Giao dịch', href: '/transactions' },
      { icon: TicketPercent, label: 'Giảm giá', href: '/discounts' },
      { icon: RefreshCw, label: 'Hoàn tiền', href: '/refunds' },
      { icon: ArrowUpRight, label: 'Rút tiền', href: '/withdraws' },
    ],
  },
  {
    label: 'Hệ thống',
    items: [
      { icon: Bell, label: 'Thông báo', href: '/notifications' },
      { icon: Settings, label: 'Cài đặt', href: '/settings' },
    ],
  },
];

export default function Sidebar({ isCollapsed, onToggle }: SidebarProps) {
  const pathname = usePathname();
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const logout = useAuthStore((s) => s.logout);

  const isActive = (href: string) => {
    if (href === '/dashboard') return pathname === '/dashboard';
    return pathname.startsWith(href);
  };

  const NavContent = () => (
    <>
      {/* Brand */}
      <div className="h-24 flex items-center px-6 shrink-0 border-b border-white/5">
        <div className="w-10 h-10 bg-emerald-500 rounded-xl flex items-center justify-center shadow-lg shadow-emerald-500/30 shrink-0">
          <Shield size={20} className="text-white" />
        </div>
        {!isCollapsed && (
          <div className="ml-3 overflow-hidden">
            <h1 className="font-black text-xl tracking-tighter text-white leading-none">
              NeuralEarn
            </h1>
            <p className="text-[10px] font-bold text-emerald-500 uppercase tracking-widest mt-1">
              Admin Portal
            </p>
          </div>
        )}
      </div>

      {/* Navigation */}
      <div className="flex-1 px-3 py-4 space-y-6 overflow-y-auto overflow-x-hidden no-scrollbar">
        {MENU_GROUPS.map((group, gIdx) => (
          <div key={gIdx} className="space-y-1">
            {!isCollapsed && (
              <p className="px-3 text-[9px] font-black text-slate-600 uppercase tracking-[2.5px] mb-3">
                {group.label}
              </p>
            )}
            {group.items.map((item) => {
              const active = isActive(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href as any}
                  onClick={() => setIsMobileOpen(false)}
                  className={cn(
                    'flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group relative',
                    active
                      ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/20'
                      : 'text-slate-500 hover:text-white hover:bg-white/5'
                  )}
                  title={isCollapsed ? item.label : undefined}
                >
                  <item.icon
                    size={18}
                    className={cn(
                      'shrink-0 transition-colors',
                      active ? 'text-white' : 'text-slate-500 group-hover:text-slate-300'
                    )}
                  />
                  {!isCollapsed && (
                    <span className="font-semibold text-sm truncate">{item.label}</span>
                  )}
                  {active && !isCollapsed && (
                    <div className="absolute right-3 w-1.5 h-1.5 bg-white rounded-full" />
                  )}
                </Link>
              );
            })}
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-white/5 space-y-1">
        <button
          onClick={logout}
          className="w-full flex items-center gap-3 px-3 py-2.5 text-slate-500 font-semibold text-sm hover:text-red-400 transition-all rounded-xl hover:bg-red-500/10 group"
          title={isCollapsed ? 'Đăng xuất' : undefined}
        >
          <LogOut size={18} className="shrink-0" />
          {!isCollapsed && <span>Đăng xuất</span>}
        </button>

        <button
          onClick={onToggle}
          className="w-full flex items-center gap-3 px-3 py-2.5 text-slate-600 font-semibold text-sm hover:text-white transition-all rounded-xl hover:bg-white/5"
          title={isCollapsed ? 'Mở rộng' : 'Thu gọn'}
        >
          {isCollapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
          {!isCollapsed && <span>Thu gọn</span>}
        </button>
      </div>
    </>
  );

  return (
    <>
      {/* Mobile toggle button */}
      <button
        onClick={() => setIsMobileOpen(!isMobileOpen)}
        className="lg:hidden fixed top-5 left-4 z-50 p-2 rounded-xl bg-[#0b0c14] border border-white/10 text-white shadow-lg"
      >
        {isMobileOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      {/* Mobile overlay */}
      {isMobileOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black/60 z-40 backdrop-blur-sm"
          onClick={() => setIsMobileOpen(false)}
        />
      )}

      {/* Desktop Sidebar */}
      <aside
        className={cn(
          'fixed left-0 top-0 h-screen bg-[#0b0c14] z-50 transition-all duration-500 ease-[cubic-bezier(0.23,1,0.32,1)] flex flex-col border-r border-white/5',
          // Desktop
          'hidden lg:flex',
          isCollapsed ? 'w-[72px]' : 'w-72'
        )}
      >
        <NavContent />
      </aside>

      {/* Mobile Sidebar (slide-in drawer) */}
      <aside
        className={cn(
          'fixed left-0 top-0 h-screen w-72 bg-[#0b0c14] z-50 flex flex-col border-r border-white/5 transition-transform duration-300 lg:hidden',
          isMobileOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <NavContent />
      </aside>
    </>
  );
}
