'use client';

import React, { useState } from 'react';
import { Globe, Shield, Bell, CreditCard, ChevronRight, Save } from 'lucide-react';

const SECTIONS = [
  { icon: Globe, label: 'Nền tảng', id: 'platform' },
  { icon: Shield, label: 'Bảo mật', id: 'security' },
  { icon: Bell, label: 'Thông báo', id: 'notifications' },
  { icon: CreditCard, label: 'Thanh toán', id: 'payment' },
];

const INPUT_CLASS = 'w-full px-4 py-3 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/8 rounded-2xl text-sm font-semibold text-slate-900 dark:text-white outline-none focus:border-emerald-400 focus:ring-2 focus:ring-emerald-400/10 transition-all';
const LABEL_CLASS = 'text-xs font-black text-slate-400 uppercase tracking-[2px] block mb-2';

const PLATFORM_FIELDS = [
  { label: 'Tên nền tảng', value: 'NeuralEarn', type: 'text' },
  { label: 'Website', value: 'https://neuralearn.vn', type: 'url' },
  { label: 'Email liên hệ', value: 'support@neuralearn.vn', type: 'email' },
  { label: 'Tỷ lệ hoa hồng giảng viên (%)', value: '70', type: 'number' },
];

const SECURITY_FIELDS = [
  { label: 'Số lần đăng nhập sai tối đa', value: '5', type: 'number' },
  { label: 'Thời gian khóa tài khoản (phút)', value: '30', type: 'number' },
  { label: 'Thời gian hết hạn token (giờ)', value: '24', type: 'number' },
];

const PAYMENT_FIELDS = [
  { label: 'Số tiền rút tối thiểu (₫)', value: '100000', type: 'number' },
  { label: 'Phí xử lý rút tiền (%)', value: '2', type: 'number' },
  { label: 'Thời gian xử lý (ngày làm việc)', value: '3', type: 'number' },
];

const NOTIFICATION_TOGGLES = [
  { label: 'Email khi có yêu cầu rút tiền mới', enabled: true },
  { label: 'Email khi có hoàn tiền mới', enabled: true },
  { label: 'Email khi người dùng bị cấm', enabled: false },
  { label: 'Thông báo đẩy real-time', enabled: true },
];

export function SettingsView() {
  const [active, setActive] = useState('platform');
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-black text-slate-900 dark:text-white tracking-tight">Cài đặt hệ thống</h1>
        <p className="text-slate-500 font-semibold mt-1">Cấu hình và tùy chỉnh nền tảng NeuralEarn</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Nav */}
        <div className="premium-card p-2 h-fit">
          {SECTIONS.map((s) => (
            <button
              key={s.id}
              onClick={() => setActive(s.id)}
              className={`w-full flex items-center justify-between gap-3 px-4 py-3 rounded-2xl text-sm font-bold transition-all ${active === s.id ? 'bg-emerald-500 text-white' : 'text-slate-500 hover:bg-slate-50 dark:hover:bg-white/5 hover:text-slate-800 dark:hover:text-white'}`}
            >
              <div className="flex items-center gap-3"><s.icon size={16} />{s.label}</div>
              <ChevronRight size={14} className={active === s.id ? 'text-white' : 'text-slate-300'} />
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="lg:col-span-3 space-y-4">
          {active === 'platform' && (
            <div className="premium-card space-y-5">
              <h3 className="font-black text-slate-900 dark:text-white text-lg">Thông tin nền tảng</h3>
              {PLATFORM_FIELDS.map((f) => (
                <div key={f.label}>
                  <label className={LABEL_CLASS}>{f.label}</label>
                  <input type={f.type} defaultValue={f.value} className={INPUT_CLASS} />
                </div>
              ))}
            </div>
          )}

          {active === 'security' && (
            <div className="premium-card space-y-5">
              <h3 className="font-black text-slate-900 dark:text-white text-lg">Bảo mật</h3>
              {SECURITY_FIELDS.map((f) => (
                <div key={f.label}>
                  <label className={LABEL_CLASS}>{f.label}</label>
                  <input type={f.type} defaultValue={f.value} className={INPUT_CLASS} />
                </div>
              ))}
              <div className="flex items-center justify-between p-4 bg-slate-50 dark:bg-white/3 rounded-2xl">
                <div>
                  <p className="font-bold text-slate-900 dark:text-white text-sm">Yêu cầu xác thực 2 bước</p>
                  <p className="text-xs text-slate-400 mt-0.5">Bắt buộc 2FA cho tài khoản admin</p>
                </div>
                <div className="w-12 h-6 bg-emerald-500 rounded-full relative cursor-pointer">
                  <div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full shadow" />
                </div>
              </div>
            </div>
          )}

          {active === 'notifications' && (
            <div className="premium-card space-y-4">
              <h3 className="font-black text-slate-900 dark:text-white text-lg">Thông báo hệ thống</h3>
              {NOTIFICATION_TOGGLES.map((item) => (
                <div key={item.label} className="flex items-center justify-between p-4 bg-slate-50 dark:bg-white/3 rounded-2xl">
                  <p className="font-semibold text-slate-700 dark:text-slate-300 text-sm">{item.label}</p>
                  <div className={`w-12 h-6 ${item.enabled ? 'bg-emerald-500' : 'bg-slate-300 dark:bg-white/20'} rounded-full relative cursor-pointer transition-colors`}>
                    <div className={`absolute top-1 w-4 h-4 bg-white rounded-full shadow transition-all ${item.enabled ? 'right-1' : 'left-1'}`} />
                  </div>
                </div>
              ))}
            </div>
          )}

          {active === 'payment' && (
            <div className="premium-card space-y-5">
              <h3 className="font-black text-slate-900 dark:text-white text-lg">Cấu hình thanh toán</h3>
              {PAYMENT_FIELDS.map((f) => (
                <div key={f.label}>
                  <label className={LABEL_CLASS}>{f.label}</label>
                  <input type={f.type} defaultValue={f.value} className={INPUT_CLASS} />
                </div>
              ))}
            </div>
          )}

          <button
            onClick={handleSave}
            className={`flex items-center gap-2 px-6 py-3 rounded-2xl font-bold text-sm transition-all hover:scale-105 active:scale-95 ${saved ? 'bg-emerald-100 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400' : 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/20 hover:bg-emerald-600'}`}
          >
            <Save size={16} />{saved ? 'Đã lưu!' : 'Lưu thay đổi'}
          </button>
        </div>
      </div>
    </div>
  );
}
