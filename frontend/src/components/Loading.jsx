import React from 'react'

// Simple loading indicator component
export default function Loading({ message = 'Loading...' }) {
  return (
    <div className="flex min-h-[50vh] items-center justify-center p-6 text-center text-slate-600">
      <div className="rounded-[1.5rem] border border-white/70 bg-white/75 px-6 py-5 shadow-[0_20px_50px_rgba(76,97,145,0.1)] backdrop-blur-xl">
        <div className="mb-3 text-sm font-medium">{message}</div>
        <div className="mx-auto inline-block h-10 w-10 animate-spin rounded-full border-4 border-sky-100 border-t-sky-500" />
      </div>
    </div>
  )
}
