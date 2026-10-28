import axios from 'axios';
import type {
  User,
  Institution,
  Student,
  UploadBatch,
  DuplicateReviewCase,
  Notification,
  AuditLog,
  Programme
} from '@/types';

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to attach JWT token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('aicte_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to handle session expiration cleanly
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && !window.location.pathname.includes('/login')) {
      localStorage.removeItem('aicte_token');
      localStorage.removeItem('aicte_user');
      window.location.href = '/login?expired=1';
    }
    return Promise.reject(error);
  }
);

export default api;

// Auth API
export const authApi = {
  login: (credentials: { username: string; password: string }) =>
    api.post<{ token: string; user: User }>('/auth/login', credentials),
  getMe: () => api.get<{ user: User }>('/auth/me'),
  updateProfile: (data: { full_name: string; email: string; phone?: string }) =>
    api.put<{ user: User; message: string }>('/auth/profile', data),
  changePassword: (data: { current_password: string; new_password: string }) =>
    api.post<{ message: string }>('/auth/change-password', data),
  switchDemoRole: (role: 'institute' | 'admin' | 'super_admin') =>
    api.post<{ token: string; user: User; message: string }>('/auth/switch-demo-role', { role }),
};

// Institutions API
export const institutionsApi = {
  list: (params?: any) => api.get<{ institutions: Institution[]; total: number; page: number; pages: number }>('/institutions', { params }),
  getMy: () => api.get<{ institution: Institution }>('/institutions/my'),
  getById: (id: number) => api.get<{ institution: Institution }>(`/institutions/${id}`),
  create: (data: Partial<Institution>) => api.post<{ institution: Institution; message: string }>('/institutions', data),
  update: (id: number, data: Partial<Institution>) => api.put<{ institution: Institution; message: string }>(`/institutions/${id}`, data),
};

// Students API
export const studentsApi = {
  list: (params?: any) => api.get<{ students: Student[]; total: number; page: number; pages: number }>('/students', { params }),
  getById: (id: number) => api.get<{ student: Student }>(`/students/${id}`),
  create: (data: any) => api.post<{ student: Student; message: string }>('/students', data),
  update: (id: number, data: any) => api.put<{ student: Student; message: string }>(`/students/${id}`, data),
  exportCsv: (params?: any) =>
    api.get('/students/export', { params, responseType: 'blob' }),
};

// Uploads API
export const uploadsApi = {
  downloadTemplate: () => api.get('/uploads/template', { responseType: 'blob' }),
  previewCsv: (formData: FormData) =>
    api.post<any>('/uploads/preview', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  commitCsv: (data: { file_name: string; file_size_bytes: number; row_results: any[]; institution_id?: number }) =>
    api.post<any>('/uploads/commit', data),
  listBatches: (params?: any) => api.get<{ batches: UploadBatch[] }>('/uploads/batches', { params }),
  getBatch: (id: number) => api.get<{ batch: UploadBatch }>(`/uploads/batches/${id}`),
  downloadErrorReport: (id: number) =>
    api.get(`/uploads/batches/${id}/error-report`, { responseType: 'blob' }),
};

// Verification API
export const verificationApi = {
  getQueue: (params?: any) => api.get<{ queue: Student[] }>('/verification/queue', { params }),
  verifySingle: (studentId: number) => api.post<any>(`/verification/verify/${studentId}`),
  manualOverride: (data: { student_id: number; status: string; notes: string }) =>
    api.post<any>('/verification/manual-override', data),
  batchVerify: () => api.post<any>('/verification/batch-verify'),
};

// Duplicate Review API
export const duplicateApi = {
  list: (params?: any) => api.get<{ cases: DuplicateReviewCase[]; total: number }>('/duplicate-cases', { params }),
  getById: (id: number) => api.get<{ case: DuplicateReviewCase }>(`/duplicate-cases/${id}`),
  resolve: (id: number, data: { decision: string; notes: string }) =>
    api.post<{ case: DuplicateReviewCase; message: string }>(`/duplicate-cases/${id}/resolve`, data),
};

// Dashboard API
export const dashboardApi = {
  getMetrics: () => api.get<any>('/dashboard/metrics'),
};

// Enrolments & Intake Monitoring API
export const enrolmentsApi = {
  getMonitoring: (params?: any) => api.get<{ programmes: Programme[]; summary: any }>('/enrolments/monitoring', { params }),
  configureIntake: (data: any) => api.post<any>('/enrolments/programmes', data),
};

// Reports API
export const reportsApi = {
  getSummary: (params?: any) => api.get<any>('/reports/summary', { params }),
  exportCsv: (reportType: string, params?: any) =>
    api.get(`/reports/export/${reportType}`, { params, responseType: 'blob' }),
};

// Notifications API
export const notificationsApi = {
  list: () => api.get<{ notifications: Notification[]; unread_count: number }>('/notifications'),
  markAsRead: (id: number) => api.post(`/notifications/${id}/read`),
  markAllAsRead: () => api.post('/notifications/read-all'),
};

// User Management API
export const usersApi = {
  list: (params?: any) => api.get<{ users: User[]; total: number }>('/users', { params }),
  create: (data: any) => api.post<{ user: User; message: string }>('/users', data),
  toggleStatus: (id: number, is_active: boolean) => api.put<{ user: User; message: string }>(`/users/${id}/status`, { is_active }),
};

// Audit Logs API
export const auditLogsApi = {
  list: (params?: any) => api.get<{
    logs: AuditLog[];
    total: number;
    page: number;
    pages: number;
    available_actions?: string[];
    available_targets?: string[];
  }>('/audit-logs', { params }),
};

// System Settings API
export const settingsApi = {
  get: () => api.get<{ settings: any }>('/settings'),
  update: (data: any) => api.put<{ settings: any; message: string }>('/settings', data),
};
