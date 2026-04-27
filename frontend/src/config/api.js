// API Configuration - Uses environment variables for deployment flexibility
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export const API_ENDPOINTS = {
  BASE_URL: API_BASE_URL,
  AUTH: {
    LOGIN: `${API_BASE_URL}/api/auth/login`,
    REGISTER: `${API_BASE_URL}/api/auth/register`,
    LOGOUT: `${API_BASE_URL}/api/auth/logout`,
    ME: `${API_BASE_URL}/api/auth/me`,
  },
  ADMIN: {
    DASHBOARD: `${API_BASE_URL}/api/admin/dashboard`,
    STUDENTS: `${API_BASE_URL}/api/admin/students`,
    EXAMS: `${API_BASE_URL}/api/admin/exams`,
    RESULTS: `${API_BASE_URL}/api/admin/results`,
    SHARE_LINK: `${API_BASE_URL}/api/admin/generate-share-link`,
  },
  STUDENT: {
    DASHBOARD: `${API_BASE_URL}/api/student/dashboard`,
    EXAMS: `${API_BASE_URL}/api/student/exams`,
    SUBMIT: `${API_BASE_URL}/api/student/submit`,
    RESULTS: `${API_BASE_URL}/api/student/results`,
  },
  SHARE: {
    JOIN: `${API_BASE_URL}/join`,
  }
};

export default API_ENDPOINTS;
