import React, { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Loading from './Loading'

export default function AuthCallbackGuard() {
  const { refreshUser, pushToast } = useAuth()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()

  useEffect(() => {
    async function complete() {
      const status = searchParams.get('status')
      const error = searchParams.get('error')

      if (error) {
        pushToast({ type: 'error', title: 'Google sign-in failed', message: error })
        navigate('/login', { replace: true })
        return
      }

      try {
        await refreshUser()
        if (status === 'success') {
          pushToast({ type: 'success', title: 'Signed in with Google', message: 'Your session is ready.' })
        }
        navigate('/', { replace: true })
      } catch (err) {
        pushToast({ type: 'error', title: 'Session restore failed', message: err.message })
        navigate('/login', { replace: true })
      }
    }

    complete()
  }, [navigate, pushToast, refreshUser, searchParams])

  return <Loading message="Completing Google sign-in..." />
}