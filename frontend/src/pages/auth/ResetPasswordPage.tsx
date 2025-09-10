import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { SparklesIcon, EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline';
import axios from 'axios';

const ResetPasswordPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { setUser, setToken } = useAuthStore();
  
  const [formData, setFormData] = useState({
    new_password: '',
    confirm_password: ''
  });
  
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [success, setSuccess] = useState(false);
  
  const uid = searchParams.get('uid');
  const token = searchParams.get('token');
  
  useEffect(() => {
    if (!uid || !token) {
      setErrors({ general: 'Invalid reset link. Please request a new password reset.' });
    }
  }, [uid, token]);
  
  const validatePassword = (password: string) => {
    if (password.length < 8) {
      return 'Password must be at least 8 characters';
    }
    if (!/\d/.test(password)) {
      return 'Password must contain at least one number';
    }
    if (!/[A-Z]/.test(password)) {
      return 'Password must contain at least one uppercase letter';
    }
    return null;
  };
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Real-time validation
    const newErrors = { ...errors };
    
    if (name === 'new_password') {
      const error = validatePassword(value);
      if (error) {
        newErrors.new_password = error;
      } else {
        delete newErrors.new_password;
      }
    }
    
    if (name === 'confirm_password' || (name === 'new_password' && formData.confirm_password)) {
      const confirmValue = name === 'confirm_password' ? value : formData.confirm_password;
      const newPasswordValue = name === 'new_password' ? value : formData.new_password;
      
      if (confirmValue !== newPasswordValue) {
        newErrors.confirm_password = 'Passwords do not match';
      } else {
        delete newErrors.confirm_password;
      }
    }
    
    setErrors(newErrors);
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!uid || !token) {
      setErrors({ general: 'Invalid reset link' });
      return;
    }
    
    // Validate password
    const passwordError = validatePassword(formData.new_password);
    if (passwordError) {
      setErrors({ new_password: passwordError });
      return;
    }
    
    if (formData.new_password !== formData.confirm_password) {
      setErrors({ confirm_password: 'Passwords do not match' });
      return;
    }
    
    setIsLoading(true);
    setErrors({});
    
    try {
      const response = await axios.post('http://localhost:8000/api/auth/reset-password/', {
        uid,
        token,
        new_password: formData.new_password,
        confirm_password: formData.confirm_password
      });
      
      if (response.data.token) {
        // Password reset successful, log them in
        setSuccess(true);
        setUser(response.data.user);
        setToken(response.data.token);
        
        // Store in localStorage
        localStorage.setItem('authToken', response.data.token);
        
        // Redirect to dashboard after a short delay
        setTimeout(() => {
          navigate('/dashboard');
        }, 2000);
      }
    } catch (err: any) {
      setErrors({ 
        general: err.response?.data?.error || 'Failed to reset password. Please try again.' 
      });
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
          Create new password
        </h2>
        <p className="mt-2 text-center text-sm text-gray-400">
          Enter your new password below
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white/10 backdrop-blur-md py-8 px-4 shadow-2xl sm:rounded-lg sm:px-10 border border-white/20">
          {success ? (
            <div className="text-center">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-500/20 mb-4">
                <svg className="h-6 w-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-200 mb-2">Password reset successful!</h3>
              <p className="text-sm text-gray-400">
                Redirecting you to the dashboard...
              </p>
            </div>
          ) : (
            <form className="space-y-6" onSubmit={handleSubmit}>
              {errors.general && (
                <div className="bg-red-500/20 border border-red-500 rounded-md p-3">
                  <p className="text-sm text-red-200">{errors.general}</p>
                </div>
              )}
              
              <div>
                <label htmlFor="new_password" className="block text-sm font-medium text-gray-200">
                  New Password
                </label>
                <div className="mt-1 relative">
                  <input
                    id="new_password"
                    name="new_password"
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={formData.new_password}
                    onChange={handleChange}
                    disabled={!uid || !token}
                    className={`appearance-none block w-full px-3 py-2 pr-10 border ${
                      errors.new_password ? 'border-red-500' : 'border-gray-600'
                    } rounded-md placeholder-gray-400 bg-gray-800/50 text-white focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm disabled:opacity-50`}
                    placeholder="Min 8 chars, 1 uppercase, 1 number"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  >
                    {showPassword ? (
                      <EyeSlashIcon className="h-5 w-5 text-gray-400" />
                    ) : (
                      <EyeIcon className="h-5 w-5 text-gray-400" />
                    )}
                  </button>
                </div>
                {errors.new_password && (
                  <p className="mt-1 text-sm text-red-400">{errors.new_password}</p>
                )}
              </div>
              
              <div>
                <label htmlFor="confirm_password" className="block text-sm font-medium text-gray-200">
                  Confirm New Password
                </label>
                <div className="mt-1 relative">
                  <input
                    id="confirm_password"
                    name="confirm_password"
                    type={showConfirmPassword ? 'text' : 'password'}
                    required
                    value={formData.confirm_password}
                    onChange={handleChange}
                    disabled={!uid || !token}
                    className={`appearance-none block w-full px-3 py-2 pr-10 border ${
                      errors.confirm_password ? 'border-red-500' : 'border-gray-600'
                    } rounded-md placeholder-gray-400 bg-gray-800/50 text-white focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm disabled:opacity-50`}
                    placeholder="Re-enter your new password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  >
                    {showConfirmPassword ? (
                      <EyeSlashIcon className="h-5 w-5 text-gray-400" />
                    ) : (
                      <EyeIcon className="h-5 w-5 text-gray-400" />
                    )}
                  </button>
                </div>
                {errors.confirm_password && (
                  <p className="mt-1 text-sm text-red-400">{errors.confirm_password}</p>
                )}
              </div>
              
              <div>
                <button
                  type="submit"
                  disabled={isLoading || !uid || !token || Object.keys(errors).length > 0}
                  className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? 'Resetting...' : 'Reset password'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default ResetPasswordPage;