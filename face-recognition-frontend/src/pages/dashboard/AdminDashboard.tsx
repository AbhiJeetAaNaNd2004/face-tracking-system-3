import React, { useState, useEffect } from 'react';
import { 
  Users, 
  Clock, 
  Camera, 
  TrendingUp, 
  AlertTriangle,
  CheckCircle,
  BarChart3,
  RefreshCw
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { AttendanceRecord, Employee, AttendanceStats } from '../../types/common';
import apiService from '../../services/api';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { format, startOfDay, parseISO } from 'date-fns';

const AdminDashboard: React.FC = () => {
  const { user } = useAuth();
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [attendance, setAttendance] = useState<AttendanceRecord[]>([]);
  const [streamStatus, setStreamStatus] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState(new Date());

  const fetchData = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const [employeesData, attendanceData, streamData] = await Promise.all([
        apiService.getEmployees().catch(() => []),
        apiService.getAttendanceRecords(100).catch(() => []),
        apiService.getStreamStatus().catch(() => ({ total_active_streams: 0, max_concurrent_streams: 5, available_slots: 5 }))
      ]);
      
      setEmployees(employeesData);
      setAttendance(attendanceData);
      setStreamStatus(streamData);
      setLastRefresh(new Date());
    } catch (err: any) {
      console.error('Dashboard fetch error:', err);
      setError('Some dashboard data may be unavailable');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (isLoading && !attendance.length) {
    return <LoadingSpinner fullScreen text="Loading admin dashboard..." />;
  }

  // Calculate statistics
  const today = new Date();
  const todayStart = startOfDay(today);
  
  const todayAttendance = attendance.filter(record => {
    const recordDate = parseISO(record.timestamp);
    return recordDate >= todayStart;
  });

  const uniqueEmployeesToday = new Set(todayAttendance.map(record => record.employee_id));
  const presentToday = uniqueEmployeesToday.size;
  const totalEmployees = employees.length;
  const attendanceRate = totalEmployees > 0 ? Math.round((presentToday / totalEmployees) * 100) : 0;

  const stats = [
    {
      title: 'Total Employees',
      value: totalEmployees.toString(),
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100 dark:bg-blue-900/20',
      change: null
    },
    {
      title: 'Present Today',
      value: presentToday.toString(),
      icon: CheckCircle,
      color: 'text-green-600',
      bgColor: 'bg-green-100 dark:bg-green-900/20',
      change: `${attendanceRate}% attendance rate`
    },
    {
      title: 'Active Streams',
      value: streamStatus?.total_active_streams?.toString() || '0',
      icon: Camera,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100 dark:bg-purple-900/20',
      change: `${streamStatus?.available_slots || 0} slots available`
    },
    {
      title: 'Today\'s Records',
      value: todayAttendance.length.toString(),
      icon: BarChart3,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-100 dark:bg-indigo-900/20',
      change: null
    }
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Admin Dashboard
          </h1>
          <p className="mt-1 text-gray-600 dark:text-gray-400">
            System overview and real-time monitoring
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex items-center space-x-4">
          <span className="text-sm text-gray-500 dark:text-gray-400">
            Last updated: {format(lastRefresh, 'HH:mm:ss')}
          </span>
          <button
            onClick={fetchData}
            disabled={isLoading}
            className="btn-secondary flex items-center"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/50 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <div className="flex items-center">
            <AlertTriangle className="h-5 w-5 text-red-600 dark:text-red-400 mr-2" />
            <p className="text-red-600 dark:text-red-400">{error}</p>
          </div>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div key={index} className="card p-6">
              <div className="flex items-center">
                <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                  <Icon className={`h-6 w-6 ${stat.color}`} />
                </div>
                <div className="ml-4 flex-1">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                    {stat.title}
                  </p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {stat.value}
                  </p>
                  {stat.change && (
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {stat.change}
                    </p>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Recent Activity & System Status */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Attendance */}
        <div className="card">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              Recent Attendance
            </h3>
          </div>
          <div className="p-6">
            {todayAttendance.length === 0 ? (
              <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                No attendance records today
              </p>
            ) : (
              <div className="space-y-4 max-h-80 overflow-y-auto">
                {todayAttendance.slice(0, 10).map((record, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center">
                      <Clock className="h-4 w-4 text-gray-400 mr-2" />
                      <div>
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          {record.employee_id}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {format(parseISO(record.timestamp), 'hh:mm a')}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center">
                      {record.confidence_score && (
                        <span className="text-xs text-gray-500 dark:text-gray-400 mr-2">
                          {Math.round(record.confidence_score * 100)}%
                        </span>
                      )}
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400">
                        {record.event_type || 'Present'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* System Status */}
        <div className="card">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              System Status
            </h3>
          </div>
          <div className="p-6 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">API Status</span>
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400">
                <span className="w-2 h-2 bg-green-400 rounded-full mr-1"></span>
                Online
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">Camera Streams</span>
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                {streamStatus?.total_active_streams || 0} / {streamStatus?.max_concurrent_streams || 5}
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">Database</span>
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400">
                <span className="w-2 h-2 bg-green-400 rounded-full mr-1"></span>
                Connected
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">Face Recognition</span>
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400">
                <span className="w-2 h-2 bg-green-400 rounded-full mr-1"></span>
                Active
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
            Quick Actions
          </h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <button className="btn-primary flex items-center justify-center">
              <Users className="h-4 w-4 mr-2" />
              Manage Employees
            </button>
            <button className="btn-secondary flex items-center justify-center">
              <Camera className="h-4 w-4 mr-2" />
              View Cameras
            </button>
            <button className="btn-secondary flex items-center justify-center">
              <BarChart3 className="h-4 w-4 mr-2" />
              Generate Report
            </button>
            <button className="btn-secondary flex items-center justify-center">
              <TrendingUp className="h-4 w-4 mr-2" />
              Analytics
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;