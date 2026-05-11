const API_URL = process.env.NEXT_PUBLIC_API_URL;

export async function apiFetch(endpoint: string, options: RequestInit = {}) {
  const url = `${API_URL}${endpoint}`;
  
  // Mặc định luôn gửi kèm credentials (cookies)
  const defaultOptions: RequestInit = {
    ...options,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  };

  const response = await fetch(url, defaultOptions);

  if (response.status === 401) {
    // Xử lý khi token hết hạn (ví dụ: logout hoặc refresh)
    // Lưu ý: Refresh token cũng được backend tự động xử lý qua cookie nếu mình gọi endpoint refresh
  }

  return response;
}
