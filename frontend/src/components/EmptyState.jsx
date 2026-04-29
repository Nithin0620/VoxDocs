import React from 'react'

// Generic empty state used when lists are empty
export default function EmptyState({ title = 'No items', description = '' }) {
  return (
    <div className="p-8 text-center text-slate-500">
      <div className="text-xl font-medium">{title}</div>
      {description && <div className="mt-2">{description}</div>}
    </div>
  )
}
