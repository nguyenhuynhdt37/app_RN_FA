import { apiFetch } from "@/lib/api";

export const authService = {
  async sendOtp(identifier: string, purpose: "authenticate") {
    const res = await apiFetch("/auth/send-otp", {
      method: "POST",
      body: JSON.stringify({ [identifier.includes("@") ? "email" : "phone"]: identifier, purpose }),
    });
    return res.json();
  },

  async verifyOtp(identifier: string, otpCode: string, purpose: "authenticate") {
    const res = await apiFetch("/auth/verify-otp", {
      method: "POST",
      body: JSON.stringify({ 
        [identifier.includes("@") ? "email" : "phone"]: identifier, 
        otp_code: otpCode, 
        purpose 
      }),
    });
    return res.json();
  },

  async authenticate(otpToken: string) {
    const res = await apiFetch("/auth/authenticate", {
      method: "POST",
      body: JSON.stringify({ 
        otp_token: otpToken,
        device_type: "WEB",
        device_name: typeof window !== "undefined" ? window.navigator.userAgent : "Web Browser"
      }),
    });
    return res.json();
  },

  async getMe() {
    const res = await apiFetch("/auth/me");
    if (!res.ok) throw new Error("Unauthorized");
    return res.json();
  },

  async logout() {
    const res = await apiFetch("/auth/logout", { method: "POST", body: JSON.stringify({}) });
    return res.ok;
  }
};
