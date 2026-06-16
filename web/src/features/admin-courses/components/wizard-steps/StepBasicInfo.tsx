import React from 'react';
import { Sparkles } from 'lucide-react';
import { TiptapEditor } from '@/components/shared/tiptap-editor/tiptap-editor';
import type { useCreateCourse } from '../../hooks/use-create-course';

type Ctx = ReturnType<typeof useCreateCourse>;

export function StepBasicInfo({ ctx }: { ctx: Ctx }) {
  const { viTrans, updateViField } = ctx;

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-black text-slate-900 dark:text-white tracking-tight">Thông tin cơ bản</h2>
        <p className="text-slate-500 text-sm font-semibold mt-1">Nhập nội dung tiếng Việt. AI sẽ tự động dịch sang tiếng Anh khi bạn xuất bản.</p>
      </div>

      {/* Title */}
      <div className="space-y-2">
        <label className="block text-[10px] font-black text-slate-400 uppercase tracking-widest">
          Tiêu đề khoá học *
        </label>
        <input
          type="text"
          value={viTrans.title}
          onChange={e => updateViField('title', e.target.value)}
          placeholder="VD: Lập trình Python từ con số 0"
          className="w-full px-5 py-4 text-lg font-bold rounded-2xl bg-white dark:bg-white/5 border border-slate-200 dark:border-white/10 outline-none focus:border-emerald-500 transition-colors"
        />
      </div>

      {/* Subtitle */}
      <div className="space-y-2">
        <label className="block text-[10px] font-black text-slate-400 uppercase tracking-widest">
          Mô tả ngắn
        </label>
        <TiptapEditor
          value={viTrans.subtitle ?? ''}
          onChange={v => updateViField('subtitle', v)}
          placeholder="Tóm tắt giá trị khoá học trong 1-2 câu..."
        />
      </div>

      {/* AI notice */}
      <div className="flex items-start gap-3 px-5 py-4 rounded-2xl bg-emerald-500/5 border border-emerald-500/20">
        <Sparkles size={16} className="text-emerald-500 shrink-0 mt-0.5" strokeWidth={2.5} />
        <p className="text-xs font-semibold text-emerald-700 dark:text-emerald-400">
          Sau khi xuất bản, AI sẽ tự động tạo bản dịch tiếng Anh, gợi ý tags và đánh giá cấp độ dựa trên nội dung bạn nhập.
        </p>
      </div>
    </div>
  );
}
