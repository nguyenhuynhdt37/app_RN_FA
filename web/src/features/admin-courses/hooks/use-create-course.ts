import { useState, useEffect } from 'react';
import { useRouter } from '@/i18n/routing';
import { toast } from 'sonner';
import { adminCourseService, CourseApiError } from '../services/courses';
import { CourseFormData, createEmptyCourseForm, CourseCategory } from '../types';

export function useCreateCourse() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [categories, setCategories] = useState<CourseCategory[]>([]);
  const [form, setForm] = useState<CourseFormData>(createEmptyCourseForm());
  const [thumbnailFile, setThumbnailFile] = useState<File | null>(null);
  const [thumbnailPreview, setThumbnailPreview] = useState<string | null>(null);

  useEffect(() => {
    adminCourseService.getCategories()
      .then((raw: any[]) =>
        setCategories(raw.map(item => ({
          id: item.id,
          translations: item.translations || {},
          icon_url: item.icon,
          position: item.position || 0,
        })))
      )
      .catch(() => toast.error('Không thể tải danh mục.'));
  }, []);

  const updateForm = (updates: Partial<CourseFormData>) =>
    setForm(prev => ({ ...prev, ...updates }));

  const updateViField = (field: string, value: any) =>
    setForm(prev => ({
      ...prev,
      translations: {
        ...prev.translations,
        vi: { ...prev.translations.vi, [field]: value },
      },
    }));

  const goNext = () => {
    if (step === 0 && !form.translations.vi.title) {
      toast.error('Vui lòng nhập tiêu đề tiếng Việt!');
      return;
    }
    setStep(s => s + 1);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const goBack = () => {
    setStep(s => s - 1);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const onThumbnailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > 2 * 1024 * 1024) { toast.error('Ảnh phải nhỏ hơn 2MB.'); return; }
    setThumbnailFile(file);
    const reader = new FileReader();
    reader.onloadend = () => setThumbnailPreview(reader.result as string);
    reader.readAsDataURL(file);
  };

  const submit = async () => {
    setLoading(true);
    try {
      // Backend tự đồng bộ AI (EN translation + tags) trước khi trả về
      const course = await adminCourseService.createCourse(form);
      if (thumbnailFile) await adminCourseService.uploadThumbnail(course.id, thumbnailFile);
      toast.success('Khóa học đã tạo thành công! AI đã tự động gen tiếng Anh.');
      router.push('/courses');
    } catch (err) {
      const code = err instanceof CourseApiError ? err.code : 'UNKNOWN';
      toast.error(`Lỗi tạo khóa học: ${code}`);
    } finally {
      setLoading(false);
    }
  };

  return {
    step, loading, categories, form,
    thumbnailPreview, updateForm, updateViField,
    goNext, goBack, onThumbnailChange, submit,
    viTrans: form.translations.vi,
  };
}
