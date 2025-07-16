# Face Recognition Attendance System - Frontend

A modern, secure Single-Page Application (SPA) built with React and TypeScript for the Face Recognition Attendance System. This frontend integrates seamlessly with the FastAPI backend to provide real-time attendance monitoring, employee management, and camera surveillance capabilities.

## 🚀 Features

### 🔐 Authentication & Security
- **JWT-based Authentication** with automatic token refresh
- **Role-based Access Control** (Admin/Employee roles)
- **Protected Routes** with automatic redirects
- **Secure API Communication** with interceptors

### 👥 User Roles

#### Employee Features
- **Personal Dashboard** with attendance overview
- **Attendance History** with filtering and search
- **Profile Management** and face enrollment status
- **Real-time Status** updates

#### Admin Features
- **System Dashboard** with comprehensive analytics
- **Employee Management** (CRUD operations)
- **Real-time Camera Monitoring** with multiple feeds
- **Attendance Reports** and analytics
- **System Configuration** and monitoring

### 🎨 Modern UI/UX
- **Responsive Design** with mobile-first approach
- **Dark/Light Mode** toggle with system preference detection
- **Modern Styling** with Tailwind CSS
- **Interactive Components** with smooth animations
- **Accessibility Compliant** (WCAG 2.1)

### 📊 Real-time Features
- **Live Camera Feeds** with WebSocket integration
- **Real-time Notifications** and status updates
- **Auto-refreshing Data** for dashboards
- **Live Attendance Tracking**

## 🛠️ Tech Stack

- **Framework:** React 19+ with TypeScript
- **Routing:** React Router v6
- **Styling:** Tailwind CSS with custom design system
- **State Management:** React Context + Custom Hooks
- **Data Fetching:** TanStack Query (React Query)
- **HTTP Client:** Axios with interceptors
- **Icons:** Lucide React
- **Date Handling:** date-fns
- **Charts:** Chart.js & Recharts
- **Build Tool:** Create React App

## 📁 Project Structure

```
src/
├── components/           # Reusable UI components
│   ├── auth/            # Authentication components
│   ├── common/          # Shared components
│   ├── dashboard/       # Dashboard components
│   └── ...
├── contexts/            # React contexts for state management
│   ├── AuthContext.tsx  # Authentication state
│   └── ThemeContext.tsx # Theme management
├── hooks/               # Custom React hooks
├── pages/               # Page components
│   ├── dashboard/       # Dashboard pages
│   ├── cameras/         # Camera monitoring
│   └── ...
├── services/            # API and external services
│   └── api.ts          # Main API service
├── types/               # TypeScript type definitions
│   └── common.ts       # Shared types
├── utils/               # Utility functions
└── App.tsx             # Main application component
```

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm
- Running FastAPI backend (see backend documentation)

### Installation

1. **Clone and navigate to the frontend directory:**
   ```bash
   cd face-recognition-frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file:
   ```env
   REACT_APP_API_URL=http://localhost:8000
   REACT_APP_WS_URL=ws://localhost:8000
   REACT_APP_DEFAULT_THEME=light
   REACT_APP_ENV=development
   ```

4. **Start the development server:**
   ```bash
   npm start
   ```

5. **Open your browser:**
   Navigate to `http://localhost:3000`

### Demo Credentials

```
Admin Access:
Username: admin
Password: admin

Employee Access:  
Username: employee
Password: employee
```

## 🔧 Configuration

### API Integration

The frontend communicates with the FastAPI backend through:

- **REST APIs** for CRUD operations
- **HTTP Streaming** for camera feeds
- **WebSocket** connections for real-time updates

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REACT_APP_API_URL` | Backend API base URL | `http://localhost:8000` |
| `REACT_APP_WS_URL` | WebSocket URL | `ws://localhost:8000` |
| `REACT_APP_DEFAULT_THEME` | Default theme | `light` |
| `REACT_APP_ENV` | Environment | `development` |

## 📱 Features Walkthrough

### Authentication Flow
1. Users login with username/password
2. JWT token stored securely in localStorage
3. Automatic token validation and refresh
4. Role-based dashboard routing

### Employee Dashboard
- **Today's Status:** Present/Absent with visual indicators
- **Attendance Statistics:** Weekly and monthly summaries
- **Recent Records:** Timeline of attendance entries
- **Profile Information:** Employee details and face enrollment status

