'use client';

import React, { useState, useEffect } from 'react';
import { Download } from 'lucide-react';
import type { AdminUser } from '@/types/admin';
import { UserFilters } from './UserFilters';
import { UsersTable } from './UsersTable';
import { BanModal } from './BanModal';
import { MOCK_USERS, PAGE_SIZE } from '../types';

export function UsersView() {
  const [searchInput, setSearchInput] = useState('');
  const [search, setSearch] = useState('');
  const [filterVerified, setFilterVerified] = useState<boolean | null>(null);
  const [filterBanned, setFilterBanned] = useState<boolean | null>(null);
  const [page, setPage] = useState(1);
  const [banTarget, setBanTarget] = useState<AdminUser | null>(null);

  // Debounce search
  useEffect(() => {
    const t = setTimeout(() => { setSearch(searchInput); setPage(1); }, 450);
    return () => clearTimeout(t);
  }, [searchInput]);

  const filtered = MOCK_USERS.filter((u) => {
    if (search && !u.fullname.toLowerCase().includes(search.toLowerCase()) && !u.email.toLowerCase().includes(search.toLowerCase())) return false;
    if (filterVerified !== null && u.is_verified_email !== filterVerified) return false;
    if (filterBanned !== null && u.is_banned !== filterBanned) return false;
    return true;
  });

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const pageData = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  const hasFilters = !!search || filterVerified !== null || filterBanned !== null;

  const clearFilters = () => {
    setSearchInput(''); setSearch('');
    setFilterVerified(null); setFilterBanned(null);
    setPage(1);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-black text-slate-900 dark:text-white tracking-tight">Người dùng</h1>
          <p className="text-slate-500 font-semibold mt-1">
            {filtered.length.toLocaleString('vi-VN')} người dùng
          </p>
        </div>
        <button className="flex items-center gap-2 px-5 py-2.5 bg-emerald-500 text-white font-bold text-sm rounded-2xl hover:bg-emerald-600 shadow-lg shadow-emerald-500/20 transition-all hover:scale-105 active:scale-95">
          <Download size={16} />Xuất Excel
        </button>
      </div>

      {/* Filters */}
      <UserFilters
        searchInput={searchInput}
        onSearchChange={setSearchInput}
        filterVerified={filterVerified}
        onFilterVerifiedChange={setFilterVerified}
        filterBanned={filterBanned}
        onFilterBannedChange={setFilterBanned}
        onClear={clearFilters}
        hasFilters={hasFilters}
      />

      {/* Table */}
      <UsersTable
        data={pageData}
        page={page}
        totalPages={totalPages}
        onPageChange={setPage}
        onBan={setBanTarget}
        totalFiltered={filtered.length}
      />

      {/* Ban modal */}
      {banTarget && (
        <BanModal
          user={banTarget}
          onClose={() => setBanTarget(null)}
          onConfirm={(reason, until) => {
            console.log('Ban user:', banTarget.id, { reason, until });
            setBanTarget(null);
          }}
        />
      )}
    </div>
  );
}
