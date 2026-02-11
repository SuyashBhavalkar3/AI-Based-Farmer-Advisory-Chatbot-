import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { authAPI, AuthResponse } from "@/services/api";
import { useToast } from "@/hooks/use-toast";

interface User {
  id: number;
  email: string;
  full_name: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  signUp: (email: string, password: string, fullName: string) => Promise<void>;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  // Check if user is already authenticated on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem("access_token");
        if (token) {
          const userData = await authAPI.getCurrentUser();
          setUser(userData.user || userData);
        }
      } catch (error) {
        console.error("Auth check failed:", error);
        localStorage.removeItem("access_token");
        localStorage.removeItem("user");
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const signUp = async (email: string, password: string, fullName: string) => {
    try {
      const response = await authAPI.signup(email, password, fullName);
      const newUser: User = {
        id: response.user.id,
        email: response.user.email,
        full_name: response.user.full_name
      };
      localStorage.setItem("access_token", response.access_token);
      localStorage.setItem("user", JSON.stringify(newUser));
      setUser(newUser);
      
      toast({
        title: "Success",
        description: "Account created successfully!",
      });
    } catch (error: any) {
      const errorMessage = error?.message || "Signup failed";
      toast({
        title: "Signup Error",
        description: errorMessage,
        variant: "destructive",
      });
      throw error;
    }
  };

  const signIn = async (email: string, password: string) => {
    try {
      const response: AuthResponse = await authAPI.login(email, password);
      
      const loginUser: User = {
        id: response.user.id,
        email: response.user.email,
        full_name: response.user.full_name
      };
      localStorage.setItem("access_token", response.access_token);
      localStorage.setItem("user", JSON.stringify(loginUser));
      setUser(loginUser);
      
      toast({
        title: "Success",
        description: "Logged in successfully",
      });
    } catch (error: any) {
      const errorMessage = error?.message || "Login failed";
      toast({
        title: "Login Error",
        description: errorMessage,
        variant: "destructive",
      });
      throw error;
    }
  };

  const signOut = async () => {
    setUser(null);
  };

  const isAuthenticated = !!user;

  return (
    <AuthContext.Provider 
      value={{ user, loading, isAuthenticated, signUp, signIn, signOut }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
}
