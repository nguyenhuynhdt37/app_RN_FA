'use client';

import React from 'react';
import { Layers } from 'lucide-react';
import { useCoursesManagement } from '../hooks/use-courses-management';

// Components
import { CoursesHeader } from './CoursesHeader';
import { CoursesFilters } from './CoursesFilters';
import { CoursesPagination } from './CoursesPagination';
import { CourseStatsCards } from './CourseStatsCards';
import { CourseCard } from './CourseCard';
import { CoursesTable } from './CoursesTable';
import { DeleteConfirmModal } from './DeleteConfirmModal';

export function CoursesView() {
  const {
    courses, categories, loading, total, totalPages, stats,
    viewMode, search, sortBy, statusFilter, levelFilter, categoryFilter,
    editingCourse, deletingCourse, deleteReason, hasFilters, currentPage,
    setViewMode, setSearch, setSortBy, setStatusFilter, setLevelFilter, 
    setCategoryFilter, setEditingCourse, setDeletingCourse, setDeleteReason,
    fetchCourses, fetchStats, handleDelete, resetFilters, goToPage
  } = useCoursesManagement();

  return (
    <div className="space-y-6">
      <CoursesHeader 
        loading={loading} 
        onRefresh={() => { fetchCourses(); fetchStats(); }} 
      />

      <CourseStatsCards
        totalCourses={stats.total_courses}
        totalEnrolls={stats.total_enrolls}
        totalRevenue={stats.total_revenue}
        avgRating={stats.avg_rating}
      />

      <CoursesFilters
        search={search}
        setSearch={setSearch}
        sortBy={sortBy}
        setSortBy={setSortBy}
        levelFilter={levelFilter}
        setLevelFilter={setLevelFilter}
        categoryFilter={categoryFilter}
        setCategoryFilter={setCategoryFilter}
        statusFilter={statusFilter}
        setStatusFilter={setStatusFilter}
        viewMode={viewMode}
        setViewMode={setViewMode}
        categories={categories}
        total={total}
        filteredCount={courses.length}
        hasFilters={hasFilters}
        onReset={resetFilters}
      />

      {/* Content Area */}
      {loading && courses.length === 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="premium-card h-64 animate-pulse bg-slate-100 dark:bg-white/5" />
          ))}
        </div>
      ) : courses.length === 0 ? (
        <div className="premium-card p-20 flex flex-col items-center justify-center text-center">
          <div className="w-16 h-16 rounded-[24px] bg-slate-100 dark:bg-white/5 flex items-center justify-center mb-4">
            <Layers size={24} className="text-slate-400" />
          </div>
          <p className="font-bold text-slate-500">Không tìm thấy khóa học nào</p>
          <p className="text-xs text-slate-400 font-semibold mt-1 max-w-xs mx-auto">
            Thử thay đổi bộ lọc hoặc tạo khóa học mới để bắt đầu hành trình kiến thức.
          </p>
          {hasFilters && (
            <button
              onClick={resetFilters}
              className="mt-6 px-8 py-2.5 bg-emerald-500 text-white font-bold text-sm rounded-full hover:bg-emerald-600 transition-all shadow-lg shadow-emerald-500/20"
            >
              Xóa bộ lọc
            </button>
          )}
        </div>
      ) : viewMode === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {courses.map(course => (
            <CourseCard
              key={course.id}
              course={course}
              onEdit={c => { /* logic to handle edit if needed */ }}
              onDelete={c => setDeletingCourse(c)}
            />
          ))}
        </div>
      ) : (
        <CoursesTable
          data={courses}
          categories={categories}
          onEdit={c => { /* logic to handle edit if needed */ }}
          onDelete={c => setDeletingCourse(c)}
        />
      )}

      <CoursesPagination 
        currentPage={currentPage} 
        totalPages={totalPages} 
        onPageChange={goToPage} 
      />

      {/* Modals */}
      <DeleteConfirmModal
        isOpen={!!deletingCourse}
        course={deletingCourse}
        reason={deleteReason}
        onReasonChange={setDeleteReason}
        onClose={() => { setDeletingCourse(null); setDeleteReason(''); }}
        onConfirm={handleDelete}
      />
    </div>
  );
}
