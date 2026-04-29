import React from 'react'
import { useAuth } from '../context/AuthContext'

// Top navigation bar (mobile + small screens)
export default function Navbar() {
  const { user, signOut } = useAuth()

  return (
    <header className="sticky top-0 z-20 border-b border-white/60 bg-white/60 backdrop-blur-xl md:pl-64">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
        <div>
          <div className="text-sm font-semibold uppercase tracking-[0.24em] text-sky-600">VoxDocs</div>
          <div className="text-sm text-slate-500">AI Document Assistant</div>
        </div>
        <div className="flex items-center gap-3">
          {user ? (
            <div className="hidden items-center gap-3 rounded-full border border-white/70 bg-white/80 px-3 py-2 shadow-sm sm:flex">
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-sky-400 to-fuchsia-400 text-sm font-semibold text-white">
                {user.name?.slice(0, 1)?.toUpperCase() || 'U'}
              </div>
              <div className="leading-tight">
                <div className="text-sm font-semibold text-slate-900">{user.name}</div>
                <div className="text-xs text-slate-500">{user.provider}</div>
              </div>
            </div>
          ) : null}
          <button
            type="button"
            onClick={signOut}
            className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:-translate-y-0.5 hover:border-slate-300 hover:text-slate-900"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  )
}
