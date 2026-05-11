import { LoginForm } from "@/features/auth/components/LoginForm";

export default function LoginPage() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center relative overflow-hidden bg-[#09090b] px-4">
      {/* Background Glow */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-brand-primary/10 blur-[120px]" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-brand-primary/10 blur-[120px]" />

      <div className="z-10 w-full flex flex-col items-center space-y-8">
        <div className="flex items-center space-x-2 mb-4">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-primary to-brand-secondary flex items-center justify-center text-white font-bold text-xl shadow-lg">
            N
          </div>
          <span className="text-2xl font-black tracking-tighter text-white">NeuralEarn</span>
        </div>
        
        <LoginForm />
        
        <p className="text-slate-500 text-sm">
          Bằng cách tiếp tục, bạn đồng ý với <span className="text-slate-300 underline cursor-pointer">Điều khoản dịch vụ</span>
        </p>
      </div>
    </main>
  );
}
