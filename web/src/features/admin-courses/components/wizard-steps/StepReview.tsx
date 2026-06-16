import React from 'react';
import { AlertCircle } from 'lucide-react';
import { COURSE_LEVEL_LABELS, formatCurrency } from '../../types';
import type { useCreateCourse } from '../../hooks/use-create-course';

type Ctx = ReturnType<typeof useCreateCourse>;

function ReviewRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex gap-4 py-3 border-b border-slate-100 dark:border-white/5 last:border-0">
      <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest w-32 shrink-0 pt-0.5">{label}</span>
      <span className="text-sm font-semibold text-slate-700 dark:text-slate-300 flex-1">{value}</span>
    </div>
  );
}

export function StepReview({ ctx }: { ctx: Ctx }) {
  const { form, viTrans, enTrans, thumbnailPreview } = ctx;

  return (
    <div className="space-y-10">
      <div>
        <h2 className="text-2xl font-black text-slate-900 dark:text-white tracking-tight">Xem lại trước khi xuất bản</h2>
        <p className="text-slate-500 text-sm font-semibold mt-1">Kiểm tra thông tin lần cuối. Khoá học sẽ ở trạng thái Draft sau khi tạo.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Preview card */}
        <div className="lg:col-span-1">
          <div className="rounded-2xl overflow-hidden border border-slate-100 dark:border-white/5 bg-white dark:bg-white/5">
            {thumbnailPreview
              ? <img src={thumbnailPreview} alt="thumbnail" className="aspect-video w-full object-cover" />
              : <div className="aspect-video bg-slate-100 dark:bg-white/5 flex items-center justify-center text-slate-300 text-xs font-bold">Chưa có ảnh bìa</div>
            }
            <div className="p-5 space-y-2">
              <div className="flex gap-1.5 flex-wrap">
                <span className="px-2.5 py-0.5 rounded-full bg-emerald-500 text-white text-[10px] font-black">
                  {COURSE_LEVEL_LABELS[form.level as keyof typeof COURSE_LEVEL_LABELS] || form.level}
                </span>
                <span className="px-2.5 py-0.5 rounded-full bg-slate-100 dark:bg-white/10 text-slate-500 text-[10px] font-black">
                  {form.estimated_duration ? `${form.estimated_duration} phút` : 'Thời lượng chưa có'}
                </span>
              </div>
              <p className="text-base font-black text-slate-900 dark:text-white line-clamp-2">{viTrans.title || '—'}</p>
              <p className="text-xs font-semibold text-slate-500 line-clamp-2">{viTrans.subtitle || ''}</p>
              <p className="text-lg font-black text-emerald-500 pt-1">
                {form.base_price === 0 ? 'Miễn phí' : formatCurrency(form.base_price)}
              </p>
            </div>
          </div>
        </div>

        {/* Details */}
        <div className="lg:col-span-2 space-y-6">
          <div className="rounded-2xl bg-white dark:bg-white/5 border border-slate-100 dark:border-white/5 px-6 py-2">
            <ReviewRow label="Tiêu đề EN" value={enTrans.title
              ? enTrans.title
              : <span className="flex items-center gap-1 text-amber-500"><AlertCircle size={12} /> Chưa có — nhấn AI Magic</span>
            } />
            <ReviewRow label="Cấp độ" value={COURSE_LEVEL_LABELS[form.level as keyof typeof COURSE_LEVEL_LABELS] || form.level} />
            <ReviewRow label="Thời lượng" value={form.estimated_duration ? `${form.estimated_duration} phút` : '—'} />
            <ReviewRow label="Danh mục" value={form.category_ids.length ? `${form.category_ids.length} danh mục` : '—'} />
            <ReviewRow
              label="Tags"
              value={form.tags.length
                ? <div className="flex flex-wrap gap-1">{form.tags.map((t: string) => (
                  <span key={t} className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-500 text-[10px] font-black border border-emerald-500/20">#{t}</span>
                ))}</div>
                : '—'
              }
            />
            <ReviewRow label="Kết quả học" value={`${viTrans.learning_outcomes?.length || 0} mục`} />
            <ReviewRow label="Yêu cầu" value={`${viTrans.prerequisites?.length || 0} mục`} />
          </div>

          {!enTrans.title && (
            <div className="flex items-start gap-3 px-5 py-4 rounded-2xl bg-amber-500/5 border border-amber-500/20">
              <AlertCircle size={16} className="text-amber-500 shrink-0 mt-0.5" strokeWidth={2.5} />
              <p className="text-xs font-semibold text-amber-600 dark:text-amber-400">
                Chưa có bản dịch tiếng Anh. Quay lại Bước 1 và nhấn <b>AI Magic</b> để đồng bộ trước khi xuất bản.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
