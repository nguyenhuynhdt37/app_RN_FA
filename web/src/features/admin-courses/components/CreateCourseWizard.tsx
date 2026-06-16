'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useRouter } from '@/i18n/routing';
import {
  ChevronLeft, ChevronRight, Save, Loader2, X, Plus,
} from 'lucide-react';
import { useCreateCourse } from '../hooks/use-create-course';
import { StepBasicInfo } from './wizard-steps/StepBasicInfo';
import { StepDetailedContent } from './wizard-steps/StepDetailedContent';
import { StepSettings } from './wizard-steps/StepSettings';
import { StepReview } from './wizard-steps/StepReview';

const STEPS = [
  { id: 0, title: 'Thông tin cơ bản' },
  { id: 1, title: 'Mô tả chi tiết' },
  { id: 2, title: 'Mục tiêu & Đối tượng' },
  { id: 3, title: 'Giá & Xuất bản' },
];

export function CreateCourseWizard() {
  const router = useRouter();
  const ctx = useCreateCourse();
  const { step, goNext, goBack, submit, isLoading } = ctx;

  const progress = ((step + 1) / STEPS.length) * 100;

  return (
    <div className="fixed inset-0 z-[100] bg-slate-50 dark:bg-[#07080f] overflow-y-auto no-scrollbar">
      <div className="max-w-4xl mx-auto px-4 py-12">
        {/* Header */}
        <div className="mb-10 flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <button
              onClick={() => router.back()}
              className="flex items-center gap-2 text-slate-500 hover:text-slate-900 dark:hover:text-white mb-4 transition-colors font-bold text-sm uppercase tracking-widest group"
            >
              <ChevronLeft size={18} className="group-hover:-translate-x-1 transition-transform" />
              Quay lại danh sách
            </button>
            <h1 className="text-4xl font-black text-slate-900 dark:text-white tracking-tight">
              Tạo khóa học mới
            </h1>
            <p className="text-slate-500 font-semibold mt-2">
              Thiết kế khoá học chất lượng cao từng bước một cách dễ dàng
            </p>
          </div>
          
          <div className="flex items-center gap-2 px-4 py-2 bg-emerald-500/10 rounded-full border border-emerald-500/20">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-[10px] font-black uppercase tracking-widest text-emerald-600 dark:text-emerald-400">
              AI-Powered Workflow
            </span>
          </div>
        </div>

        {/* Progress Bar - Studynest Style */}
        <div className="bg-white dark:bg-white/5 rounded-[32px] p-8 border border-slate-200 dark:border-white/10 mb-8">
          <div className="flex items-center justify-between text-[11px] font-black uppercase tracking-widest text-slate-400 dark:text-slate-500 mb-4">
            <span>Bước {step + 1} / {STEPS.length}</span>
            <span className="text-emerald-500">{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-slate-100 dark:bg-white/5 h-3 rounded-full overflow-hidden">
            <motion.div 
              className="h-full bg-gradient-to-r from-emerald-500 to-teal-600"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ type: 'spring', damping: 20, stiffness: 100 }}
            />
          </div>
          <div className="hidden md:flex items-center justify-between mt-6 text-[10px] font-black uppercase tracking-widest text-slate-400">
            {STEPS.map((s, i) => (
              <span key={i} className={i <= step ? 'text-emerald-600 dark:text-emerald-400 font-black' : 'font-semibold'}>
                {s.title}
              </span>
            ))}
          </div>
        </div>

        {/* Wizard Card */}
        <div className="bg-white dark:bg-white/5 rounded-[40px] border border-slate-200 dark:border-white/10 p-10 min-h-[500px] flex flex-col shadow-xl shadow-slate-200/20 dark:shadow-none">
          <div className="flex-1">
            <AnimatePresence mode="wait">
              <motion.div
                key={step}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ type: 'spring', damping: 25, stiffness: 200 }}
              >
                {step === 0 && <StepBasicInfo ctx={ctx} />}
                {step === 1 && <StepDetailedContent ctx={ctx} />}
                {step === 2 && <StepSettings ctx={ctx} />}
                {step === 3 && <StepReview ctx={ctx} />}
              </motion.div>
            </AnimatePresence>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-between mt-12 pt-8 border-t border-slate-100 dark:border-white/5">
            <button
              onClick={goBack}
              disabled={step === 0}
              className="px-8 py-4 rounded-full text-sm font-black uppercase tracking-widest text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors disabled:opacity-0"
            >
              Quay lại
            </button>

            <button
              onClick={step === STEPS.length - 1 ? submit : goNext}
              disabled={isLoading}
              className="px-10 py-4 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white rounded-full text-sm font-black uppercase tracking-widest transition-all active:scale-95 disabled:opacity-50 flex items-center gap-3 shadow-lg shadow-emerald-500/20"
            >
              {isLoading ? (
                <Loader2 size={18} className="animate-spin" />
              ) : null}
              {step === STEPS.length - 1 ? (
                <><Save size={18} strokeWidth={2.5} /> Xuất bản ngay</>
              ) : (
                <><span className="md:inline hidden">Tiếp theo</span> <ChevronRight size={18} strokeWidth={3} /></>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
