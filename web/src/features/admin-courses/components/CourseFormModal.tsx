'use client';

import React, { useState } from 'react';
import {
  X, Sparkles, Loader2, Save, Globe, Plus, Trash2, Upload,
  ChevronRight, ChevronLeft, CheckCircle, AlertCircle,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import {
  AdminCourse, CourseCategory, AIAnalysisResult,
  CourseFormData, createEmptyCourseForm, SupportedLang
} from '../types';
import { adminCourseService } from '../services/courses';
import { toast } from 'sonner';
import { TiptapEditor } from '@/components/shared/tiptap-editor/tiptap-editor';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CourseFormData, thumbnailFile?: File) => void;
  categories: CourseCategory[];
  initialData?: AdminCourse | null;
}

export function CourseFormModal({ isOpen, onClose, onSubmit, categories, initialData }: Props) {
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [lang, setLang] = useState<SupportedLang>('vi');
  const [thumbnailFile, setThumbnailFile] = useState<File | null>(null);
  const [thumbnailPreview, setThumbnailPreview] = useState<string | null>(initialData?.thumbnail_url || null);

  const initForm = (): CourseFormData => {
    if (initialData?.translations) {
      return {
        translations: {
          vi: {
            title: initialData.translations.vi?.title || '',
            subtitle: initialData.translations.vi?.subtitle || '',
            description: initialData.translations.vi?.description || '',
            learning_outcomes: initialData.translations.vi?.learning_outcomes || [],
            prerequisites: initialData.translations.vi?.prerequisites || [],
          },
          en: {
            title: initialData.translations.en?.title || '',
            subtitle: initialData.translations.en?.subtitle || '',
            description: initialData.translations.en?.description || '',
            learning_outcomes: initialData.translations.en?.learning_outcomes || [],
            prerequisites: initialData.translations.en?.prerequisites || [],
          },
        },
        slug: initialData.slug,
        thumbnail_url: initialData.thumbnail_url,
        preview_video_type: initialData.preview_video_type,
        level: initialData.level || 'BEGINNER',
        language: initialData.language || 'vi',
        tags: initialData.tags || [],
        difficulty_score: initialData.difficulty_score,
        estimated_duration: initialData.estimated_duration,
        base_price: initialData.base_price || 0,
        currency: initialData.currency || 'VND',
        category_ids: initialData.category_ids || [],
        is_published: initialData.is_published || false,
      };
    }
    return createEmptyCourseForm();
  };

  const [form, setForm] = useState<CourseFormData>(initForm);

  if (!isOpen) return null;

  const t_ui = useTranslations('Admin.courses');
  const currentTranslation = form.translations[lang as 'vi' | 'en'];

  const updateTranslation = (field: string, value: string | string[] | number) => {
    setForm(f => ({
      ...f,
      translations: {
        ...f.translations,
        [lang]: { ...f.translations[lang as keyof typeof f.translations], [field]: value },
      },
    }));
  };

  const handleAi = async () => {
    const currentTitle = currentTranslation.title;
    if (!currentTitle) { toast.error('Nhập tiêu đề trước!'); return; }

    setAiLoading(true);
    try {
      const r: AIAnalysisResult = await adminCourseService.analyzeCourse(currentTitle, currentTranslation.description || '');

      if (r.translations?.vi && r.translations?.en) {
        setForm(f => ({
          ...f,
          translations: {
            vi: r.translations.vi,
            en: r.translations.en,
          },
          level: r.suggested_level || f.level,
          tags: r.suggested_tags?.length ? r.suggested_tags : f.tags,
          difficulty_score: r.difficulty_score || f.difficulty_score,
        }));
        toast.success('AI đã phân tích và dịch song ngữ!');
      } else {
        toast.error('AI trả về dữ liệu không hợp lệ.');
      }
    } catch { toast.error('AI gặp sự cố.'); }
    finally { setAiLoading(false); }
  };

  const handleThumbnailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 2 * 1024 * 1024) {
        toast.error('Ảnh quá lớn (tối đa 2MB)');
        return;
      }
      setThumbnailFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setThumbnailPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async () => {
    if (!form.translations.vi.title) {
      toast.error('Tiêu đề tiếng Việt là bắt buộc!');
      return;
    }

    setLoading(true);
    try {
      await onSubmit(form, thumbnailFile || undefined);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-dark-card rounded-3xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">

        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/10">
          <h2 className="text-xl font-bold text-white">
            {initialData ? 'Sửa khóa học' : 'Tạo khóa học mới'}
          </h2>
          <button onClick={onClose} className="p-2 rounded-xl hover:bg-white/10 transition-colors">
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Language Toggle */}
        <div className="flex gap-2 px-6 py-3 border-b border-white/10">
          {(['vi', 'en'] as SupportedLang[]).map(l => (
            <button
              key={l}
              onClick={() => setLang(l)}
              className={cn(
                "px-4 py-2 rounded-xl font-medium transition-all",
                lang === l
                  ? "bg-emerald-500 text-white shadow-lg shadow-emerald-500/30"
                  : "bg-white/5 text-gray-400 hover:bg-white/10"
              )}
            >
              {l === 'vi' ? '🇻🇳 Tiếng Việt' : '🇺🇸 English'}
            </button>
          ))}
        </div>

        {/* Form Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">

          {/* Thumbnail */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Ảnh đại diện khóa học</label>
            <div className="flex items-center gap-4">
              <div className="relative w-40 h-24 rounded-xl bg-white/5 border border-white/10 overflow-hidden flex items-center justify-center">
                {thumbnailPreview ? (
                  <img src={thumbnailPreview} alt="Preview" className="w-full h-full object-cover" />
                ) : (
                  <Upload className="w-6 h-6 text-gray-500" />
                )}
              </div>
              <div className="flex-1">
                <input
                  type="file"
                  id="thumbnail-upload"
                  className="hidden"
                  accept="image/*"
                  onChange={handleThumbnailChange}
                />
                <label
                  htmlFor="thumbnail-upload"
                  className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 text-white rounded-xl text-sm font-medium hover:bg-white/20 cursor-pointer transition-colors"
                >
                  <Upload className="w-4 h-4" /> Chọn ảnh
                </label>
                <p className="mt-2 text-xs text-gray-500">Khuyên dùng tỷ lệ 16:9, tối đa 2MB.</p>
              </div>
            </div>
          </div>

          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              {t_ui('table.course')} {lang === 'vi' ? '🇻🇳' : '🇺🇸'} *
            </label>
            <input
              type="text"
              value={currentTranslation.title}
              onChange={e => updateTranslation('title', e.target.value)}
              placeholder={lang === 'vi' ? 'VD: Lập trình Python cơ bản' : 'VD: Basic Python Programming'}
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 transition-all"
            />
          </div>

          {/* Subtitle */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              {t_ui('table.description')}
            </label>
            <input
              type="text"
              value={currentTranslation.subtitle || ''}
              onChange={e => updateTranslation('subtitle', e.target.value)}
              placeholder={lang === 'vi' ? 'Một dòng mô tả hấp dẫn về khóa học' : 'A compelling one-liner about the course'}
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:border-emerald-500 transition-all"
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              {t_ui('table.description')} (Markdown)
            </label>
            <TiptapEditor
              value={currentTranslation.description || ''}
              onChange={val => updateTranslation('description', val)}
              placeholder={lang === 'vi' ? '## Giới thiệu\n\nMô tả chi tiết khóa học...' : '## Introduction\n\nDetailed course description...'}
            />
          </div>

          {/* Learning Outcomes */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Kết quả học tập
            </label>
            <div className="space-y-2">
              {(currentTranslation.learning_outcomes || []).map((item, i) => (
                <div key={i} className="flex gap-2">
                  <input
                    type="text"
                    value={item}
                    onChange={e => {
                      const newList = [...(currentTranslation.learning_outcomes || [])];
                      newList[i] = e.target.value;
                      updateTranslation('learning_outcomes', newList);
                    }}
                    placeholder={lang === 'vi' ? 'Sau khóa học, bạn sẽ...' : 'After this course, you will...'}
                    className="flex-1 px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 text-sm focus:border-emerald-500"
                  />
                  <button
                    onClick={() => {
                      const newList = (currentTranslation.learning_outcomes || []).filter((_, idx) => idx !== i);
                      updateTranslation('learning_outcomes', newList);
                    }}
                    className="p-2 text-red-400 hover:bg-red-500/10 rounded-xl"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
              <button
                onClick={() => updateTranslation('learning_outcomes', [...(currentTranslation.learning_outcomes || []), ''])}
                className="flex items-center gap-2 px-4 py-2 text-emerald-400 hover:bg-emerald-500/10 rounded-xl text-sm"
              >
                <Plus className="w-4 h-4" /> Thêm kết quả
              </button>
            </div>
          </div>

          {/* Prerequisites */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Yêu cầu trước khi học
            </label>
            <div className="space-y-2">
              {(currentTranslation.prerequisites || []).map((item, i) => (
                <div key={i} className="flex gap-2">
                  <input
                    type="text"
                    value={item}
                    onChange={e => {
                      const newList = [...(currentTranslation.prerequisites || [])];
                      newList[i] = e.target.value;
                      updateTranslation('prerequisites', newList);
                    }}
                    placeholder={lang === 'vi' ? 'Yêu cầu cần có...' : 'Prerequisite requirement...'}
                    className="flex-1 px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 text-sm focus:border-emerald-500"
                  />
                  <button
                    onClick={() => {
                      const newList = (currentTranslation.prerequisites || []).filter((_, idx) => idx !== i);
                      updateTranslation('prerequisites', newList);
                    }}
                    className="p-2 text-red-400 hover:bg-red-500/10 rounded-xl"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
              <button
                onClick={() => updateTranslation('prerequisites', [...(currentTranslation.prerequisites || []), ''])}
                className="flex items-center gap-2 px-4 py-2 text-emerald-400 hover:bg-emerald-500/10 rounded-xl text-sm"
              >
                <Plus className="w-4 h-4" /> Thêm yêu cầu
              </button>
            </div>
          </div>

          {/* Categories Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-3">
              {t_ui('table.category')}
            </label>
            <div className="grid grid-cols-2 gap-3 p-4 bg-white/5 border border-white/10 rounded-2xl max-h-[200px] overflow-y-auto">
              {categories.map((cat) => {
                const isSelected = form.category_ids.includes(cat.id);
                const name = cat.translations.vi?.name || cat.translations.en?.name || cat.id;

                return (
                  <button
                    key={cat.id}
                    onClick={() => {
                      setForm(f => ({
                        ...f,
                        category_ids: isSelected
                          ? f.category_ids.filter(id => id !== cat.id)
                          : [...f.category_ids, cat.id]
                      }));
                    }}
                    className={cn(
                      "flex items-center gap-3 p-2.5 rounded-xl transition-all text-left group",
                      isSelected
                        ? "bg-emerald-500/20 border border-emerald-500/30 text-emerald-400"
                        : "bg-white/5 border border-transparent text-gray-400 hover:bg-white/10"
                    )}
                  >
                    <div className={cn(
                      "flex h-5 w-5 shrink-0 items-center justify-center rounded-lg border transition-all",
                      isSelected
                        ? "border-emerald-500 bg-emerald-500 text-white"
                        : "border-white/20 bg-white/5 group-hover:border-white/40"
                    )}>
                      {isSelected && <Check size={12} strokeWidth={4} />}
                    </div>
                    <span className="text-xs font-bold truncate">{name}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Categories Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-3">
              {t_ui('table.category')}
            </label>
            <div className="grid grid-cols-2 gap-3 p-4 bg-white/5 border border-white/10 rounded-2xl max-h-[200px] overflow-y-auto">
              {categories.map((cat) => {
                const isSelected = form.category_ids.includes(cat.id);
                const name = cat.translations.vi?.name || cat.translations.en?.name || cat.id;

                return (
                  <button
                    key={cat.id}
                    onClick={() => {
                      setForm(f => ({
                        ...f,
                        category_ids: isSelected
                          ? f.category_ids.filter(id => id !== cat.id)
                          : [...f.category_ids, cat.id]
                      }));
                    }}
                    className={cn(
                      "flex items-center gap-3 p-2.5 rounded-xl transition-all text-left group",
                      isSelected
                        ? "bg-emerald-500/20 border border-emerald-500/30 text-emerald-400"
                        : "bg-white/5 border border-transparent text-gray-400 hover:bg-white/10"
                    )}
                  >
                    <div className={cn(
                      "flex h-5 w-5 shrink-0 items-center justify-center rounded-lg border transition-all",
                      isSelected
                        ? "border-emerald-500 bg-emerald-500 text-white"
                        : "border-white/20 bg-white/5 group-hover:border-white/40"
                    )}>
                      {isSelected && <Check size={12} strokeWidth={4} />}
                    </div>
                    <span className="text-xs font-bold truncate">{name}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Basic Info */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">{t_ui('table.level')}</label>
              <select
                value={form.level}
                onChange={e => setForm(f => ({ ...f, level: e.target.value as any }))}
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:border-emerald-500 appearance-none"
              >
                <option value="BEGINNER">{t_ui('level.BEGINNER')}</option>
                <option value="INTERMEDIATE">{t_ui('level.INTERMEDIATE')}</option>
                <option value="ADVANCED">{t_ui('level.ADVANCED')}</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Thời lượng (phút)</label>
              <input
                type="number"
                value={form.estimated_duration || ''}
                onChange={e => setForm(f => ({ ...f, estimated_duration: Number(e.target.value) }))}
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:border-emerald-500"
              />
            </div>
          </div>

          {/* Price */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">{t_ui('table.revenue')} (VND)</label>
              <input
                type="number"
                value={form.base_price}
                onChange={e => setForm(f => ({ ...f, base_price: Number(e.target.value) }))}
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:border-emerald-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Tags</label>
              <input
                type="text"
                value={form.tags?.join(', ') || ''}
                onChange={e => setForm(f => ({ ...f, tags: e.target.value.split(',').map(t => t.trim()).filter(Boolean) }))}
                placeholder="python, programming, beginner"
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:border-emerald-500"
              />
            </div>
          </div>

          {/* Publish */}
          <label className="flex items-center gap-3 p-4 bg-white/5 rounded-xl cursor-pointer hover:bg-white/10 transition-colors">
            <input
              type="checkbox"
              checked={form.is_published}
              onChange={e => setForm(f => ({ ...f, is_published: e.target.checked }))}
              className="w-5 h-5 rounded bg-white/10 border-white/20 text-emerald-500 focus:ring-emerald-500"
            />
            <span className="text-white font-medium">{t_ui('status.published')}</span>
          </label>

        </div>

        {/* Footer */}
        <div className="flex items-center justify-between gap-4 px-6 py-4 border-t border-white/10">
          <button
            onClick={handleAi}
            disabled={aiLoading}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-violet-500 to-purple-500 text-white rounded-xl font-medium hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            {aiLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
            AI Dịch song ngữ
          </button>

          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="px-6 py-3 text-gray-400 hover:text-white transition-colors"
            >
              Hủy
            </button>
            <button
              onClick={() => onSubmit(form)}
              disabled={loading}
              className="flex items-center gap-2 px-6 py-3 bg-emerald-500 text-white rounded-xl font-medium hover:bg-emerald-600 transition-colors disabled:opacity-50"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
              {initialData ? 'Lưu thay đổi' : 'Tạo khóa học'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
