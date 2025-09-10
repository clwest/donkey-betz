import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { SparklesIcon, ArrowLeftIcon } from '@heroicons/react/24/outline';
import axios from 'axios';

const ForgotPasswordPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resetInfo, setResetInfo] = useState<{ uid: string; token: string } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email) {
      setError('Please enter your email address');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    setSuccess(false);
    
    try {
      const response = await axios.post('http://localhost:8000/api/auth/forgot-password/', {
        email
      });
      
      setSuccess(true);
      
      // In dev mode, we get the reset info directly
      if (response.data.uid && response.data.token) {
        setResetInfo({
          uid: response.data.uid,
          token: response.data.token
        });
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to send reset email. Please try again.');
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
          Reset your password
        </h2>
        <p className="mt-2 text-center text-sm text-gray-400">
          We'll send you an email with instructions to reset your password.
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white/10 backdrop-blur-md py-8 px-4 shadow-2xl sm:rounded-lg sm:px-10 border border-white/20">
          {!success ? (
            <form className="space-y-6" onSubmit={handleSubmit}>
              {error && (
                <div className="bg-red-500/20 border border-red-500 rounded-md p-3">
                  <p className="text-sm text-red-200">{error}</p>
                </div>
              )}
              
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-200">
                  Email Address
                </label>
                <div className="mt-1">
                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="appearance-none block w-full px-3 py-2 border border-gray-600 rounded-md placeholder-gray-400 bg-gray-800/50 text-white focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm"
                    placeholder="Enter your email address"
                  />
                </div>
              </div>
              
              <div>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:opacity-50"
                >
                  {isLoading ? 'Sending...' : 'Send reset link'}
                </button>
              </div>
              
              <div className="flex items-center justify-center">
                <Link
                  to="/login"
                  className="flex items-center text-sm text-purple-400 hover:text-purple-300"
                >
                  <ArrowLeftIcon className="h-4 w-4 mr-1" />
                  Back to sign in
                </Link>
              </div>
            </form>
          ) : (
            <div className="text-center">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-500/20 mb-4">
                <svg className="h-6 w-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              
              <h3 className="text-lg font-medium text-gray-200 mb-2">Check your email</h3>
              <p className="text-sm text-gray-400 mb-6">
                We've sent password reset instructions to {email}
              </p>
              
              {resetInfo && (
                <div className="mt-4 p-4 bg-gray-800/50 rounded-lg border border-gray-700">
                  <p className="text-xs text-gray-400 mb-2">Development mode - Reset info:</p>
                  <div className="text-xs text-gray-300 text-left font-mono">
                    <p>UID: {resetInfo.uid}</p>
                    <p className="break-all">Token: {resetInfo.token}</p>
                  </div>
                  <Link
                    to={`/reset-password?uid=${resetInfo.uid}&token=${resetInfo.token}`}
                    className="mt-3 inline-flex items-center text-sm text-purple-400 hover:text-purple-300"
                  >
                    Go to reset page →
                  </Link>
                </div>
              )}
              
              <div className="mt-6">
                <p className="text-sm text-gray-400 mb-3">
                  Didn't receive the email? Check your spam folder or
                </p>
                <button
                  onClick={() => {
                    setSuccess(false);
                    setResetInfo(null);
                  }}
                  className="text-purple-400 hover:text-purple-300 font-medium"
                >
                  Try again
                </button>
              </div>
              
              <div className="mt-6">
                <Link
                  to="/login"
                  className="flex items-center justify-center text-sm text-purple-400 hover:text-purple-300"
                >
                  <ArrowLeftIcon className="h-4 w-4 mr-1" />
                  Back to sign in
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ForgotPasswordPage;