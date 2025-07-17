import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { 
  LoginRequest, 
  LoginResponse, 
  Employee, 
  AttendanceRecord, 
  CameraStatus,
  ApiResponse 
} from '../types/common';

// API Base URL - adjust based on your backend configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor to handle common errors
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Authentication
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response: AxiosResponse<LoginResponse> = await this.api.post('/auth/login/', credentials);
    return response.data;
  }

  async verifyToken(): Promise<any> {
    const response = await this.api.get('/auth/secure/');
    return response.data;
  }

  // Employee Management
  async getEmployees(): Promise<Employee[]> {
    const response: AxiosResponse<Employee[]> = await this.api.get('/employees/');
    return response.data;
  }

  async getEmployee(employeeId: string): Promise<Employee> {
    const response: AxiosResponse<Employee> = await this.api.get(`/employees/${employeeId}`);
    return response.data;
  }

  async createEmployee(employee: Omit<Employee, 'created_at' | 'updated_at'>): Promise<Employee> {
    const response: AxiosResponse<Employee> = await this.api.post('/employees/', employee);
    return response.data;
  }

  async updateEmployee(employeeId: string, employee: Partial<Employee>): Promise<Employee> {
    const response: AxiosResponse<Employee> = await this.api.put(`/employees/${employeeId}`, employee);
    return response.data;
  }

  async deleteEmployee(employeeId: string): Promise<{ deleted: boolean; message: string }> {
    const response = await this.api.delete(`/employees/${employeeId}`);
    return response.data;
  }

  // Attendance
  async getAttendanceRecords(limit: number = 50): Promise<AttendanceRecord[]> {
    const response: AxiosResponse<AttendanceRecord[]> = await this.api.get('/attendance/', {
      params: { limit }
    });
    return response.data;
  }

  async getEmployeeAttendance(employeeId: string): Promise<AttendanceRecord[]> {
    const response: AxiosResponse<AttendanceRecord[]> = await this.api.get(`/attendance/${employeeId}`);
    return response.data;
  }

  // Camera/Streaming
  async getCameraStatus(cameraId: number): Promise<CameraStatus> {
    const response: AxiosResponse<CameraStatus> = await this.api.get(`/stream/status/${cameraId}`);
    return response.data;
  }

  async getStreamStatus(): Promise<{ total_active_streams: number; max_concurrent_streams: number; available_slots: number }> {
    const response = await this.api.get('/stream/');
    return response.data;
  }

  // Get camera stream URL
  getCameraStreamUrl(cameraId: number): string {
    const token = localStorage.getItem('access_token');
    return `${API_BASE_URL}/stream/${camera_id}`;
  }

  // WebSocket connection for real-time updates
  createWebSocketConnection(endpoint: string): WebSocket {
    const token = localStorage.getItem('access_token');
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/${endpoint}?token=${token}`;
    return new WebSocket(wsUrl);
  }

  // Health check
  async healthCheck(): Promise<{ message: string }> {
    const response = await this.api.get('/');
    return response.data;
  }
}

export const apiService = new ApiService();
export default apiService;