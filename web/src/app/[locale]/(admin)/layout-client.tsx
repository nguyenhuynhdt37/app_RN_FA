'use client';

import React, { useState } from 'react';
import Sidebar from '@/components/admin/sidebar';
import Header from '@/components/admin/header';
import { cn } from '@/lib/utils';

export function AdminLayoutClient({ children }: { children: React.ReactNode }) {
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <div className="min-h-screen bg-[#f8fafc] dark:bg-[#020617]">
      <Sidebar 
        isCollapsed={isCollapsed} 
        onToggle={() => setIsCollapsed(!isCollapsed)} 
      />
      
      <Header isCollapsed={isCollapsed} />

      <main 
        className={cn(
          "pt-24 transition-all duration-500 ease-[cubic-bezier(0.23,1,0.32,1)] min-h-screen",
          isCollapsed ? "ml-20" : "ml-72"
        )}
      >
        <div className="p-10 max-w-[1600px] mx-auto">
          {children}
        </div>
      </main>
    </div>
  );
}
