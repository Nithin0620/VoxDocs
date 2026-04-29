import React from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import AppLayout from './components/AppLayout'
import AuthCallback from './pages/AuthCallback'
import LoginPage from './pages/LoginPage'
import ProtectedRoute from './components/ProtectedRoute'
import SignupPage from './pages/SignupPage'
import Home from './pages/Home'
import UploadPage from './pages/UploadPage'
import DocumentsPage from './pages/DocumentsPage'
import AskPage from './pages/AskPage'
import SessionsPage from './pages/SessionsPage'
import VoicePage from './pages/VoicePage'
import ToastStack from './components/ToastStack'
import { useAuth } from './context/AuthContext'
import Loading from './components/Loading'

function AppRedirect() {
  const { isAuthenticated, initializing } = useAuth()

  if (initializing) {
    return <Loading message="Loading VoxDocs..." />
  }

  return <Navigate to={isAuthenticated ? '/' : '/login'} replace />
}

export default function App() {
  return (
    <>
      <ToastStack />
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/auth/callback" element={<AuthCallback />} />
        <Route element={<ProtectedRoute />}>
          <Route element={<AppLayout />}>
            <Route path="/" element={<Home />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/documents" element={<DocumentsPage />} />
            <Route path="/ask" element={<AskPage />} />
            <Route path="/sessions" element={<SessionsPage />} />
            <Route path="/voice" element={<VoicePage />} />
          </Route>
        </Route>
        <Route path="*" element={<AppRedirect />} />
      </Routes>
    </>
  )
}
