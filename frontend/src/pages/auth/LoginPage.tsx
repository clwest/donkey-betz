import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { SparklesIcon } from '@heroicons/react/24/outline';
import axios from 'axios';

const LoginPage: React.FC = () => {
  console.log('🔐 LoginPage: Component rendering');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { setUser, setToken } = useAuthStore();
  
  console.log('🔐 LoginPage: Auth store hooks loaded', { setUser: !!setUser, setToken: !!setToken });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('🔐 LoginPage: handleSubmit called with username:', username);
    setIsLoading(true);
    setError(null);

    try {
      // Call the actual Django auth API
      const response = await axios.post('http://localhost:8000/api/auth/login/', {
        username,
        password
      });

      console.log('🔐 LoginPage: Login response:', response.data);
      
      if (response.data.token) {
        // Set the user data from the response
        const user = {
          id: response.data.user.id || String(Math.random()),
          username: response.data.user.username,
          email: response.data.user.email,
          credits: response.data.user.credits || 1000,
          subscription: response.data.user.subscription || 'premium'
        };
        
        console.log('🔐 LoginPage: Setting user:', user);
        console.log('🔐 LoginPage: Setting token:', response.data.token);
        
        setUser(user);
        setToken(response.data.token);
        
        // Navigate to dashboard
        console.log('🔐 LoginPage: Navigating to /dashboard');
        navigate('/dashboard');
      } else {
        setError('Invalid response from server');
      }
    } catch (err: any) {
      console.error('🔐 LoginPage: Login error:', err);
      if (err.response?.status === 401) {
        setError('Invalid username or password');
      } else if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError('Failed to login. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickLogin = async (quickUsername: string, quickPassword: string) => {
    console.log('🔐 LoginPage: Quick login for user:', quickUsername);
    setUsername(quickUsername);
    setPassword(quickPassword);
    setIsLoading(true);
    setError(null);

    try {
      const response = await axios.post('http://localhost:8000/api/auth/login/', {
        username: quickUsername,
        password: quickPassword
      });

      console.log('🔐 LoginPage: Quick login response:', response.data);
      
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
        navigate('/dashboard');
      } else {
        setError('Invalid response from server');
      }
    } catch (err: any) {
      console.error('🔐 LoginPage: Quick login error:', err);
      setError('Quick login failed. Please enter credentials manually.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <div className="flex items-center space-x-2">
            <SparklesIcon className="h-12 w-12 text-purple-400" />
            <h2 className="text-3xl font-bold text-white">AI Content Studio</h2>
          </div>
        </div>
        <h2 className="mt-6 text-center text-2xl font-bold text-gray-300">
          Sign in to your account
        </h2>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white/10 backdrop-blur-md py-8 px-4 shadow-2xl sm:rounded-lg sm:px-10 border border-white/20">
          <form className="space-y-6" onSubmit={handleSubmit}>
            {error && (
              <div className="bg-red-500/20 border border-red-500 rounded-md p-3">
                <p className="text-sm text-red-200">{error}</p>
              </div>
            )}
            
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-200">
                Username
              </label>
              <div className="mt-1">
                <input
                  id="username"
                  name="username"
                  type="text"
                  autoComplete="username"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="appearance-none block w-full px-3 py-2 border border-gray-600 rounded-md placeholder-gray-400 bg-gray-800/50 text-white focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm"
                  placeholder="Enter your username"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-200">
                Password
              </label>
              <div className="mt-1">
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="appearance-none block w-full px-3 py-2 border border-gray-600 rounded-md placeholder-gray-400 bg-gray-800/50 text-white focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm"
                  placeholder="Enter your password"
                />
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:opacity-50"
              >
                {isLoading ? 'Signing in...' : 'Sign in'}
              </button>
            </div>
          </form>

          {/* Demo user buttons */}
          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-600" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-transparent text-gray-400">Quick access</span>
              </div>
            </div>

            <div className="mt-6 space-y-3">
              <button
                onClick={() => handleQuickLogin('admin', 'admin123')}
                disabled={isLoading}
                className="w-full flex justify-center py-2 px-4 border border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-200 bg-gray-800/30 hover:bg-gray-700/50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 disabled:opacity-50"
              >
                Sign in as Admin (admin/admin123)
              </button>
            </div>
          </div>

          <div className="mt-6 text-center">
            <p className="text-xs text-gray-400">
              Use admin/admin123 for quick access or create your own account.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;