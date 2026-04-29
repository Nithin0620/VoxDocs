import React, { useEffect, useState } from 'react'
import { getAllSessions, getSessionHistory, createSession, deleteSession } from '../api'
import Loading from '../components/Loading'
import ErrorMessage from '../components/ErrorMessage'
import EmptyState from '../components/EmptyState'
import SessionCard from '../components/SessionCard'

// Sessions page showing list and history
export default function SessionsPage() {
  const [sessions, setSessions] = useState([])
  const [selected, setSelected] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [creating, setCreating] = useState(false)

  // Load sessions on mount
  useEffect(() => {
    loadSessions()
  }, [])

  async function loadSessions() {
    setLoading(true)
    setError(null)
    try {
      const data = await getAllSessions()
      setSessions(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function openSession(id) {
    setLoading(true)
    try {
      const data = await getSessionHistory(id)
      setSelected(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleCreate() {
    setCreating(true)
    try {
      await createSession(null)
      await loadSessions()
    } catch (err) {
      setError(err.message)
    } finally {
      setCreating(false)
    }
  }

  async function handleDelete(id) {
    if (!window.confirm('Delete this session?')) return
    try {
      await deleteSession(id)
      await loadSessions()
      setSelected(null)
    } catch (err) {
      setError(err.message)
    }
  }

  if (loading) return <Loading message="Loading sessions..." />
  if (error) return <ErrorMessage error={error} />

  return (
    <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-4">
      <div>
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-lg font-semibold">Sessions</h3>
          <button onClick={handleCreate} disabled={creating} className="px-3 py-1 bg-slate-800 text-white rounded">New</button>
        </div>

        {sessions.length === 0 && <EmptyState title="No sessions" description="Create a new session to start a conversation." />}
        <div className="space-y-2">
          {sessions.map(s => (
            <SessionCard key={s.id} session={s} onOpen={openSession} onDelete={handleDelete} />
          ))}
        </div>
      </div>

      <div className="md:col-span-2">
        <h3 className="text-lg font-semibold">Conversation</h3>
        {selected ? (
          <div className="p-4 bg-white border rounded space-y-3">
            <div className="font-medium">{selected.session.title}</div>
            {selected.messages.length === 0 ? (
              <EmptyState title="No messages" description="Ask questions in this session to build history." />
            ) : (
              <div className="space-y-4">
                {selected.messages.map(m => (
                  <div key={m.id} className="p-3 border rounded">
                    <div className="text-sm text-slate-600">{new Date(m.created_at).toLocaleString()}</div>
                    <div className="mt-2"><strong>Q:</strong> {m.question}</div>
                    <div className="mt-1 text-slate-700"><strong>A:</strong> {m.answer}</div>
                    <div className="mt-1 text-sm text-slate-500">Sources: {m.sources.join(', ')}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          <EmptyState title="Select a session" description="Choose a session to view its conversation history." />
        )}
      </div>
    </div>
  )
}
