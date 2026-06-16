import React from 'react';
import { Plus, Trash2 } from 'lucide-react';
import { TiptapEditor } from '@/components/shared/tiptap-editor/tiptap-editor';
import type { useCreateCourse } from '../../hooks/use-create-course';

type Ctx = ReturnType<typeof useCreateCourse>;

function ListField({ items, placeholder, onAdd, onRemove, onUpdate }: {
  items: string[];
  placeholder: string;
  onAdd: () => void;
  onRemove: (i: number) => void;
  onUpdate: (i: number, v: string) => void;
}) {
  return (
    <div className="space-y-2">
      {items.map((item, i) => (
        <div key={i} className="group flex gap-2">
          <input
            type="text"
            value={item}
            onChange={e => onUpdate(i, e.target.value)}
            placeholder={placeholder}
            className="flex-1 px-4 py-2.5 text-sm font-semibold rounded-2xl bg-white dark:bg-white/5 border border-slate-200 dark:border-white/10 outline-none focus:border-emerald-500 transition-colors"
          />
          <button
            onClick={() => onRemove(i)}
            className="p-2.5 rounded-2xl text-slate-300 hover:text-red-500 hover:bg-red-500/5 transition-all opacity-0 group-hover:opacity-100"
          >
            <Trash2 size={14} strokeWidth={2.5} />
          </button>
        </div>
      ))}
      <button
        onClick={onAdd}
        className="flex items-center gap-1.5 text-[10px] font-black text-emerald-500 uppercase tracking-widest hover:opacity-70 transition-opacity"
      >
        <Plus size={12} strokeWidth={3} /> Thêm
      </button>
    </div>
  );
}

export function StepDetailedContent({ ctx }: { ctx: Ctx }) {
  const { form, updateViField } = ctx;
  const vi = form.translations.vi;

  const addOutcome = () => updateViField('learning_outcomes', [...(vi.learning_outcomes || []), '']);
  const removeOutcome = (i: number) => updateViField('learning_outcomes', vi.learning_outcomes.filter((_: any, j: number) => j !== i));
  const updateOutcome = (i: number, v: string) => { const next = [...vi.learning_outcomes]; next[i] = v; updateViField('learning_outcomes', next); };

  const addPrereq = () => updateViField('prerequisites', [...(vi.prerequisites || []), '']);
  const removePrereq = (i: number) => updateViField('prerequisites', vi.prerequisites.filter((_: any, j: number) => j !== i));
  const updatePrereq = (i: number, v: string) => { const next = [...vi.prerequisites]; next[i] = v; updateViField('prerequisites', next); };

  return (
    <div className="space-y-10">
      <div>
        <h2 className="text-2xl font-black text-slate-900 dark:text-white tracking-tight">Nội dung chi tiết</h2>
        <p className="text-slate-500 text-sm font-semibold mt-1">Nhập nội dung tiếng Việt. AI tự động gen tiếng Anh khi xuất bản.</p>
      </div>

      {/* Description */}
      <div className="space-y-2">
        <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Mô tả chi tiết</label>
        <TiptapEditor value={vi.description || ''} onChange={v => updateViField('description', v)} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
        <div className="space-y-3">
          <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">✅ Kết quả học tập</label>
          <ListField
            items={vi.learning_outcomes || []}
            placeholder="Học viên sẽ..."
            onAdd={addOutcome}
            onRemove={removeOutcome}
            onUpdate={updateOutcome}
          />
        </div>
        <div className="space-y-3">
          <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">⚡ Yêu cầu tiên quyết</label>
          <ListField
            items={vi.prerequisites || []}
            placeholder="Kỹ năng cần có..."
            onAdd={addPrereq}
            onRemove={removePrereq}
            onUpdate={updatePrereq}
          />
        </div>
      </div>
    </div>
  );
}
