'use client';

import React, { useState } from 'react';
import { AlertTriangle, Loader2, Trash2, X } from 'lucide-react';
import { useTranslations } from 'next-intl';

interface CategoryDeleteModalProps {
  isOpen: boolean;
  categoryName: string;
  isSubmitting: boolean;
  errorCode: string | null;
  onClose: () => void;
  onConfirm: () => Promise<void>;
}

export function CategoryDeleteModal({
  isOpen,
  categoryName,
  isSubmitting,
  errorCode,
  onClose,
  onConfirm,
}: CategoryDeleteModalProps) {
  const t = useTranslations('Admin.categories.delete');
  const tErrors = useTranslations('Admin.categories.errors');
  const [isConfirming, setIsConfirming] = useState(false);

  if (!isOpen) return null;

  const handleClose = () => {
    if (isSubmitting) return;
    setIsConfirming(false);
    onClose();
  };

  const handleConfirm = async () => {
    if (!isConfirming) {
      setIsConfirming(true);
      return;
    }
    await onConfirm();
  };

  return (
    <div className="fixed inset-0 z-[80] flex items-center justify-center bg-slate-950/55 p-4 backdrop-blur-sm">
      <div className="w-full max-w-md rounded-[28px] border border-slate-100 bg-white p-6 dark:border-white/10 dark:bg-slate-950">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-red-500/15 bg-red-500/10 text-red-500">
              <AlertTriangle size={20} strokeWidth={2.5} />
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

        <div className="mt-6">
          <div className="rounded-[24px] border border-slate-100 bg-slate-50 p-4 dark:border-white/5 dark:bg-white/5">
            <p className="text-sm font-bold text-slate-900 dark:text-white">
              {t('categoryLabel')}
            </p>
            <p className="mt-1 text-base font-black text-red-500">{categoryName}</p>
          </div>

          <p className="mt-4 text-sm font-semibold leading-6 text-slate-500">
            {t('warning')}
          </p>

          {errorCode && (
            <div className="mt-4 rounded-2xl border border-red-500/15 bg-red-500/10 px-4 py-3 text-sm font-bold text-red-600 dark:text-red-400">
              {tErrors(errorCode)}
            </div>
          )}

          <div className="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
            <button
              type="button"
              onClick={handleClose}
              disabled={isSubmitting}
              className="rounded-full border border-slate-200 px-5 py-3 text-sm font-black text-slate-500 transition-colors hover:border-slate-300 hover:text-slate-700 disabled:opacity-40 dark:border-white/10 dark:text-slate-300 dark:hover:text-white"
            >
              {t('cancel')}
            </button>
            <button
              type="button"
              onClick={handleConfirm}
              disabled={isSubmitting}
              className="inline-flex items-center justify-center gap-2 rounded-full bg-red-500 px-6 py-3 text-sm font-black text-white transition-colors hover:bg-red-600 active:scale-95 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isSubmitting ? (
                <Loader2 size={16} strokeWidth={2.5} className="animate-spin" />
              ) : isConfirming ? (
                <Trash2 size={16} strokeWidth={2.5} />
              ) : (
                <AlertTriangle size={16} strokeWidth={2.5} />
              )}
              {isSubmitting ? t('deleting') : isConfirming ? t('confirm') : t('proceed')}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
