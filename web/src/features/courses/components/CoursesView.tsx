'use client';

import { useState, useEffect } from 'react';
import { Search, SlidersHorizontal, Loader2, BookOpen } from 'lucide-react';
import { courseService, Course } from '../services/course.service';
import { CourseCard } from './CourseCard';
import { toast } from 'sonner';
import { useTranslations } from 'next-intl';

export default function CoursesView({ locale }: { locale: string }) {
  const t = useTranslations('Courses');
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const pageSize = 12;

  const fetchCourses = async () => {
    setLoading(true);
    try {
      const data = await courseService.getCourses({
        page,
        page_size: pageSize,
        search,
        lang: locale,
      });
      setCourses(data.items);
      setTotal(data.total);
    } catch (error) {
      console.error('Error fetching courses:', error);
      toast.error('Không thể tải danh sách khóa học');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchCourses();
    }, 500);
    return () => clearTimeout(timer);
  }, [search, page]);

  return (
    <div className="container mx-auto px-4 py-12">
      {/* Header */}
      <div className="mb-12 flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-4xl font-black text-white md:text-5xl">
            {t.rich('title', {
              span: (chunks) => <span className="text-emerald-500">{chunks}</span>
            })}
          </h1>
          <p className="mt-4 text-lg font-medium text-zinc-400">
            {t('subtitle')}
          </p>
        </div>

        <div className="relative flex w-full flex-col gap-4 md:w-[400px]">
          <div className="group relative flex items-center">
            <Search className="absolute left-4 text-zinc-500 transition-colors group-focus-within:text-emerald-500" size={20} strokeWidth={2.5} />
            <input
              type="text"
              placeholder={t('searchPlaceholder')}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full rounded-full border border-white/10 bg-white/5 py-4 pl-12 pr-6 text-sm font-bold text-white outline-none transition-all focus:border-emerald-500/50 focus:bg-white/10"
            />
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="mb-8 flex items-center gap-4 overflow-x-auto pb-4 scrollbar-hide">
        <button className="flex items-center gap-2 rounded-full bg-emerald-500 px-6 py-2.5 text-sm font-black text-white shadow-[0_0_20px_rgba(16,185,129,0.3)] transition hover:scale-105 active:scale-95">
          <SlidersHorizontal size={16} strokeWidth={3} />
          <span>{t('categories.all')}</span>
        </button>
        {['programming', 'design', 'marketing', 'business'].map((key) => (
          <button key={key} className="whitespace-nowrap rounded-full border border-white/10 bg-white/5 px-6 py-2.5 text-sm font-bold text-zinc-400 transition hover:border-white/20 hover:text-white active:scale-95">
            {t(`categories.${key}`)}
          </button>
        ))}
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex min-h-[400px] flex-col items-center justify-center gap-4">
          <Loader2 className="animate-spin text-emerald-500" size={48} strokeWidth={2.5} />
          <p className="font-black text-zinc-500 uppercase tracking-widest text-xs">{t('loading')}</p>
        </div>
      ) : courses.length > 0 ? (
        <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {courses.map((course) => (
            <CourseCard key={course.id} course={course} />
          ))}
        </div>
      ) : (
        <div className="flex min-h-[400px] flex-col items-center justify-center rounded-[48px] border border-dashed border-white/10 bg-white/5 p-12 text-center">
          <div className="mb-6 flex h-24 w-24 items-center justify-center rounded-[32px] bg-white/5 text-zinc-700">
            <BookOpen size={48} strokeWidth={1.5} />
          </div>
          <h3 className="text-2xl font-black text-white">{t('notFound')}</h3>
          <p className="mt-2 font-medium text-zinc-500">{t('tryAgain')}</p>
        </div>
      )}

      {/* Pagination */}
      {total > pageSize && (
        <div className="mt-16 flex items-center justify-center gap-2">
          {Array.from({ length: Math.ceil(total / pageSize) }).map((_, i) => (
            <button
              key={i}
              onClick={() => setPage(i + 1)}
              className={`h-12 w-12 rounded-2xl text-sm font-black transition-all ${
                page === i + 1
                  ? 'bg-emerald-500 text-white shadow-[0_0_20px_rgba(16,185,129,0.3)]'
                  : 'bg-white/5 text-zinc-500 hover:bg-white/10 hover:text-white'
              }`}
            >
              {i + 1}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
