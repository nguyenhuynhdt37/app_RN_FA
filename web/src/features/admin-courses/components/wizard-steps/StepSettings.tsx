import React from 'react';
import { Check, Upload } from 'lucide-react';
import { cn } from '@/lib/utils';
import { COURSE_LEVEL_LABELS } from '../../types';
import type { useCreateCourse } from '../../hooks/use-create-course';

type Ctx = ReturnType<typeof useCreateCourse>;

export function StepSettings({ ctx }: { ctx: Ctx }) {
  const { form, updateForm, thumbnailPreview, onThumbnailChange, categories } = ctx;

  const toggleCategory = (id: string) => {
    const next = form.category_ids.includes(id)
      ? form.category_ids.filter((c: string) => c !== id)
      : [...form.category_ids, id];
    updateForm({ category_ids: next });
  };

  return (
    <div className="space-y-10">
      <div>
        <h2 className="text-2xl font-black text-slate-900 dark:text-white tracking-tight">Thiết lập & Giá</h2>
        <p className="text-slate-500 text-sm font-semibold mt-1">Cấu hình kỹ thuật, ảnh bìa và định giá khoá học.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
        {/* Left */}
        <div className="space-y-6">
          {/* Thumbnail */}
          <div className="space-y-2">
            <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Ảnh bìa (16:9)</label>
            <label htmlFor="thumb-upload" className="relative block aspect-video rounded-2xl bg-slate-100 dark:bg-white/5 border-2 border-dashed border-slate-200 dark:border-white/10 overflow-hidden cursor-pointer group">
              {thumbnailPreview
                ? <img src={thumbnailPreview} alt="preview" className="w-full h-full object-cover" />
                : (
                  <div className="flex flex-col items-center justify-center h-full gap-2">
                    <Upload size={24} className="text-slate-400" strokeWidth={2} />
                    <span className="text-xs font-bold text-slate-400">Tải ảnh lên</span>
                  </div>
                )
              }
              {thumbnailPreview && (
                <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  <span className="text-white text-xs font-black uppercase tracking-widest">Thay đổi</span>
                </div>
              )}
            </label>
            <input type="file" id="thumb-upload" className="hidden" accept="image/*" onChange={onThumbnailChange} />
          </div>

          {/* Level + Duration */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Cấp độ</label>
              <select
                value={form.level}
                onChange={e => updateForm({ level: e.target.value as any })}
                className="w-full px-4 py-3 text-sm font-semibold rounded-2xl bg-white dark:bg-white/5 border border-slate-200 dark:border-white/10 outline-none focus:border-emerald-500 transition-colors appearance-none"
              >
                {Object.entries(COURSE_LEVEL_LABELS).map(([v, l]) => (
                  <option key={v} value={v}>{l}</option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Thời lượng (phút)</label>
              <input
                type="number"
                value={form.estimated_duration || ''}
                onChange={e => updateForm({ estimated_duration: Number(e.target.value) })}
                placeholder="120"
                className="w-full px-4 py-3 text-sm font-semibold rounded-2xl bg-white dark:bg-white/5 border border-slate-200 dark:border-white/10 outline-none focus:border-emerald-500 transition-colors"
              />
            </div>
          </div>
        </div>

        {/* Right */}
        <div className="space-y-6">
          {/* Price */}
          <div className="space-y-2">
            <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Giá (VNĐ)</label>
            <div className="relative">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 font-black text-emerald-500 text-sm">₫</span>
              <input
                type="number"
                value={form.base_price || ''}
                onChange={e => updateForm({ base_price: Number(e.target.value) })}
                placeholder="0"
                className="w-full pl-9 pr-4 py-3 text-xl font-black rounded-2xl bg-white dark:bg-white/5 border border-slate-200 dark:border-white/10 outline-none focus:border-emerald-500 transition-colors"
              />
            </div>
            <p className="text-[10px] text-slate-400 font-semibold px-1">Để 0 nếu miễn phí</p>
          </div>

          {/* Categories */}
          <div className="space-y-2">
            <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Danh mục</label>
            <div className="grid grid-cols-2 gap-2">
              {categories.map((cat: any) => {
                const selected = form.category_ids.includes(cat.id);
                const name = cat.translations?.vi?.name || cat.translations?.en?.name || '—';
                return (
                  <button
                    key={cat.id}
                    onClick={() => toggleCategory(cat.id)}
                    className={cn(
                      'flex items-center gap-2 px-3 py-2.5 rounded-2xl border text-xs font-bold transition-all text-left',
                      selected
                        ? 'bg-emerald-500 border-emerald-500 text-white'
                        : 'bg-white dark:bg-white/5 border-slate-200 dark:border-white/10 text-slate-600 dark:text-slate-400 hover:border-emerald-400',
                    )}
                  >
                    {selected && <Check size={12} strokeWidth={3} />}
                    <span className="truncate">{name}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Tags */}
          <div className="space-y-2">
            <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Tags (phân cách bằng dấu phẩy)</label>
            <input
              type="text"
              value={form.tags.join(', ')}
              onChange={e => updateForm({ tags: e.target.value.split(',').map((t: string) => t.trim()).filter(Boolean) })}
              placeholder="python, backend, ai..."
              className="w-full px-4 py-3 text-sm font-semibold rounded-2xl bg-white dark:bg-white/5 border border-slate-200 dark:border-white/10 outline-none focus:border-emerald-500 transition-colors"
            />
            {form.tags.length > 0 && (
              <div className="flex flex-wrap gap-1.5 pt-1">
                {form.tags.map((t: string) => (
                  <span key={t} className="px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-500 text-[10px] font-black border border-emerald-500/20">
                    #{t}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
