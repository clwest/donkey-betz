import { useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

interface AuthGuardProps {
  children: React.ReactNode;
}

export const AuthGuard: React.FC<AuthGuardProps> = ({ children }) => {
  const { isAuthenticated, user, initAuth } = useAuthStore();
  const location = useLocation();

  useEffect(() => {
    console.log('🔐 AuthGuard: Initializing auth on mount');
    // Initialize auth on mount
    initAuth();
  }, [initAuth]);

  console.log('🔐 AuthGuard: Checking auth', { 
    isAuthenticated, 
    hasUser: !!user, 
    currentPath: location.pathname 
  });

  // If not authenticated and not on login page, redirect to login
  if (!isAuthenticated || !user) {
    console.log('🔐 AuthGuard: Not authenticated, redirecting to /login');
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  console.log('🔐 AuthGuard: User authenticated, rendering protected content');
  return <>{children}</>;
};