import React, { useState } from 'react'
import { askQuestion, askQuestionWithSession } from '../api'
import Loading from '../components/Loading'
import ErrorMessage from '../components/ErrorMessage'
import EmptyState from '../components/EmptyState'

// Ask page for free-form queries and session-bound queries
export default function AskPage() {
  const [question, setQuestion] = useState('')
  const [sessionId, setSessionId] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [answer, setAnswer] = useState(null)

  // Submit a standalone question
  async function handleAsk(e) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setAnswer(null)
    try {
      const resp = await askQuestion(question, false)
      setAnswer(resp)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // Submit question within a session context
  async function handleAskWithSession(e) {
    e.preventDefault()
    if (!sessionId) return setError('Please provide a session ID')
    setLoading(true)
    setError(null)
    setAnswer(null)
    try {
      const resp = await askQuestionWithSession(sessionId, question, false)
      setAnswer(resp)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <h2 className="text-xl font-semibold">Ask Documents</h2>
      <form onSubmit={handleAsk} className="p-4 bg-white border rounded space-y-3">
        <label className="block text-sm font-medium">Question</label>
        <textarea value={question} onChange={e=>setQuestion(e.target.value)} rows={4} className="w-full p-2 border rounded" />
        <div className="flex gap-2">
          <button disabled={loading} className="px-4 py-2 bg-slate-800 text-white rounded">Ask</button>
          <input placeholder="Session ID (optional)" value={sessionId} onChange={e=>setSessionId(e.target.value)} className="p-2 border rounded" />
          <button type="button" onClick={handleAskWithSession} className="px-3 py-2 bg-slate-100 rounded">Ask with Session</button>
        </div>
      </form>

      {loading && <Loading message="Processing question..." />}
      {error && <ErrorMessage error={error} />}

      {answer ? (
        <div className="p-4 bg-white border rounded">
          <div className="font-medium">Answer</div>
          <div className="mt-2 text-slate-700">{answer.answer}</div>
          <div className="mt-3 text-sm text-slate-500">Sources: {answer.sources && answer.sources.length ? answer.sources.join(', ') : 'None'}</div>
        </div>
      ) : (
        <EmptyState title="No answer yet" description="Ask a question to get started." />
      )}
    </div>
  )
}
