import React, { useState, useEffect } from 'react';
import { 
  Clock, 
  Calendar, 
  User, 
  TrendingUp, 
  CheckCircle, 
  XCircle,
  BarChart3
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { AttendanceRecord, Employee } from '../../types/common';
import apiService from '../../services/api';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { format, startOfMonth, endOfMonth, subDays, parseISO } from 'date-fns';

const EmployeeDashboard: React.FC = () => {
  const { user } = useAuth();
  const [attendance, setAttendance] = useState<AttendanceRecord[]>([]);
  const [employeeData, setEmployeeData] = useState<Employee | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        // In a real implementation, you'd have the employee ID from the user data
        const employeeId = user?.username || 'employee1'; // Fallback for demo
        
        const [attendanceData, empData] = await Promise.all([
          apiService.getEmployeeAttendance(employeeId),
          apiService.getEmployee(employeeId).catch(() => null) // Employee might not exist yet
        ]);
        
        setAttendance(attendanceData);
        setEmployeeData(empData);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch data');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [user]);

  if (isLoading) {
    return <LoadingSpinner fullScreen text="Loading your dashboard..." />;
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 dark:bg-red-900/50 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-red-600 dark:text-red-400">{error}</p>
        </div>
      </div>
    );
  }

  // Calculate statistics
  const today = new Date();
  const thisMonth = attendance.filter(record => {
    const recordDate = parseISO(record.timestamp);
    return recordDate >= startOfMonth(today) && recordDate <= endOfMonth(today);
  });

  const thisWeek = attendance.filter(record => {
    const recordDate = parseISO(record.timestamp);
    return recordDate >= subDays(today, 7);
  });

  const todayAttendance = attendance.filter(record => {
    const recordDate = parseISO(record.timestamp);
    return format(recordDate, 'yyyy-MM-dd') === format(today, 'yyyy-MM-dd');
  });

  const stats = [
    {
      title: 'Today\'s Status',
      value: todayAttendance.length > 0 ? 'Present' : 'Absent',
      icon: todayAttendance.length > 0 ? CheckCircle : XCircle,
      color: todayAttendance.length > 0 ? 'text-green-600' : 'text-red-600',
      bgColor: todayAttendance.length > 0 ? 'bg-green-100 dark:bg-green-900/20' : 'bg-red-100 dark:bg-red-900/20'
    },
    {
      title: 'This Week',
      value: `${thisWeek.length} days`,
      icon: Calendar,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100 dark:bg-blue-900/20'
    },
    {
      title: 'This Month',
      value: `${thisMonth.length} days`,
      icon: BarChart3,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100 dark:bg-purple-900/20'
    },
    {
      title: 'Total Records',
      value: attendance.length.toString(),
      icon: TrendingUp,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-100 dark:bg-indigo-900/20'
    }
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Welcome back, {user?.username}!
          </h1>
          <p className="mt-1 text-gray-600 dark:text-gray-400">
            Here's your attendance overview
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400">
            <span className="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
            Active Employee
          </span>
        </div>
      </div>

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
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                    {stat.title}
                  </p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {stat.value}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Recent Attendance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              Recent Attendance
            </h3>
          </div>
          <div className="p-6">
            {attendance.length === 0 ? (
              <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                No attendance records found
              </p>
            ) : (
              <div className="space-y-4">
                {attendance.slice(0, 5).map((record, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center">
                      <Clock className="h-4 w-4 text-gray-400 mr-2" />
                      <div>
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          {format(parseISO(record.timestamp), 'MMM dd, yyyy')}
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

        {/* Profile Information */}
        <div className="card">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              Profile Information
            </h3>
          </div>
          <div className="p-6">
            <div className="flex items-center mb-6">
              <div className="h-16 w-16 bg-primary-600 rounded-full flex items-center justify-center">
                <User className="h-8 w-8 text-white" />
              </div>
              <div className="ml-4">
                <h4 className="text-lg font-medium text-gray-900 dark:text-white">
                  {employeeData?.name || user?.username}
                </h4>
                <p className="text-gray-600 dark:text-gray-400">
                  {employeeData?.designation || 'Employee'}
                </p>
              </div>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Employee ID
                </label>
                <p className="text-gray-900 dark:text-white">
                  {employeeData?.employee_id || user?.username}
                </p>
              </div>
              
              {employeeData?.department && (
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Department
                  </label>
                  <p className="text-gray-900 dark:text-white">
                    {employeeData.department}
                  </p>
                </div>
              )}
              
              {employeeData?.email && (
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Email
                  </label>
                  <p className="text-gray-900 dark:text-white">
                    {employeeData.email}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmployeeDashboard;