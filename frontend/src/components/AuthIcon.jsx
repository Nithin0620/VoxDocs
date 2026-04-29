import React from 'react'

export function MailIcon({ className = 'h-5 w-5' }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className={className}>
      <path d="M4 6h16v12H4z" />
      <path d="m4 7 8 6 8-6" />
    </svg>
  )
}

export function LockIcon({ className = 'h-5 w-5' }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className={className}>
      <rect x="5" y="10" width="14" height="10" rx="2" />
      <path d="M8 10V7a4 4 0 1 1 8 0v3" />
    </svg>
  )
}

export function UserIcon({ className = 'h-5 w-5' }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className={className}>
      <path d="M20 21a8 8 0 0 0-16 0" />
      <circle cx="12" cy="8" r="4" />
    </svg>
  )
}

export function EyeIcon({ className = 'h-5 w-5' }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className={className}>
      <path d="M2 12s3.5-6.5 10-6.5S22 12 22 12s-3.5 6.5-10 6.5S2 12 2 12Z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  )
}

export function EyeOffIcon({ className = 'h-5 w-5' }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className={className}>
      <path d="M3 3l18 18" />
      <path d="M10.5 10.6a3 3 0 0 0 4 4" />
      <path d="M6.5 6.6C4.2 8.3 2.7 12 2.7 12s3.5 6.5 9.3 6.5c1.2 0 2.3-.2 3.3-.5" />
      <path d="M14.3 5.4c4.7.9 7 6.6 7 6.6s-.8 1.6-2.2 3.1" />
    </svg>
  )
}

export function GoogleIcon({ className = 'h-5 w-5' }) {
  return (
    <svg viewBox="0 0 24 24" className={className} aria-hidden="true">
      <path fill="#EA4335" d="M12 10.2v3.9h5.5c-.2 1.4-1.7 4.2-5.5 4.2-3.3 0-6-2.7-6-6s2.7-6 6-6c1.9 0 3.2.8 3.9 1.5l2.7-2.6C16.9 3.6 14.7 2.5 12 2.5 6.8 2.5 2.5 6.8 2.5 12S6.8 21.5 12 21.5c6 0 9.9-4.2 9.9-10.1 0-.7-.1-1.2-.2-1.7H12Z" />
      <path fill="#FBBC05" d="M3.6 7.8 6.7 10c.8-2.2 3-3.9 5.3-3.9 1.9 0 3.2.8 3.9 1.5l2.7-2.6C16.9 3.6 14.7 2.5 12 2.5 8.2 2.5 5 4.8 3.6 7.8Z" opacity=".95" />
      <path fill="#34A853" d="M12 21.5c2.6 0 4.8-.9 6.5-2.5l-3-2.5c-.8.6-1.9 1-3.5 1-3.3 0-6-2.7-6-6 0-.8.2-1.6.5-2.3L3.6 7.8A9.5 9.5 0 0 0 2.5 12c0 5.2 4.3 9.5 9.5 9.5Z" opacity=".95" />
      <path fill="#4285F4" d="M21.8 11.1H12v3.9h5.5c-.5 1.5-1.8 2.8-3.7 3.5l3 2.5c1.7-1.6 2.7-4 2.7-7.2 0-.7-.1-1.3-.2-1.7Z" opacity=".95" />
    </svg>
  )
}