import { useState, useEffect, createContext, useContext, ReactNode } from 'react';
import { User } from '@/types';
import { getUser, isAuthenticated, refreshUserData, clearTokens, clearUser } from '@/lib/auth';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isLoggedIn: boolean;
  login: (user: User) => void;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        if (isAuthenticated()) {
          const userData = await refreshUserData();
          setUser(userData);
        } else {
          const storedUser = getUser();
          if (storedUser && !isAuthenticated()) {
            // User data exists but no valid token, clear everything
            clearUser();
            clearTokens();
          } else {
            setUser(storedUser);
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        clearUser();
        clearTokens();
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const login = (userData: User) => {
    setUser(userData);
  };

  const logout = () => {
    setUser(null);
    clearTokens();
    clearUser();
    window.location.href = '/login';
  };

  const refreshUser = async () => {
    try {
      const userData = await refreshUserData();
      setUser(userData);
    } catch (error) {
      console.error('Error refreshing user:', error);
      logout();
    }
  };

  const value = {
    user,
    isLoading,
    isLoggedIn: !!user && isAuthenticated(),
    login,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthProvider;