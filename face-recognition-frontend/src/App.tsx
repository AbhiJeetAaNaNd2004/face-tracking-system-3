import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import ProtectedRoute from './components/common/ProtectedRoute';
import Layout from './components/common/Layout';
import LoginForm from './components/auth/LoginForm';
import EmployeeDashboard from './pages/dashboard/EmployeeDashboard';
import AdminDashboard from './pages/dashboard/AdminDashboard';
import CamerasPage from './pages/cameras/CamerasPage';
import LoadingSpinner from './components/common/LoadingSpinner';

// Create a client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

// Dashboard component that routes based on user role
const Dashboard: React.FC = () => {
  const { user } = useAuth();
  
  if (user?.role === 'admin') {
    return <AdminDashboard />;
  } else {
    return <EmployeeDashboard />;
  }
};

// Placeholder components for future implementation
const EmployeesPage: React.FC = () => (
  <div className="p-6">
    <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
      Employee Management
    </h1>
    <div className="card p-6">
      <p className="text-gray-600 dark:text-gray-400">
        Employee management functionality will be implemented here.
      </p>
    </div>
  </div>
);

const AttendancePage: React.FC = () => (
  <div className="p-6">
    <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
      Attendance Records
    </h1>
    <div className="card p-6">
      <p className="text-gray-600 dark:text-gray-400">
        Detailed attendance records and reporting will be implemented here.
      </p>
    </div>
  </div>
);

const ProfilePage: React.FC = () => (
  <div className="p-6">
    <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
      Profile
    </h1>
    <div className="card p-6">
      <p className="text-gray-600 dark:text-gray-400">
        User profile management will be implemented here.
      </p>
    </div>
  </div>
);

const SettingsPage: React.FC = () => (
  <div className="p-6">
    <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
      Settings
    </h1>
    <div className="card p-6">
      <p className="text-gray-600 dark:text-gray-400">
        System settings and configuration will be implemented here.
      </p>
    </div>
  </div>
);

const UnauthorizedPage: React.FC = () => (
  <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
    <div className="max-w-md w-full text-center">
      <div className="mb-4">
        <div className="mx-auto h-12 w-12 flex items-center justify-center bg-red-100 rounded-full">
          <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
      </div>
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
        Unauthorized Access
      </h1>
      <p className="text-gray-600 dark:text-gray-400 mb-6">
        You don't have permission to access this page.
      </p>
      <button 
        onClick={() => window.history.back()}
        className="btn-primary"
      >
        Go Back
      </button>
    </div>
  </div>
);

const NotFoundPage: React.FC = () => (
  <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
    <div className="max-w-md w-full text-center">
      <div className="mb-4">
        <div className="mx-auto h-12 w-12 flex items-center justify-center bg-gray-100 rounded-full">
          <svg className="h-6 w-6 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 15c-2.34 0-4.5-.9-6.1-2.379C7.27 10.654 9.5 9 12 9s4.73 1.654 6.1 3.621z" />
          </svg>
        </div>
      </div>
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
        Page Not Found
      </h1>
      <p className="text-gray-600 dark:text-gray-400 mb-6">
        The page you're looking for doesn't exist.
      </p>
      <button 
        onClick={() => window.location.href = '/dashboard'}
        className="btn-primary"
      >
        Go to Dashboard
      </button>
    </div>
  </div>
);

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AuthProvider>
          <Router>
            <div className="App">
              <Routes>
                {/* Public routes */}
                <Route path="/login" element={<LoginForm />} />
                <Route path="/unauthorized" element={<UnauthorizedPage />} />
                
                {/* Protected routes */}
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route
                  path="/dashboard"
                  element={
                    <ProtectedRoute>
                      <Layout>
                        <Dashboard />
                      </Layout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/employees"
                  element={
                    <ProtectedRoute requireAdmin>
                      <Layout>
                        <EmployeesPage />
                      </Layout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/attendance"
                  element={
                    <ProtectedRoute>
                      <Layout>
                        <AttendancePage />
                      </Layout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/cameras"
                  element={
                    <ProtectedRoute requireAdmin>
                      <Layout>
                        <CamerasPage />
                      </Layout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/profile"
                  element={
                    <ProtectedRoute>
                      <Layout>
                        <ProfilePage />
                      </Layout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/settings"
                  element={
                    <ProtectedRoute requireAdmin>
                      <Layout>
                        <SettingsPage />
                      </Layout>
                    </ProtectedRoute>
                  }
                />
                
                {/* Catch all route */}
                <Route path="*" element={<NotFoundPage />} />
              </Routes>
            </div>
          </Router>
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
