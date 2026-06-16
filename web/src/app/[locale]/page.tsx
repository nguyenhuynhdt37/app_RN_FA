'use client';

import { useTranslations } from 'next-intl';
import { Link } from '@/i18n/routing';

export default function HomePage() {
  const t = useTranslations('Home');

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-6 bg-white">
      <div className="max-w-xl text-center space-y-6">
        <div className="w-16 h-16 bg-[#00a73d] rounded-2xl mx-auto flex items-center justify-center shadow-lg shadow-[#00a73d]/20">
          <div className="w-8 h-8 border-4 border-white rounded-full border-t-transparent animate-spin-slow" />
        </div>
        
        <h1 className="text-4xl font-black text-[#09090b] tracking-tight">
          {t('title')}
        </h1>
        
        <p className="text-zinc-500 font-medium leading-relaxed">
          {t('subtitle')}
        </p>

        <div className="flex flex-col sm:flex-row gap-3 justify-center pt-4">
          <Link 
            href="/dashboard" 
            className="bg-[#00a73d] text-white px-8 py-3 rounded-xl font-bold hover:opacity-90 transition-all active:scale-95"
          >
            Dashboard
          </Link>
          <Link 
            href="/home" 
            className="bg-zinc-100 text-zinc-900 px-8 py-3 rounded-xl font-bold hover:bg-zinc-200 transition-all active:scale-95"
          >
            {t('getStarted')}
          </Link>
        </div>
      </div>
    </main>
  );
}
