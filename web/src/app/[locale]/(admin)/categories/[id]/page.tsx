import { CategoryDetailView } from '@/features/admin-categories/components/CategoryDetailView';
import type { Metadata } from 'next';

interface CategoryDetailPageProps {
  params: Promise<{ id: string }>;
}

export const metadata: Metadata = {
  title: 'Chi tiết danh mục | NeuralEarn Admin',
  description: 'Xem thống kê và nội dung đầy đủ của danh mục khóa học.',
};

export default async function CategoryDetailPage({ params }: CategoryDetailPageProps) {
  const { id } = await params;
  return <CategoryDetailView categoryId={id} />;
}
