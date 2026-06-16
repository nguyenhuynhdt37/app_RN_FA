import { Metadata } from 'next';
import CoursesView from '@/features/courses/components/CoursesView';

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  return {
    title: locale === 'vi' ? 'Khám phá Khóa học - NeuralEarn' : 'Explore Courses - NeuralEarn',
    description: locale === 'vi' ? 'Khám phá danh sách khóa học chất lượng cao trên NeuralEarn' : 'Discover high-quality courses on NeuralEarn',
  };
}

interface Props {
  params: Promise<{
    locale: string;
  }>;
}

export default async function CoursesPage({ params }: Props) {
  const { locale } = await params;

  return (
    <main className="min-h-screen bg-[#050505]">
      {/* Background Decor */}
      <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
        <div className="absolute -left-[10%] -top-[10%] h-[500px] w-[500px] rounded-full bg-emerald-500/10 blur-[120px]" />
        <div className="absolute -right-[10%] bottom-0 h-[400px] w-[400px] rounded-full bg-emerald-500/5 blur-[100px]" />
      </div>

      <div className="relative z-10">
        <CoursesView locale={locale} />
      </div>
    </main>
  );
}
