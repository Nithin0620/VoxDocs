import React from 'react'

// Card showing session summary
export default function SessionCard({ session, onOpen, onDelete }) {
  return (
    <div className="p-4 border bg-white rounded flex items-center justify-between">
      <div>
        <div className="font-medium">{session.title}</div>
        <div className="text-sm text-slate-500">Created: {new Date(session.created_at).toLocaleString()}</div>
      </div>
      <div className="space-x-2">
        <button onClick={() => onOpen(session.id)} className="px-3 py-1 bg-slate-100 rounded">Open</button>
        <button onClick={() => onDelete(session.id)} className="px-3 py-1 bg-rose-50 text-rose-600 rounded">Delete</button>
      </div>
    </div>
  )
}
