'use client';

import { Star, Users, BookOpen, ChevronRight } from 'lucide-react';
import Image from 'next/image';
import { Course } from '../services/course.service';
import { Link } from '@/i18n/routing';
import { useTranslations } from 'next-intl';

interface CourseCardProps {
  course: Course;
}

export function CourseCard({ course }: CourseCardProps) {
  const t = useTranslations('Courses');

  return (
    <Link 
      href={`/explore/${course.id}`}
      className="premium-card group relative flex flex-col overflow-hidden !rounded-[48px] transition-all hover:scale-[1.02] hover:border-emerald-500/50"
    >
      {/* Thumbnail */}
      <div className="relative aspect-video overflow-hidden rounded-[36px]">
        {course.thumbnail_url ? (
          <Image
            src={course.thumbnail_url}
            alt={course.title}
            fill
            className="object-cover transition-transform duration-500 group-hover:scale-110"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center bg-zinc-900">
            <BookOpen size={48} className="text-zinc-700" strokeWidth={1.5} />
          </div>
        )}
        
        {/* Badge Level */}
        <div className="absolute left-4 top-4 rounded-full bg-black/40 px-3 py-1 text-[10px] font-black uppercase tracking-wider text-white backdrop-blur-md border border-white/10">
          {course.level}
        </div>
      </div>

      {/* Content */}
      <div className="flex flex-1 flex-col p-6">
        <div className="mb-3 flex items-center justify-between text-xs font-bold text-zinc-500">
          <div className="flex items-center gap-1.5">
            <Users size={14} className="text-emerald-500" strokeWidth={2.5} />
            <span>{t('enrollCount', { count: course.total_enrolls })}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Star size={14} className="fill-amber-400 text-amber-400" strokeWidth={2.5} />
            <span className="text-zinc-200">{t('rating', { count: course.rating_avg.toFixed(1) })}</span>
          </div>
        </div>

        <h3 className="line-clamp-2 text-xl font-black text-white group-hover:text-emerald-400 transition-colors">
          {course.title}
        </h3>
        
        <p className="mt-2 line-clamp-2 text-sm font-medium leading-relaxed text-zinc-400">
          {course.subtitle}
        </p>

        <div className="mt-auto pt-6">
          <div className="flex items-center justify-between">
            <div className="flex flex-col">
              <span className="text-[10px] font-black uppercase tracking-widest text-zinc-500">{t('price')}</span>
              <div className="flex items-baseline gap-1">
                <span className="text-2xl font-black text-emerald-400">
                  {course.base_price > 0 ? course.base_price.toLocaleString() : t('free')}
                </span>
                {course.base_price > 0 && <span className="text-xs font-bold text-zinc-500">{course.currency}</span>}
              </div>
            </div>
            
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-500 text-white shadow-[0_0_20px_rgba(16,185,129,0.4)] transition-transform group-hover:rotate-[-10deg] group-hover:scale-110">
              <ChevronRight size={24} strokeWidth={3} />
            </div>
          </div>
        </div>
      </div>

      {/* Categories */}
      <div className="flex flex-wrap gap-2 px-6 pb-6">
        {course.categories.slice(0, 2).map((cat) => (
          <span key={cat.id} className="rounded-full bg-white/5 border border-white/5 px-2.5 py-1 text-[10px] font-bold text-zinc-400">
            {cat.name}
          </span>
        ))}
      </div>
    </Link>
  );
}
