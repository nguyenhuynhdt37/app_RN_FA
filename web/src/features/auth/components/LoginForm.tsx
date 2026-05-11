import { useState } from "react";
import { useTranslations } from "next-intl";
import { authService } from "../services/auth";

export function LoginForm() {
  const t = useTranslations("Auth.login");
  const tc = useTranslations("Common");
  
  const [identifier, setIdentifier] = useState("");
  const [otp, setOtp] = useState("");
  const [step, setStep] = useState<"identifier" | "otp">("identifier");
  const [loading, setLoading] = useState(false);

  const handleSendOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await authService.sendOtp(identifier, "authenticate");
      setStep("otp");
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const { otp_token } = await authService.verifyOtp(identifier, otp, "authenticate");
      await authService.authenticate(otp_token);
      window.location.href = "/dashboard";
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-card p-8 w-full max-w-md space-y-6">
      <div className="text-center space-y-2">
        <h2 className="text-3xl font-black tracking-tighter text-white">
          {t("title")}
        </h2>
        <p className="text-zinc-400 text-sm">
          {step === "identifier" 
            ? t("description") 
            : t("otpDescription", { identifier })}
        </p>
      </div>

      <form onSubmit={step === "identifier" ? handleSendOtp : handleVerify} className="space-y-4">
        {step === "identifier" ? (
          <div className="space-y-2">
            <input
              type="text"
              placeholder={t("placeholder")}
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              className="w-full px-6 py-4 rounded-full bg-white/5 border border-white/10 text-white placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-brand-primary/50 transition-all"
              required
            />
          </div>
        ) : (
          <div className="space-y-2">
            <input
              type="text"
              placeholder={t("otpPlaceholder")}
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
              className="w-full px-6 py-4 rounded-full bg-white/5 border border-white/10 text-white placeholder:text-zinc-500 text-center tracking-[1em] text-xl font-bold focus:outline-none focus:ring-2 focus:ring-brand-primary/50 transition-all"
              maxLength={6}
              required
            />
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full py-4 rounded-full bg-white text-black font-bold hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50"
        >
          {loading ? t("processing") : step === "identifier" ? t("continue") : t("confirm")}
        </button>

        {step === "otp" && (
          <button
            type="button"
            onClick={() => setStep("identifier")}
            className="w-full text-sm text-zinc-400 hover:text-white transition-colors"
          >
            {t("changeIdentifier")}
          </button>
        )}
      </form>
    </div>
  );
}
