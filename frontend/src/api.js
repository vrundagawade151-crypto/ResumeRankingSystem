import axios from 'axios';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      localStorage.removeItem('profile');
      localStorage.removeItem('role');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

// Auth
export const sendOTP = (email, role, extra = {}) =>
  api.post('/auth/send-otp', { email, role, ...extra });
export const verifyOTP = (email, otp, role) =>
  api.post('/auth/verify-otp', { email, otp, role });
export const loginDirect = (email, password, role) =>
  api.post('/auth/login', { email, password, role });
export const uploadCandidateResume = (formData) =>
  api.post('/auth/profile/resume', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

// Jobs
export const getJobs = () => api.get('/jobs');
export const getRecruiterJobs = () => api.get('/jobs/recruiter');
export const getJob = (id) => api.get(`/jobs/${id}`);
export const createJob = (data) => api.post('/jobs', data);
export const updateJob = (id, data) => api.put(`/jobs/${id}`, data);
export const deleteJob = (id) => api.delete(`/jobs/${id}`);

// Applications
export const applyForJob = (formData) =>
  api.post('/applications', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
export const getApplicants = (jobId) => api.get(`/applications/job/${jobId}`);
export const getMyApplications = () => api.get('/applications/candidate');

// Recruiter
export const getRecruiterProfile = () => api.get('/recruiter/profile');
export const updateRecruiterProfile = (data) => api.put('/recruiter/profile', data);

// Admin
export const getRecruiters = () => api.get('/admin/recruiters');
export const getCandidates = () => api.get('/admin/candidates');
export const getAdminJobs = () => api.get('/admin/jobs');
export const getStatistics = () => api.get('/admin/statistics');

// AI Screening
export const extractAndRankResumes = (jobId, limit, fileType) =>
  api.post('/ai-screening/extract', { job_id: jobId, limit: limit || 100, file_type: fileType || 'all' });
export const getRankedCandidates = (jobId) => api.get(`/ai-screening/ranked/${jobId}`);

export default api;
