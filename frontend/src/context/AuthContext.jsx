import React, { createContext, useContext, useEffect, useRef, useState } from 'react'
import { getCurrentUser, getGoogleAuthUrl, signIn, signOut, signUp } from '../api'

const AuthContext = createContext(null)

function createToastId() {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID()
  }
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [initializing, setInitializing] = useState(true)
  const [toasts, setToasts] = useState([])
  const timersRef = useRef(new Map())

  useEffect(() => {
    let mounted = true

    async function bootstrap() {
      try {
        const response = await getCurrentUser()
        if (mounted) {
          setUser(response.user)
        }
      } catch {
        if (mounted) {
          setUser(null)
        }
      } finally {
        if (mounted) {
          setInitializing(false)
        }
      }
    }

    bootstrap()

    return () => {
      mounted = false
      timersRef.current.forEach(clearTimeout)
      timersRef.current.clear()
    }
  }, [])

  function pushToast(toast) {
    const id = createToastId()
    setToasts(previous => [...previous, { id, ...toast }])
    const timeoutId = window.setTimeout(() => {
      setToasts(previous => previous.filter(entry => entry.id !== id))
      timersRef.current.delete(id)
    }, 3600)
    timersRef.current.set(id, timeoutId)
    return id
  }

  function removeToast(id) {
    setToasts(previous => previous.filter(entry => entry.id !== id))
    const timeoutId = timersRef.current.get(id)
    if (timeoutId) {
      clearTimeout(timeoutId)
      timersRef.current.delete(id)
    }
  }

  async function refreshUser() {
    const response = await getCurrentUser()
    setUser(response.user)
    return response.user
  }

  async function handleSignIn(values) {
    const response = await signIn(values)
    setUser(response.user)
    return response.user
  }

  async function handleSignUp(values) {
    const response = await signUp(values)
    setUser(response.user)
    return response.user
  }

  async function handleSignOut() {
    try {
      await signOut()
    } finally {
      setUser(null)
      pushToast({ type: 'info', title: 'Signed out', message: 'Your session has been cleared.' })
    }
  }

  function startGoogleLogin() {
    window.location.assign(getGoogleAuthUrl())
  }

  const value = {
    user,
    isAuthenticated: Boolean(user),
    initializing,
    toasts,
    pushToast,
    removeToast,
    refreshUser,
    signIn: handleSignIn,
    signUp: handleSignUp,
    signOut: handleSignOut,
    startGoogleLogin,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}