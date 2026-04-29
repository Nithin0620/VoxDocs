import React from 'react'
import { useAuth } from '../context/AuthContext'

const toastStyles = {
  success: 'border-emerald-200 bg-emerald-50 text-emerald-900',
  info: 'border-sky-200 bg-sky-50 text-sky-900',
  error: 'border-rose-200 bg-rose-50 text-rose-900',
  warning: 'border-amber-200 bg-amber-50 text-amber-900',
}

export default function ToastStack() {
  const { toasts, removeToast } = useAuth()

  return (
    <div className="pointer-events-none fixed right-4 top-4 z-50 flex w-full max-w-sm flex-col gap-3 px-4 sm:px-0">
      {toasts.map(toast => (
        <div
          key={toast.id}
          className={`pointer-events-auto rounded-2xl border px-4 py-3 shadow-[0_18px_45px_rgba(15,23,42,0.12)] backdrop-blur-xl transition-all duration-300 ${toastStyles[toast.type] || toastStyles.info}`}
        >
          <div className="flex items-start justify-between gap-3">
            <div>
              <div className="text-sm font-semibold">{toast.title}</div>
              <div className="mt-1 text-sm opacity-90">{toast.message}</div>
            </div>
            <button
              type="button"
              onClick={() => removeToast(toast.id)}
              className="rounded-full px-2 py-1 text-sm font-semibold opacity-70 transition hover:bg-white/70 hover:opacity-100"
            >
              ×
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}