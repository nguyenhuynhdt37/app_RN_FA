'use client';

import React, { useState } from 'react';
import { useRouter } from '@/i18n/routing';
import { useAuthStore } from '@/store/auth-store';
import { UserRole } from '@/types/auth';
import { loginAction } from '../actions/auth-actions';

export function LoginForm() {
  const router = useRouter();
  const setUser = useAuthStore(state => state.setUser);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const result = await loginAction(email, password);
      
      if (result.success) {
        // We still set the user in the client store, but we'll fetch real data on the dashboard
        setUser({
          id: '1',
          email,
          fullName: 'Admin User',
          role: 'admin',
        });

        // Small delay to ensure cookies are set before redirect
        router.push('/dashboard');
        router.refresh();
      } else {
        setError(result.error || 'Đăng nhập thất bại.');
      }
    } catch (err: any) {
      setError('Lỗi kết nối server.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleLogin} className="space-y-4 w-full max-w-sm">
      {error && (
        <div className="p-3 rounded-xl bg-red-50 border border-red-100 text-red-600 text-xs font-bold">
          {error}
        </div>
      )}
      
      <div className="space-y-1">
        <label className="text-xs font-bold text-zinc-500 uppercase tracking-widest">Email</label>
        <input 
          type="email" 
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="admin@studynest.vn"
          className="w-full px-4 py-3 rounded-xl border border-zinc-200 focus:border-[#00a73d] focus:ring-1 focus:ring-[#00a73d] outline-none transition-all font-semibold"
          required
          disabled={loading}
        />
      </div>

      <div className="space-y-1">
        <label className="text-xs font-bold text-zinc-500 uppercase tracking-widest">Mật khẩu</label>
        <input 
          type="password" 
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="••••••••"
          className="w-full px-4 py-3 rounded-xl border border-zinc-200 focus:border-[#00a73d] focus:ring-1 focus:ring-[#00a73d] outline-none transition-all font-semibold"
          required
          disabled={loading}
        />
      </div>

      <button 
        type="submit"
        disabled={loading}
        className={`w-full bg-[#00a73d] text-white font-bold py-3 rounded-xl hover:opacity-90 transition-all active:scale-95 shadow-lg shadow-[#00a73d]/20 ${loading ? 'opacity-70 cursor-not-allowed' : ''}`}
      >
        {loading ? 'Đang xác thực...' : 'Đăng nhập'}
      </button>
      
      <p className="text-center text-[10px] text-zinc-400 font-bold uppercase tracking-widest">
        Admin: admin@gmail.com / Huynh@2004
      </p>
    </form>
  );
}

