import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// In-memory token management (as specified: no token in localStorage)
let inMemoryToken: string | null = sessionStorage.getItem('aicte_session_token');

export const setAuthToken = (token: string | null) => {
  inMemoryToken = token;
  if (token) {
    sessionStorage.setItem('aicte_session_token', token);
  } else {
    sessionStorage.removeItem('aicte_session_token');
  }
};

export const getAuthToken = () => inMemoryToken;

export const api = axios.create({
  baseURL: API_BASE_URL,
});

api.interceptors.request.use((config) => {
  if (inMemoryToken) {
    config.headers.Authorization = `Bearer ${inMemoryToken}`;
  }
  return config;
});

// API Services
export const authService = {
  login: async (username: string) => {
    const res = await api.post('/auth/token', { username, password: 'password123' });
    setAuthToken(res.data.access_token);
    return res.data;
  },
  getCurrentUser: async () => {
    const res = await api.get('/auth/me');
    return res.data;
  },
  logout: () => {
    setAuthToken(null);
  },
};

export const institutionsService = {
  list: async () => {
    const res = await api.get('/institutions');
    return res.data;
  },
  getProgrammes: async (institutionId: string) => {
    const res = await api.get(`/institutions/${institutionId}/programmes`);
    return res.data;
  },
};

export const studentsService = {
  list: async (params?: { academic_year?: string; status?: string; search?: string }) => {
    const res = await api.get('/students', { params });
    return res.data;
  },
  get: async (id: string) => {
    const res = await api.get(`/students/${id}`);
    return res.data;
  },
  patch: async (id: string, data: { name?: string; seat_category?: string; status?: string }) => {
    const res = await api.patch(`/students/${id}`, data);
    return res.data;
  },
};

export const uploadsService = {
  uploadFile: async (file: File, academicYear: string, institutionId?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('academic_year', academicYear);
    if (institutionId) {
      formData.append('institution_id', institutionId);
    }
    const res = await api.post('/uploads', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },
  getBatch: async (batchId: string) => {
    const res = await api.get(`/uploads/${batchId}`);
    return res.data;
  },
  getResults: async (batchId: string) => {
    const res = await api.get(`/uploads/${batchId}/results`);
    return res.data;
  },
};

export const validationService = {
  listCases: async (params?: { status?: string; rule_code?: string; severity?: string }) => {
    const res = await api.get('/validation-cases', { params });
    return res.data;
  },
  resolveCase: async (id: string, resolution_note: string, action: 'resolve' | 'dismiss' = 'resolve') => {
    const res = await api.post(`/validation-cases/${id}/resolve`, { resolution_note, action });
    return res.data;
  },
};

export const analyticsService = {
  getNational: async () => {
    const res = await api.get('/analytics/national');
    return res.data;
  },
  getInstitution: async (institutionId?: string) => {
    const res = await api.get('/analytics/institution', { params: { institution_id: institutionId } });
    return res.data;
  },
  downloadEnrolmentReport: async (academicYear?: string) => {
    const res = await api.get('/reports/enrolment', {
      params: { academic_year: academicYear },
      responseType: 'blob',
    });
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `aicte_enrolment_${academicYear || 'all'}.xlsx`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  },
};

export const verificationService = {
  createRequest: async (admissionId: string) => {
    const res = await api.post('/verification-requests', { admission_id: admissionId });
    return res.data;
  },
  publicVerify: async (ref: string) => {
    const res = await api.get(`/credentials/${ref}/verify`);
    return res.data;
  },
  getAuditLogs: async () => {
    const res = await api.get('/audit-logs');
    return res.data;
  },
};
