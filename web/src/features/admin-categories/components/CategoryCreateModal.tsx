'use client';

import React, { useState } from 'react';
import { Loader2, Sparkles, X } from 'lucide-react';
import { useTranslations } from 'next-intl';
import type { CreateCategoryPayload } from '../types';

interface CategoryCreateModalProps {
  isOpen: boolean;
  isSubmitting: boolean;
  errorCode: string | null;
  onClose: () => void;
  onSubmit: (payload: CreateCategoryPayload) => Promise<void>;
}

const MAX_DESCRIPTION_LENGTH = 5000;

export function CategoryCreateModal({
  isOpen,
  isSubmitting,
  errorCode,
  onClose,
  onSubmit,
}: CategoryCreateModalProps) {
  const t = useTranslations('Admin.categories.create');
  const tErrors = useTranslations('Admin.categories.errors');
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');

  if (!isOpen) return null;

  const trimmedName = name.trim();
  const trimmedDescription = description.trim();
  const canSubmit = trimmedName.length > 0 && !isSubmitting;

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!canSubmit) return;

    await onSubmit({
      name: trimmedName,
      description: trimmedDescription || undefined,
      auto_translate_en: true,
    });
  };

  const handleClose = () => {
    if (isSubmitting) return;
    setName('');
    setDescription('');
    onClose();
  };

  return (
    <div className="fixed inset-0 z-[80] flex items-center justify-center bg-slate-950/55 p-4 backdrop-blur-sm">
      <div className="w-full max-w-xl rounded-[28px] border border-slate-100 bg-white p-6 dark:border-white/10 dark:bg-slate-950">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-emerald-500/15 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
              <Sparkles size={20} strokeWidth={2.5} />
            </div>
            <div>
              <h2 className="text-xl font-black text-slate-900 dark:text-white">{t('title')}</h2>
              <p className="mt-1 text-sm font-semibold text-slate-500">{t('subtitle')}</p>
            </div>
          </div>
          <button
            type="button"
            onClick={handleClose}
            disabled={isSubmitting}
            className="flex h-10 w-10 items-center justify-center rounded-2xl border border-slate-100 text-slate-400 transition-colors hover:border-red-200 hover:text-red-500 disabled:opacity-40 dark:border-white/10"
            aria-label={t('close')}
          >
            <X size={18} strokeWidth={2.5} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="mt-6 space-y-5">
          <div>
            <label htmlFor="category-name" className="text-[10px] font-black uppercase tracking-[2px] text-slate-400">
              {t('nameLabel')}
            </label>
            <input
              id="category-name"
              value={name}
              onChange={(event) => setName(event.target.value)}
              disabled={isSubmitting}
              placeholder={t('namePlaceholder')}
              className="mt-2 w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-bold text-slate-900 outline-none transition-colors placeholder:text-slate-400 focus:border-emerald-400 disabled:opacity-60 dark:border-white/10 dark:bg-white/5 dark:text-white"
              autoFocus
            />
          </div>

          <div>
            <div className="flex items-center justify-between gap-3">
              <label htmlFor="category-description" className="text-[10px] font-black uppercase tracking-[2px] text-slate-400">
                {t('descriptionLabel')}
              </label>
              <span className="text-[10px] font-black text-slate-400">
                {description.length}/{MAX_DESCRIPTION_LENGTH}
              </span>
            </div>
            <textarea
              id="category-description"
              value={description}
              onChange={(event) => setDescription(event.target.value.slice(0, MAX_DESCRIPTION_LENGTH))}
              disabled={isSubmitting}
              placeholder={t('descriptionPlaceholder')}
              rows={5}
              className="mt-2 w-full resize-none rounded-[24px] border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-semibold leading-6 text-slate-900 outline-none transition-colors placeholder:text-slate-400 focus:border-emerald-400 disabled:opacity-60 dark:border-white/10 dark:bg-white/5 dark:text-white"
            />
          </div>

          {errorCode && (
            <div className="rounded-2xl border border-red-500/15 bg-red-500/10 px-4 py-3 text-sm font-bold text-red-600 dark:text-red-400">
              {tErrors(errorCode)}
            </div>
          )}

          <div className="flex flex-col-reverse gap-3 pt-2 sm:flex-row sm:justify-end">
            <button
              type="button"
              onClick={handleClose}
              disabled={isSubmitting}
              className="rounded-full border border-slate-200 px-5 py-3 text-sm font-black text-slate-500 transition-colors hover:border-slate-300 hover:text-slate-700 disabled:opacity-40 dark:border-white/10 dark:text-slate-300 dark:hover:text-white"
            >
              {t('cancel')}
            </button>
            <button
              type="submit"
              disabled={!canSubmit}
              className="inline-flex items-center justify-center gap-2 rounded-full bg-emerald-500 px-6 py-3 text-sm font-black text-white transition-colors hover:bg-emerald-600 active:scale-95 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isSubmitting ? <Loader2 size={16} strokeWidth={2.5} className="animate-spin" /> : <Sparkles size={16} strokeWidth={2.5} />}
              {isSubmitting ? t('submitting') : t('submit')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
