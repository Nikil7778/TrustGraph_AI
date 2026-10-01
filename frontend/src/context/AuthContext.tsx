import React, { createContext, useContext, useState, useEffect } from 'react';
import { loginUser, registerUser, fetchCurrentUser, fetchTestAccounts } from '../services/api';

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  role: string;
}

interface AuthContextType {
  user: UserProfile | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  testAccounts: UserProfile[];
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  switchUser: (email: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('trust_ai_token'));
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [testAccounts, setTestAccounts] = useState<UserProfile[]>([]);

  const loadProfile = async () => {
    try {
      const data = await fetchCurrentUser();
      setUser(data);
    } catch (err) {
      console.warn('Failed to load user profile with current token, clearing:', err);
      logout();
    }
  };

  const loadAccounts = async () => {
    try {
      const accounts = await fetchTestAccounts();
      setTestAccounts(accounts);
    } catch (err) {
      console.warn('Could not load test accounts list:', err);
    }
  };

  useEffect(() => {
    const initAuth = async () => {
      setIsLoading(true);
      await loadAccounts();

      const existingToken = localStorage.getItem('trust_ai_token');
      if (existingToken) {
        setToken(existingToken);
        await loadProfile();
      } else {
        // Auto-login as User A for seamless prototype experience
        try {
          const res = await loginUser('userA@example.com', 'password123');
          localStorage.setItem('trust_ai_token', res.token);
          setToken(res.token);
          setUser(res.user);
        } catch (e) {
          console.warn('Auto-login as User A failed:', e);
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const res = await loginUser(email, password);
      localStorage.setItem('trust_ai_token', res.token);
      setToken(res.token);
      setUser(res.user);
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (name: string, email: string, password: string) => {
    setIsLoading(true);
    try {
      const res = await registerUser(name, email, password);
      localStorage.setItem('trust_ai_token', res.token);
      setToken(res.token);
      setUser(res.user);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('trust_ai_token');
    setToken(null);
    setUser(null);
  };

  const switchUser = async (email: string) => {
    setIsLoading(true);
    const password = email.includes('admin') ? 'admin123' : 'password123';
    try {
      await login(email, password);
    } catch (err) {
      console.error(`Error switching to user ${email}:`, err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token && !!user,
        isLoading,
        testAccounts,
        login,
        register,
        logout,
        switchUser
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};
