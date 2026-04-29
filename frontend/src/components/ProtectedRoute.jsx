import React from 'react'
import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Loading from './Loading'

export default function ProtectedRoute() {
  const { isAuthenticated, initializing } = useAuth()
  const location = useLocation()

  if (initializing) {
    return <Loading message="Restoring your session..." />
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }

  return <Outlet />
}