import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { translations, Lang } from '../constants/languages';

interface LangState {
  lang: Lang;
  setLang: (lang: Lang) => void;
  t: typeof translations.vi;
}

export const useLangStore = create<LangState>()(
  persist(
    (set, get) => ({
      lang: 'vi',
      setLang: (lang) => set({ lang, t: translations[lang] }),
      t: translations.vi,
    }),
    { name: 'lang-storage' }
  )
);
