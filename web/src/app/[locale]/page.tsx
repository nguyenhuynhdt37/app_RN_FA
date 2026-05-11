import { useTranslations } from 'next-intl';

export default function Home() {
  const t = useTranslations('Home');

  return (
    <main className="min-h-screen flex flex-col items-center justify-center relative overflow-hidden bg-[#09090b]">
      {/* Background Glow */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-brand-primary/10 blur-[120px]" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-brand-primary/10 blur-[120px]" />

      <div className="z-10 text-center space-y-8 max-w-2xl px-4">
        <div className="inline-block px-4 py-1.5 rounded-full glass border border-white/10 text-brand-secondary text-sm font-medium tracking-wider uppercase mb-4 animate-in fade-in slide-in-from-bottom-4 duration-1000">
          {t('badge')}
        </div>
        
        <h1 className="text-5xl md:text-7xl font-black tracking-tighter text-white drop-shadow-2xl">
          {t.rich('title', {
            accent: (chunks) => <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-primary via-brand-secondary to-brand-accent">{chunks}</span>
          })}
        </h1>
        
        <p className="text-lg text-zinc-400 font-medium leading-relaxed">
          {t('description')}
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
          <button className="px-8 py-4 rounded-2xl bg-white text-black font-bold hover:scale-105 transition-transform duration-300">
            {t('getStarted')}
          </button>
          <button className="px-8 py-4 rounded-2xl glass text-white font-bold border border-white/10 hover:bg-white/5 transition-all duration-300">
            {t('viewDocs')}
          </button>
        </div>
      </div>

      {/* Preview Card */}
      <div className="mt-20 w-full max-w-5xl px-4 animate-in fade-in zoom-in duration-1000 delay-500">
        <div className="glass-card aspect-video w-full flex items-center justify-center text-zinc-500 border border-white/5">
          <p className="font-mono text-sm uppercase tracking-widest">{t('preview')}</p>
        </div>
      </div>
    </main>
  );
}
