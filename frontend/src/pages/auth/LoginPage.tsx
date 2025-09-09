import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { SparklesIcon } from '@heroicons/react/24/outline';

const LoginPage: React.FC = () => {
  console.log('🔐 LoginPage: Component rendering');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { setUser, setToken } = useAuthStore();
  
  console.log('🔐 LoginPage: Auth store hooks loaded', { setUser: !!setUser, setToken: !!setToken });

  // Demo users for quick access with their actual tokens
  const demoUsers = [
    { 
      username: 'chris', 
      email: 'chris@donkeybetz.com', 
      name: 'Chris King',
      token: 'e7d2ae96885384ad8c66cfcd094f4f193629f227'
    },
    { 
      username: 'testuser', 
      email: 'test@example.com', 
      name: 'Test User',
      token: 'cff3e8441c4e2490e970de2f921f0064e7cc88a7'
    },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('🔐 LoginPage: handleSubmit called with username:', username);
    setIsLoading(true);

    // Simulate login - in a real app, this would call your auth API
    setTimeout(() => {
      // Find the demo user or create a generic one
      const demoUser = demoUsers.find(u => u.username === username);
      console.log('🔐 LoginPage: Found demo user:', demoUser);
      
      if (demoUser) {
        // Use the actual demo user with correct token
        const user = {
          id: String(Math.random()),
          username: demoUser.username,
          email: demoUser.email,
          credits: 1000,
          subscription: 'premium'
        };
        console.log('🔐 LoginPage: Setting user:', user);
        console.log('🔐 LoginPage: Setting token:', demoUser.token);
        setUser(user);
        setToken(demoUser.token);
      } else {
        // Unknown user - use testuser token as fallback
        const user = {
          id: String(Math.random()),
          username,
          email: `${username}@example.com`,
          credits: 1000,
          subscription: 'premium'
        };
        console.log('🔐 LoginPage: Creating generic user:', user);
        console.log('🔐 LoginPage: Using fallback token');
        setUser(user);
        setToken('cff3e8441c4e2490e970de2f921f0064e7cc88a7');
      }

      // Navigate to dashboard
      console.log('🔐 LoginPage: Navigating to /dashboard');
      navigate('/dashboard');
      setIsLoading(false);
    }, 500);
  };

  const handleDemoLogin = (user: typeof demoUsers[0]) => {
    console.log('🔐 LoginPage: handleDemoLogin called for user:', user.username);
    const newUser = {
      id: String(Math.random()),
      username: user.username,
      email: user.email,
      credits: 1000,
      subscription: 'premium'
    };
    console.log('🔐 LoginPage: Setting demo user:', newUser);
    console.log('🔐 LoginPage: Setting demo token:', user.token);
    setUser(newUser);
    // Use the correct token for each user
    setToken(user.token);
    console.log('🔐 LoginPage: Navigating to /dashboard from demo login');
    navigate('/dashboard');
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
              {demoUsers.map((user) => (
                <button
                  key={user.username}
                  onClick={() => handleDemoLogin(user)}
                  className="w-full flex justify-center py-2 px-4 border border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-200 bg-gray-800/30 hover:bg-gray-700/50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
                >
                  Sign in as {user.name} ({user.username})
                </button>
              ))}
            </div>
          </div>

          <div className="mt-6 text-center">
            <p className="text-xs text-gray-400">
              This is a demo login. In production, this would connect to your authentication system.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;