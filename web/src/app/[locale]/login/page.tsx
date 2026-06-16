'use client';

import { LoginForm } from '@/features/auth/components/login-form';
import { Sparkles } from 'lucide-react';

export default function LoginPage() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-6 bg-white">
      <div className="w-full max-w-sm space-y-8">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 bg-[#00a73d] rounded-2xl mx-auto flex items-center justify-center mb-6">
            <Sparkles size={24} className="text-white" />
          </div>
          <h1 className="text-3xl font-black tracking-tight text-zinc-900">StudyNest</h1>
          <p className="text-zinc-500 font-medium">Đăng nhập vào hệ thống quản trị</p>
        </div>

        <LoginForm />

        <div className="pt-8 border-t border-zinc-100 flex justify-center gap-6">
          <span className="text-[10px] font-bold text-zinc-400 uppercase tracking-widest">Bảo mật</span>
          <span className="text-[10px] font-bold text-zinc-400 uppercase tracking-widest">Tin cậy</span>
          <span className="text-[10px] font-bold text-zinc-400 uppercase tracking-widest">Hiệu quả</span>
        </div>
      </div>
    </main>
  );
}
