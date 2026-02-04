import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  ApiResponse,
  ErrorResponse,
  Nurse,
  Patient,
  Session,
  Transcript,
  Classification,
  Notification,
  ProcessingJob,
  DashboardStats,
  PaginationParams,
  PaginatedResponse,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError<ErrorResponse>) => {
        if (error.response) {
          const message = error.response.data?.message || 'An error occurred';
          console.error('API Error:', message);
        }
        return Promise.reject(error);
      }
    );
  }

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }

  // Nurses
  async getNurses(params?: PaginationParams): Promise<PaginatedResponse<Nurse>> {
    const response = await this.client.get('/nurses', { params });
    return response.data;
  }

  async getNurse(id: string): Promise<Nurse> {
    const response = await this.client.get(`/nurses/${id}`);
    return response.data;
  }

  async getNurseTranscripts(
    nurseId: string,
    params?: PaginationParams
  ): Promise<PaginatedResponse<Transcript>> {
    const response = await this.client.get(`/nurses/${nurseId}/transcripts`, { params });
    return response.data;
  }

  async getNurseStatistics(nurseId: string): Promise<Record<string, unknown>> {
    const response = await this.client.get(`/nurses/${nurseId}/statistics`);
    return response.data;
  }

  // Patients
  async getPatients(params?: PaginationParams): Promise<PaginatedResponse<Patient>> {
    const response = await this.client.get('/patients', { params });
    return response.data;
  }

  async getPatient(id: string): Promise<Patient> {
    const response = await this.client.get(`/patients/${id}`);
    return response.data;
  }

  async getPatientTranscripts(
    patientId: string,
    params?: PaginationParams
  ): Promise<PaginatedResponse<Transcript>> {
    const response = await this.client.get(`/patients/${patientId}/transcripts`, { params });
    return response.data;
  }

  // Sessions
  async getSessions(params?: PaginationParams): Promise<PaginatedResponse<Session>> {
    const response = await this.client.get('/sessions', { params });
    return response.data;
  }

  async getSession(id: string): Promise<Session> {
    const response = await this.client.get(`/sessions/${id}`);
    return response.data;
  }

  async startSession(data: {
    nurseId: string;
    patientId: string;
    sessionType: string;
    department: string;
  }): Promise<Session> {
    const response = await this.client.post('/sessions/start', data);
    return response.data;
  }

  async stopSession(sessionId: string): Promise<Session> {
    const response = await this.client.post(`/sessions/${sessionId}/stop`);
    return response.data;
  }

  // Transcripts
  async getTranscript(id: string): Promise<Transcript> {
    const response = await this.client.get(`/transcripts/${id}`);
    return response.data;
  }

  async processTranscript(data: {
    sessionId: string;
    nurseId: string;
    patientId: string;
    transcriptText: string;
    metadata: Record<string, unknown>;
  }): Promise<ApiResponse<{ jobId: string }>> {
    const response = await this.client.post('/transcripts/process', data);
    return response.data;
  }

  async getTranscriptStatus(transcriptId: string): Promise<{ status: string }> {
    const response = await this.client.get(`/transcripts/${transcriptId}/status`);
    return response.data;
  }

  // Classifications
  async getClassification(transcriptId: string): Promise<Classification> {
    const response = await this.client.get(`/transcripts/${transcriptId}/classification`);
    return response.data;
  }

  // Notifications
  async getNotifications(params?: PaginationParams): Promise<PaginatedResponse<Notification>> {
    const response = await this.client.get('/notifications', { params });
    return response.data;
  }

  async getAlerts(): Promise<Notification[]> {
    const response = await this.client.get('/notifications/alerts');
    return response.data;
  }

  async markNotificationRead(id: string): Promise<void> {
    await this.client.put(`/notifications/${id}/read`);
  }

  async markAllNotificationsRead(): Promise<void> {
    await this.client.put('/notifications/read-all');
  }

  async createNotification(data: Partial<Notification>): Promise<Notification> {
    const response = await this.client.post('/notifications', data);
    return response.data;
  }

  // Jobs
  async getJobStatus(jobId: string): Promise<ProcessingJob> {
    const response = await this.client.get(`/jobs/${jobId}/status`);
    return response.data;
  }

  // Dashboard
  async getDashboardStats(): Promise<DashboardStats> {
    const response = await this.client.get('/dashboard/stats');
    return response.data;
  }

  async getRiskTrends(days: number = 30): Promise<Record<string, unknown>[]> {
    const response = await this.client.get('/dashboard/risk-trends', { params: { days } });
    return response.data;
  }
}

export const apiClient = new ApiClient();
export default apiClient;
