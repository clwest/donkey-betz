import { apiClient } from './apiClient';
import { storage, STORAGE_KEYS } from './apiConfig';
import { LoginRequest, LoginResponse, RegisterRequest, User } from '../types/api';

class AuthService {
  // Login
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post<any>('/auth/login/', credentials);
    
    // Handle the actual API response format: {user_id, username, token}
    // and convert it to the expected format: {token, user}
    const loginResponse: LoginResponse = {
      token: response.token,
      user: {
        id: response.user_id,
        username: response.username,
        email: '', // Will be filled when we fetch profile
        first_name: '',
        last_name: '',
        is_premium: false,
        date_joined: new Date().toISOString(),
      }
    };
    
    // Store auth data
    await apiClient.setAuthToken(loginResponse.token);
    await storage.setObject(STORAGE_KEYS.USER, loginResponse.user);
    
    // Fetch full profile data after login
    try {
      const profile = await apiClient.get('/profile/');
      if (profile.user) {
        const fullUser = profile.user;
        await storage.setObject(STORAGE_KEYS.USER, fullUser);
        loginResponse.user = fullUser;
      }
    } catch (error) {
      console.warn('Could not fetch full profile after login:', error);
    }
    
    return loginResponse;
  }

  // Register
  async register(userData: RegisterRequest): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/auth/register/', userData);
    
    // Store auth data
    await apiClient.setAuthToken(response.token);
    await storage.setObject(STORAGE_KEYS.USER, response.user);
    
    return response;
  }

  // Logout
  async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout/', {});
    } catch (error) {
      // Even if the server request fails, clear local auth
      console.warn('Logout request failed, but clearing local auth:', error);
    }
    
    await apiClient.clearAuth();
  }

  // Get current user from storage
  async getCurrentUser(): Promise<User | null> {
    return await storage.getObject<User>(STORAGE_KEYS.USER);
  }

  // Check if user is authenticated
  async isAuthenticated(): Promise<boolean> {
    const token = await storage.getItem(STORAGE_KEYS.AUTH_TOKEN);
    return !!token;
  }

  // Change password
  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await apiClient.post('/auth/change-password/', {
      current_password: currentPassword,
      new_password: newPassword,
    });
  }

  // Update profile
  async updateProfile(userData: Partial<User>): Promise<User> {
    const response = await apiClient.patch<User>('/profile/update/', userData);
    
    // Update stored user data
    await storage.setObject(STORAGE_KEYS.USER, response);
    
    return response;
  }

  // Upload avatar
  async uploadAvatar(imageFile: any): Promise<User> {
    const response = await apiClient.uploadFile<User>(
      '/profile/avatar/',
      imageFile,
      'avatar'
    );
    
    // Update stored user data
    await storage.setObject(STORAGE_KEYS.USER, response);
    
    return response;
  }

  // Delete avatar
  async deleteAvatar(): Promise<User> {
    const response = await apiClient.delete<User>('/profile/avatar/delete/');
    
    // Update stored user data
    await storage.setObject(STORAGE_KEYS.USER, response);
    
    return response;
  }

  // Get user stats
  async getUserStats(): Promise<any> {
    return await apiClient.get('/profile/stats/');
  }

  // Check auth status and refresh if needed
  async checkAuthStatus(): Promise<boolean> {
    try {
      const profile = await apiClient.get('/profile/');
      await storage.setObject(STORAGE_KEYS.USER, profile);
      return true;
    } catch (error) {
      // If profile request fails, user is not authenticated
      await apiClient.clearAuth();
      return false;
    }
  }
}

export const authService = new AuthService();
export default authService;