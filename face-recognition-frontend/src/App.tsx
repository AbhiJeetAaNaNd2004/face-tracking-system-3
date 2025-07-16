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
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
        Page Not Found
      </h1>
      <p className="text-gray-600 dark:text-gray-400 mb-6">
        The page you're looking for doesn't exist.
      </p>
      <Navigate to="/dashboard" replace />
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
