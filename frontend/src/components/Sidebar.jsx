import React from 'react'
import { NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

// Sidebar navigation links
export default function Sidebar() {
  const { user } = useAuth()

  return (
    <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-white/60 bg-white/65 backdrop-blur-xl md:flex md:flex-col">
      <div className="flex-1 p-5">
        <div className="rounded-[1.5rem] border border-white/70 bg-gradient-to-br from-sky-100 via-white to-fuchsia-100 p-4 shadow-[0_18px_45px_rgba(76,97,145,0.1)]">
          <div className="text-sm font-semibold uppercase tracking-[0.24em] text-sky-600">VoxDocs</div>
          <div className="mt-2 text-lg font-semibold text-slate-900">Document AI Workspace</div>
          <div className="mt-3 text-sm text-slate-600">Secure access with Google and local accounts.</div>
        </div>

        <nav className="mt-6 space-y-2">
          {[
            ['/', 'Home'],
            ['/upload', 'Upload'],
            ['/documents', 'Documents'],
            ['/ask', 'Ask'],
            ['/voice', 'Voice'],
            ['/sessions', 'Sessions'],
          ].map(([path, label]) => (
            <NavLink
              key={path}
              to={path}
              className={({ isActive }) =>
                `block rounded-2xl px-4 py-3 text-sm font-medium transition ${isActive ? 'bg-slate-900 text-white shadow-lg' : 'text-slate-600 hover:bg-white/80 hover:text-slate-900'}`
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>
      </div>

      {user ? (
        <div className="border-t border-white/70 p-5">
          <div className="rounded-[1.5rem] border border-white/70 bg-white/80 p-4 shadow-[0_18px_45px_rgba(76,97,145,0.08)]">
            <div className="text-sm font-semibold text-slate-900">{user.name}</div>
            <div className="mt-1 text-xs text-slate-500">{user.email}</div>
          </div>
        </div>
      ) : null}
    </aside>
  )
}
