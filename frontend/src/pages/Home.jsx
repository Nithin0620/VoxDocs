import React, { useEffect, useState } from 'react'
import { healthCheck } from '../api'
import Loading from '../components/Loading'
import ErrorMessage from '../components/ErrorMessage'

// Home page with a simple health overview
export default function Home() {
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Load health status on mount
  useEffect(() => {
    async function load() {
      setLoading(true)
      try {
        const resp = await healthCheck()
        setStatus(resp)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) return <Loading message="Checking API health..." />
  if (error) return <ErrorMessage error={error} />

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-semibold mb-4">Welcome to VoxDocs</h1>
      {status ? (
        <div className="p-4 bg-white border rounded">
          <div><strong>{status.name}</strong> — v{status.version}</div>
          <div className="text-slate-600 mt-2">Status: {status.status}</div>
        </div>
      ) : (
        <div className="p-4 text-slate-500">No status available</div>
      )}
    </div>
  )
}
