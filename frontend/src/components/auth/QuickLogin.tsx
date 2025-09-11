import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import axios from 'axios';

export const QuickLogin: React.FC = () => {
  const navigate = useNavigate();
  const { setUser, setToken } = useAuthStore();
  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const quickLogin = async (username: string, password: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await axios.post('http://localhost:8000/api/v1/auth/login/', {
        username,
        password
      });
      
      if (response.data.token) {
        const user = {
          id: response.data.user.id || String(Math.random()),
          username: response.data.user.username,
          email: response.data.user.email,
          credits: response.data.user.credits || 1000,
          subscription: response.data.user.subscription || 'premium'
        };
        
        setUser(user);
        setToken(response.data.token);
        
        // Clear any existing invalid tokens
        localStorage.removeItem('auth-storage');
        localStorage.setItem('authToken', response.data.token);
        
        navigate('/dashboard');
      }
    } catch (err: any) {
      console.error('Quick login error:', err);
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="mt-4 space-y-2">
      <p className="text-sm text-gray-600 dark:text-gray-400">Quick Login:</p>
      
      <div className="flex gap-2">
        <button
          onClick={() => quickLogin('testuser', 'testpass123')}
          disabled={isLoading}
          className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
        >
          Test User
        </button>
        
        <button
          onClick={() => quickLogin('demo', 'demo123')}
          disabled={isLoading}
          className="px-3 py-1 text-sm bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
        >
          Demo User
        </button>
        
        <button
          onClick={() => quickLogin('admin', 'admin123')}
          disabled={isLoading}
          className="px-3 py-1 text-sm bg-purple-500 text-white rounded hover:bg-purple-600 disabled:opacity-50"
        >
          Admin
        </button>
      </div>
      
      {error && (
        <p className="text-sm text-red-500">{error}</p>
      )}
      
      {isLoading && (
        <p className="text-sm text-gray-500">Logging in...</p>
      )}
    </div>
  );
};