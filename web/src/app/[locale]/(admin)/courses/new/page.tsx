import { CreateCourseWizard } from "@/features/admin-courses/components/CreateCourseWizard";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Tạo Khóa Học Mới | NeuralEarn Admin",
  description: "Thiết kế khóa học mới với sự hỗ trợ của AI.",
};

export default function CreateCoursePage() {
  return (
    <div className="container mx-auto py-8">
      <CreateCourseWizard />
    </div>
  );
}
