import React from 'react'

// Displays a user-friendly error message
export default function ErrorMessage({ error }) {
  return (
    <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-rose-800 shadow-sm">
      <strong className="block text-sm uppercase tracking-[0.2em]">Error</strong>
      <div className="mt-1 text-sm">{String(error)}</div>
    </div>
  )
}
