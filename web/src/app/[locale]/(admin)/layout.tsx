import React from 'react';
import { AdminLayoutClient } from './layout-client';
import { requireAdminRole } from '@/lib/auth-server';

export default async function AdminLayout({
  children,
  params
}: {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;

  // Check RBAC before rendering the layout
  await requireAdminRole(locale);
  
  return <AdminLayoutClient>{children}</AdminLayoutClient>;
}
