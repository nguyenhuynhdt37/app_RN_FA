import { cookies } from "next/headers";
import { redirect } from "next/navigation";

export async function getRolesFromToken(): Promise<string[]> {
  const cookieStore = await cookies();
  const token = cookieStore.get("access_token")?.value;
  
  if (!token) return [];
  
  try {
    // Decode JWT payload (the second part of the token)
    const payloadBase64 = token.split(".")[1];
    // Base64Url decode
    const base64 = payloadBase64.replace(/-/g, "+").replace(/_/g, "/");
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split("")
        .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
        .join("")
    );
    const payload = JSON.parse(jsonPayload);
    return payload.roles || [];
  } catch (e) {
    return [];
  }
}

export async function requireAdminRole(locale: string = "vi") {
  const roles = await getRolesFromToken();
  
  // If user is not logged in or has no roles, redirect to login
  if (!roles.length) {
    redirect(`/${locale}/login`);
  }
  
  // Allow if user is admin, moderator, support, finance
  const allowedRoles = ["admin", "moderator", "support", "finance"];
  const hasAccess = roles.some(role => allowedRoles.includes(role));
  
  if (!hasAccess) {
    // If they are just a student or lecturer, they shouldn't access the admin panel
    // Redirect to home or an unauthorized page
    redirect(`/${locale}`);
  }
  
  return roles;
}
