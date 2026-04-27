import React, { Suspense, lazy } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Layout from './components/Layout'
import Loading from './components/Loading'

// Lazy load pages for better performance
const Login = lazy(() => import('./pages/Login'))
const Register = lazy(() => import('./pages/Register'))
const AdminDashboard = lazy(() => import('./pages/admin/Dashboard'))
const StudentDashboard = lazy(() => import('./pages/student/Dashboard'))
const Exam = lazy(() => import('./pages/student/Exam'))
const Results = lazy(() => import('./pages/student/Results'))
const ShareJoin = lazy(() => import('./pages/ShareJoin'))

function ProtectedRoute({ children, allowedRoles }) {
  const { user, isAuthenticated } = useAuthStore()
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  if (allowedRoles && !allowedRoles.includes(user?.role)) {
    return <Navigate to="/" replace />
  }
  
  return children
}

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/join/:token" element={<ShareJoin />} />
        
        {/* Protected routes */}
        <Route path="/" element={<Layout />}>
          <Route index element={
            <ProtectedRoute>
              <RoleRedirect />
            </ProtectedRoute>
          } />
          
          {/* Admin routes */}
          <Route path="admin/*" element={
            <ProtectedRoute allowedRoles={['admin']}>
              <AdminDashboard />
            </ProtectedRoute>
          } />
          
          {/* Student routes */}
          <Route path="student/*" element={
            <ProtectedRoute allowedRoles={['student']}>
              <StudentDashboard />
            </ProtectedRoute>
          } />
          <Route path="exam/:id" element={
            <ProtectedRoute allowedRoles={['student']}>
              <Exam />
            </ProtectedRoute>
          } />
          <Route path="results" element={
            <ProtectedRoute allowedRoles={['student']}>
              <Results />
            </ProtectedRoute>
          } />
        </Route>
        
        {/* Catch all - redirect to login */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </Suspense>
  )
}

function RoleRedirect() {
  const { user } = useAuthStore()
  
  if (user?.role === 'admin') {
    return <Navigate to="/admin" replace />
  }
  return <Navigate to="/student" replace />
}

export default App
