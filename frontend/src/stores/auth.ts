import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { authApi } from '@/services/api';
import type { User, UserRole } from '@/types';

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('aicte_token'));
  const storedUser = localStorage.getItem('aicte_user');
  const user = ref<User | null>(storedUser ? JSON.parse(storedUser) : null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  const isAuthenticated = computed(() => !!token.value && !!user.value);
  const role = computed<UserRole | null>(() => user.value?.role || null);
  const isInstitute = computed(() => user.value?.role === 'institute');
  const isAdmin = computed(() => user.value?.role === 'admin');
  const isSuperAdmin = computed(() => user.value?.role === 'super_admin');
  const institutionName = computed(() => user.value?.institution_name || 'All Affiliated Institutions');
  const institutionCode = computed(() => user.value?.institution_code || 'AICTE-CENTRAL');

  async function login(username: string, password: string) {
    isLoading.value = true;
    error.value = null;
    try {
      const res = await authApi.login({ username, password });
      token.value = res.data.token;
      user.value = res.data.user;
      localStorage.setItem('aicte_token', res.data.token);
      localStorage.setItem('aicte_user', JSON.stringify(res.data.user));
      return { success: true };
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Login failed. Please verify credentials.';
      return { success: false, message: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  async function switchDemoRole(targetRole: UserRole) {
    isLoading.value = true;
    try {
      const res = await authApi.switchDemoRole(targetRole);
      token.value = res.data.token;
      user.value = res.data.user;
      localStorage.setItem('aicte_token', res.data.token);
      localStorage.setItem('aicte_user', JSON.stringify(res.data.user));
      return { success: true, message: res.data.message };
    } catch (err: any) {
      return { success: false, message: err.response?.data?.message || 'Failed to switch role' };
    } finally {
      isLoading.value = false;
    }
  }

  async function updateProfile(data: { full_name: string; email: string; phone?: string }) {
    isLoading.value = true;
    error.value = null;
    try {
      const res = await authApi.updateProfile(data);
      user.value = res.data.user;
      localStorage.setItem('aicte_user', JSON.stringify(res.data.user));
      return { success: true, message: res.data.message };
    } catch (err: any) {
      const msg = err.response?.data?.message || 'Failed to update profile';
      error.value = msg;
      return { success: false, message: msg };
    } finally {
      isLoading.value = false;
    }
  }

  async function changePassword(data: { current_password: string; new_password: string }) {
    isLoading.value = true;
    error.value = null;
    try {
      const res = await authApi.changePassword(data);
      return { success: true, message: res.data.message };
    } catch (err: any) {
      const msg = err.response?.data?.message || 'Failed to change password';
      error.value = msg;
      return { success: false, message: msg };
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchMe() {
    if (!token.value) return;
    try {
      const res = await authApi.getMe();
      user.value = res.data.user;
      localStorage.setItem('aicte_user', JSON.stringify(res.data.user));
    } catch (err) {
      logout();
    }
  }

  function logout() {
    token.value = null;
    user.value = null;
    localStorage.removeItem('aicte_token');
    localStorage.removeItem('aicte_user');
  }

  return {
    token,
    user,
    isLoading,
    error,
    isAuthenticated,
    role,
    isInstitute,
    isAdmin,
    isSuperAdmin,
    institutionName,
    institutionCode,
    login,
    switchDemoRole,
    updateProfile,
    changePassword,
    fetchMe,
    logout,
  };
});