### Admin Dashboard
- **System Overview:** Real-time statistics and monitoring
- **Employee Management:** Add, edit, delete employee records
- **Camera Monitoring:** Live feeds from multiple cameras
- **Reports & Analytics:** Attendance trends and insights

### Camera System
- **Real-time Streaming:** MJPEG streams from backend
- **Multiple Views:** Grid and list layout options
- **Status Monitoring:** Camera availability and stream counts
- **Face Detection:** Live recognition with confidence scores

## 🎨 UI/UX Features

### Design System
- **Color Palette:** Professional blue-gray theme with semantic colors
- **Typography:** System fonts optimized for readability
- **Spacing:** Consistent 8px grid system
- **Components:** Reusable UI patterns with variants

### Dark Mode
- **System Detection:** Automatically detects user preference
- **Manual Toggle:** Switch between light and dark themes
- **Persistent:** Theme choice saved in localStorage
- **Consistent:** All components support both modes

### Responsive Design
- **Mobile First:** Optimized for mobile devices
- **Breakpoints:** Tailored layouts for different screen sizes
- **Touch Friendly:** Proper touch targets and gestures
- **Progressive Enhancement:** Enhanced features for larger screens

## 🔒 Security Features

### Frontend Security
- **Protected Routes:** Authentication required for sensitive pages
- **Role Validation:** Admin-only features properly restricted
- **Token Management:** Secure storage and automatic cleanup
- **Input Validation:** Client-side validation with server confirmation

### API Security
- **Bearer Tokens:** JWT tokens in Authorization headers
- **Request Interceptors:** Automatic token attachment
- **Error Handling:** Proper error responses and user feedback
- **Rate Limiting:** Client-side request throttling

## 📊 Performance

### Optimization Features
- **Code Splitting:** Lazy loading for better initial load times
- **Image Optimization:** Efficient camera stream handling
- **Caching:** Smart data caching with React Query
- **Bundle Analysis:** Optimized production builds

### Real-time Performance
- **Efficient Updates:** Minimal re-renders with proper state management
- **Stream Management:** Intelligent camera stream lifecycle
- **Background Tasks:** Non-blocking data fetching
- **Memory Management:** Proper cleanup of resources

## 🧪 Development

### Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run test suite
- `npm run eject` - Eject from Create React App

### Development Guidelines

1. **Code Style:** Follow TypeScript and React best practices
2. **Component Design:** Create reusable, accessible components
3. **State Management:** Use Context for global state, local state for components
4. **Error Handling:** Implement proper error boundaries and user feedback
5. **Testing:** Write unit tests for critical functionality

## 🚀 Deployment

### Production Build

```bash
npm run build
```

This creates an optimized build in the `build/` directory ready for deployment.

### Environment Setup

1. **Configure production API URL** in environment variables
2. **Set up HTTPS** for secure communication
3. **Configure CORS** on the backend for your domain
4. **Set up monitoring** and error tracking

### Deployment Options

- **Static Hosting:** Netlify, Vercel, AWS S3 + CloudFront
- **Container Deployment:** Docker with Nginx
- **Traditional Hosting:** Apache or Nginx web server

## 🤝 Integration with Backend

### API Endpoints Used

- `POST /auth/login/` - User authentication
- `GET /auth/secure/` - Token verification
- `GET /employees/` - Employee list
- `GET /attendance/` - Attendance records
- `GET /stream/{camera_id}` - Camera streaming
- `GET /stream/status/{camera_id}` - Camera status

### Real-time Features

- **HTTP Streaming:** For camera feeds
- **WebSocket:** For live notifications (planned)
- **Polling:** For dashboard updates

## 📝 License

This project is part of the Face Recognition Attendance System. See the main project documentation for licensing information.

## 🆘 Troubleshooting

### Common Issues

1. **Connection Errors:** Verify backend is running on correct port
2. **Authentication Issues:** Check JWT token expiration and backend auth configuration
3. **Camera Streams:** Ensure cameras are connected and accessible
4. **Build Errors:** Clear node_modules and reinstall dependencies

### Getting Help

- Check the browser console for error messages
- Verify network connectivity to the backend
- Ensure all environment variables are properly configured
- Review the backend logs for API errors

---

**🎯 Ready to monitor attendance with modern technology!**

This frontend provides a professional, scalable solution for face recognition attendance tracking with enterprise-grade security and user experience.
