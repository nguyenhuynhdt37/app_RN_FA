"use server";

import { cookies } from "next/headers";

/**
 * Mock login action that sets a cookie with user roles.
 * In a real app, this would call the backend API and get a real JWT.
 */
import { apiFetch } from "@/lib/api";

export async function loginAction(email: string, password?: string) {
  const cookieStore = await cookies();
  
  const response = await apiFetch("/auth/login/password", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });

  const data = await response.json();

  if (!response.ok) {
    return { 
      success: false, 
      error: data.detail?.message || data.detail || "Đăng nhập thất bại" 
    };
  }
  
  // Backend set cookies (access_token, refresh_token) automatically via set_auth_cookies
  // But Server Action response headers are NOT automatically merged into the browser response
  // unless we manually set them here OR if the browser calls this via a Client Action.
  // Wait, in Next.js Server Actions, if the fetch call returns Set-Cookie headers, 
  // they are NOT automatically forwarded to the browser.
  // We need to manually extract them or rely on the backend being called from the client.
  
  // Actually, since this is a Server Action, we need to manually set the cookie in cookieStore
  // if we want it to be available in the next request.
  
  const setCookieHeader = response.headers.get("set-cookie");
  if (setCookieHeader) {
    // Basic parser for set-cookie header
    const cookies_to_set = setCookieHeader.split(/,(?=[^;]+=[^;]+)/);
    for (const c of cookies_to_set) {
      const [nameValue, ...opts] = c.split(";");
      const [name, value] = nameValue.split("=");
      
      const cookieOptions: any = {};
      opts.forEach(opt => {
        const [k, v] = opt.trim().split("=");
        const key = k.toLowerCase();
        if (key === "httponly") cookieOptions.httpOnly = true;
        if (key === "secure") cookieOptions.secure = true;
        if (key === "path") cookieOptions.path = v;
        if (key === "max-age") cookieOptions.maxAge = parseInt(v);
        if (key === "samesite") cookieOptions.sameSite = v.toLowerCase();
      });
      
      cookieStore.set(name.trim(), value.trim(), cookieOptions);
    }
  }

  // Get roles from the token (we can just return them from the backend)
  // For now, let's assume it succeeded if response.ok
  return { success: true };
}

export async function logoutAction() {
  const cookieStore = await cookies();
  cookieStore.delete("access_token");
  return { success: true };
}
