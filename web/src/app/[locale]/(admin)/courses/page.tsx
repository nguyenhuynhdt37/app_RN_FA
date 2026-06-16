import { CoursesView } from "@/features/admin-courses/components/CoursesView";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Quản lý Khóa học | NeuralEarn Admin",
  description: "Quản lý lộ trình học tập và nội dung khóa học.",
};

export default function AdminCoursesPage() {
  return <CoursesView />;
}
