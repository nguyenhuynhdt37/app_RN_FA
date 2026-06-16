import React from 'react';
import { Search, XCircle } from 'lucide-react';

interface Props {
  searchInput: string;
  onSearchChange: (v: string) => void;
  filterVerified: boolean | null;
  onFilterVerifiedChange: (v: boolean | null) => void;
  filterBanned: boolean | null;
  onFilterBannedChange: (v: boolean | null) => void;
  onClear: () => void;
  hasFilters: boolean;
}

export function UserFilters({
  searchInput, onSearchChange,
  filterVerified, onFilterVerifiedChange,
  filterBanned, onFilterBannedChange,
  onClear, hasFilters,
}: Props) {
  const inputClass = 'px-4 py-3 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/8 rounded-2xl text-sm font-semibold text-slate-700 dark:text-slate-300 outline-none focus:border-emerald-400 transition-colors';

  return (
    <div className="premium-card">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Search */}
        <div className="relative group">
          <Search
            size={16}
            className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-emerald-500 transition-colors"
          />
          <input
            type="text"
            value={searchInput}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Tìm theo tên hoặc email..."
            className={`w-full pl-10 pr-4 ${inputClass}`}
          />
        </div>

        {/* Email verification filter */}
        <select
          value={filterVerified === null ? '' : String(filterVerified)}
          onChange={(e) =>
            onFilterVerifiedChange(e.target.value === '' ? null : e.target.value === 'true')
          }
          className={inputClass}
        >
          <option value="">Xác thực email</option>
          <option value="true">Đã xác thực</option>
          <option value="false">Chưa xác thực</option>
        </select>

        {/* Banned filter */}
        <select
          value={filterBanned === null ? '' : String(filterBanned)}
          onChange={(e) =>
            onFilterBannedChange(e.target.value === '' ? null : e.target.value === 'true')
          }
          className={inputClass}
        >
          <option value="">Trạng thái</option>
          <option value="false">Bình thường</option>
          <option value="true">Bị cấm</option>
        </select>

        {/* Clear */}
        <button
          onClick={onClear}
          disabled={!hasFilters}
          className="flex items-center justify-center gap-2 px-4 py-3 rounded-2xl border border-slate-200 dark:border-white/8 text-sm font-bold text-slate-500 hover:text-slate-800 hover:bg-slate-50 dark:hover:bg-white/5 transition-all disabled:opacity-40"
        >
          <XCircle size={16} />
          Xóa bộ lọc
        </button>
      </div>
    </div>
  );
}
