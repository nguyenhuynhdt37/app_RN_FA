export type UserRole = 
  | 'admin' 
  | 'teacher' 
  | 'moderator' 
  | 'support' 
  | 'finance' 
  | 'partner' 
  | 'affiliate' 
  | 'student';

export interface User {
  id: string;
  email: string;
  fullName: string;
  role: UserRole;
  avatarUrl?: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
