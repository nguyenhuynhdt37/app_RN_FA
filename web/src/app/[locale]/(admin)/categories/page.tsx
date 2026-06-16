import { CategoriesView } from '@/features/admin-categories/components/CategoriesView';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Danh mục | NeuralEarn Admin',
  description: 'Quản lý danh sách danh mục khóa học.',
};

export default function CategoriesPage() {
  return <CategoriesView />;
}
