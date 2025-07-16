// Common types used throughout the application

export interface User {
  id: number;
  username: string;
  role: 'admin' | 'employee';
  status: 'active' | 'inactive' | 'suspended';
  lastLoginTime?: string;
  createdAt: string;
  updatedAt: string;
}

export interface Employee {
  employee_id: string;
  name: string;
  department?: string;
  designation?: string;
  email?: string;
  phone?: string;
  created_at?: string;
  updated_at?: string;
}

export interface AttendanceRecord {
  id?: number;
  employee_id: string;
  timestamp: string;
  confidence_score?: number;
  camera_id?: number;
  event_type?: string;
  work_status?: string;
  notes?: string;
}

export interface CameraStatus {
  camera_id: number;
  is_available: boolean;
  active_streams: number;
  max_streams: number;
}

export interface SystemNotification {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: number;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface AttendanceStats {
  totalEmployees: number;
  presentToday: number;
  averageAttendance: number;
  lateArrivals: number;
}

export interface ChartDataPoint {
  label: string;
  value: number;
  date?: string;
}

export interface ThemeContextType {
  isDark: boolean;
  toggleTheme: () => void;
}

export interface LoadingState {
  isLoading: boolean;
  error?: string | null;
}

export interface PaginationParams {
  page: number;
  limit: number;
  total?: number;
}