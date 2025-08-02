import Cookies from 'js-cookie';
import { User } from '@/types';
import { authApi } from './api';

// Authentication functions
export const signIn = async (email: string, password: string) => {
  try {
    const response = await authApi.login(email, password);
    
    // Set tokens
    setToken(response.access_token);
    Cookies.set('refresh_token', response.refresh_token, { expires: 7 });
    setUser(response.user);
    
    return response;
  } catch (error: any) {
    console.error('Login error:', error);
    throw new Error(error.response?.data?.detail || 'Invalid email or password');
  }
};

export const signUp = async (userData: {
  email: string;
  username: string;
  full_name: string;
  password: string;
}) => {
  try {
    const response = await authApi.register(userData);
    return response;
  } catch (error: any) {
    console.error('Registration error:', error);
    throw new Error(error.response?.data?.detail || 'Registration failed');
  }
};

export const signOut = async () => {
  try {
    await authApi.logout();
  } catch (error) {
    console.error('Logout error:', error);
  } finally {
    clearTokens();
    clearUser();
  }
};

export const isAuthenticated = (): boolean => {
  return !!getToken();
};

export const getToken = (): string | null => {
  return Cookies.get('access_token') || null;
};

export const setToken = (token: string) => {
  Cookies.set('access_token', token, { expires: 1 });
};

export const clearTokens = () => {
  Cookies.remove('access_token');
  Cookies.remove('refresh_token');
};

export const getUser = (): User | null => {
  const userStr = localStorage.getItem('user');
  if (userStr) {
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  }
  return null;
};

export const setUser = (user: User) => {
  localStorage.setItem('user', JSON.stringify(user));
};

export const clearUser = () => {
  localStorage.removeItem('user');
};

export const refreshUserData = async (): Promise<User | null> => {
  try {
    const user = await authApi.getCurrentUser() as User;
    if (user) {
      setUser(user);
      return user;
    }
    return null;
  } catch (error) {
    console.error('Failed to refresh user data:', error);
    return null;
  }
};

// Permission checking functions
export const hasPermission = (user: User | null, permission: string): boolean => {
  if (!user) return false;
  
  // Check if user has the required permission
  if (user.roles && user.roles.length > 0) {
    return user.roles.some(role => {
      if (role.permissions) {
        return Object.values(role.permissions).some((perms: any) => 
          Array.isArray(perms) && perms.includes(permission)
        );
      }
      return false;
    });
  }
  
  return false;
};

export const hasRole = (user: User | null, role: string): boolean => {
  if (!user) return false;
  
  if (user.roles && user.roles.length > 0) {
    return user.roles.some(userRole => 
      userRole.name.toLowerCase() === role.toLowerCase()
    );
  }
  
  return false;
};

// Alias for compatibility
export const login = signIn;
