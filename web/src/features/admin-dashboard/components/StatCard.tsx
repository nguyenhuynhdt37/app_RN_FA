import React from 'react';

interface StatCardProps {
  label: string;
  value: string;
  icon: React.ElementType;
  iconBg: string;
  badge?: { text: string; urgent?: boolean };
  loading?: boolean;
}

export function StatCard({ label, value, icon: Icon, iconBg, badge, loading }: StatCardProps) {
  return (
    <div className="premium-card group flex flex-col gap-4">
      <div className="flex items-start justify-between">
        <div className={`w-12 h-12 rounded-2xl ${iconBg} flex items-center justify-center transition-transform group-hover:scale-110`}>
          <Icon size={22} className="text-white" />
        </div>
        {badge && (
          <span className={`text-[10px] font-black px-2.5 py-1 rounded-full uppercase tracking-wider ${badge.urgent ? 'bg-red-50 text-red-600' : 'bg-amber-50 text-amber-600'}`}>
            {badge.text}
          </span>
        )}
      </div>
      {loading ? (
        <div className="h-8 w-28 bg-slate-100 dark:bg-white/10 rounded-xl animate-pulse" />
      ) : (
        <div>
          <p className="text-[10px] font-black text-slate-400 uppercase tracking-[2px] mb-1.5">{label}</p>
          <p className="text-2xl font-black text-slate-900 dark:text-white tracking-tight">{value}</p>
        </div>
      )}
    </div>
  );
}
