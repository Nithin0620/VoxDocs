import React from 'react'
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import Navbar from './Navbar'

export default function AppLayout() {
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,rgba(125,211,252,0.22),transparent_32%),radial-gradient(circle_at_top_right,rgba(244,114,182,0.18),transparent_28%),linear-gradient(180deg,#f8fbff_0%,#eef4ff_100%)] text-slate-900">
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex min-h-screen flex-1 flex-col md:pl-64">
          <Navbar />
          <main className="flex-1 px-4 py-6 sm:px-6 lg:px-8">
            <div className="mx-auto w-full max-w-7xl">
              <Outlet />
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}