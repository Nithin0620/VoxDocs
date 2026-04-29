import React, { useEffect, useMemo, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { EyeIcon, EyeOffIcon, GoogleIcon, LockIcon, MailIcon, UserIcon } from '../components/AuthIcon'
import { useAuth } from '../context/AuthContext'

function AuthField({ icon, label, type = 'text', value, onChange, placeholder, autoComplete, error, rightSlot }) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm font-semibold text-slate-700">{label}</span>
      <div className={`flex items-center gap-3 rounded-2xl border bg-white/80 px-4 py-3 shadow-[0_12px_35px_rgba(76,97,145,0.08)] transition focus-within:border-sky-300 focus-within:ring-4 focus-within:ring-sky-100 ${error ? 'border-rose-300' : 'border-white/70'}`}>
        <span className="text-slate-400">{icon}</span>
        <input
          type={type}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          autoComplete={autoComplete}
          className="w-full bg-transparent text-[15px] outline-none placeholder:text-slate-400"
        />
        {rightSlot}
      </div>
      {error ? <div className="mt-1 text-sm text-rose-600">{error}</div> : null}
    </label>
  )
}

export default function AuthPage({ mode = 'login' }) {
  const isSignup = mode === 'signup'
  const { signIn, signUp, startGoogleLogin, pushToast, isAuthenticated, initializing } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [queryErrorShown, setQueryErrorShown] = useState(false)
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [form, setForm] = useState({ name: '', email: '', password: '', confirmPassword: '' })
  const [errors, setErrors] = useState({})

  const fromPath = useMemo(() => location.state?.from?.pathname || '/', [location.state])

  useEffect(() => {
    if (initializing) return
    if (isAuthenticated) {
      navigate('/', { replace: true })
      return
    }
    if (queryErrorShown) return
    const params = new URLSearchParams(location.search)
    const error = params.get('error')
    if (error) {
      pushToast({ type: 'error', title: 'Authentication error', message: error })
      setQueryErrorShown(true)
      navigate(location.pathname, { replace: true })
    }
  }, [initializing, isAuthenticated, location.pathname, location.search, navigate, pushToast, queryErrorShown])

  function updateField(field, value) {
    setForm(previous => ({ ...previous, [field]: value }))
  }

  function validate() {
    const nextErrors = {}

    if (isSignup && form.name.trim().length < 2) {
      nextErrors.name = 'Please enter your full name.'
    }

    if (!form.email.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
      nextErrors.email = 'Enter a valid email address.'
    }

    if (form.password.length < 8) {
      nextErrors.password = 'Password must be at least 8 characters.'
    }

    if (isSignup && form.password !== form.confirmPassword) {
      nextErrors.confirmPassword = 'Passwords do not match.'
    }

    setErrors(nextErrors)
    return Object.keys(nextErrors).length === 0
  }

  async function handleSubmit(event) {
    event.preventDefault()
    if (!validate()) return

    setLoading(true)
    try {
      if (isSignup) {
        await signUp({ name: form.name, email: form.email, password: form.password })
      } else {
        await signIn({ email: form.email, password: form.password })
      }
      pushToast({
        type: 'success',
        title: isSignup ? 'Account ready' : 'Signed in',
        message: isSignup ? 'You can start using VoxDocs now.' : 'Welcome back to VoxDocs.',
      })
      navigate(fromPath, { replace: true })
    } catch (error) {
      pushToast({ type: 'error', title: 'Authentication failed', message: error.message })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="relative min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top_left,rgba(96,165,250,0.3),transparent_30%),radial-gradient(circle_at_top_right,rgba(244,114,182,0.24),transparent_28%),linear-gradient(180deg,#f8fbff_0%,#eef4ff_100%)] px-4 py-6 text-slate-900 sm:px-6 lg:px-8">
      <div className="absolute left-[-6rem] top-20 h-56 w-56 rounded-full bg-sky-200/50 blur-3xl" />
      <div className="absolute right-[-4rem] top-40 h-72 w-72 rounded-full bg-pink-200/50 blur-3xl" />
      <div className="mx-auto grid min-h-[calc(100vh-3rem)] w-full max-w-7xl grid-cols-1 items-stretch gap-8 lg:grid-cols-[1.05fr_0.95fr]">
        <section className="relative hidden overflow-hidden rounded-[2rem] border border-white/50 bg-white/40 p-8 shadow-[0_30px_90px_rgba(76,97,145,0.14)] backdrop-blur-xl lg:flex lg:flex-col lg:justify-between">
          <div>
            <div className="inline-flex items-center rounded-full border border-sky-200/70 bg-white/70 px-4 py-2 text-sm font-semibold text-sky-700 shadow-sm">
              VoxDocs secure access
            </div>
            <h1 className="mt-8 max-w-xl text-5xl font-semibold tracking-tight text-slate-900">
              Keep every document conversation in one private workspace.
            </h1>
            <p className="mt-5 max-w-lg text-lg leading-8 text-slate-600">
              Sign in with email or Google, keep your sessions locked behind a JWT cookie, and jump straight into your document knowledge base.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4 text-sm">
            {[
              ['Secure auth', 'JWT cookie + protected routes'],
              ['Google ready', 'OAuth with automatic account creation'],
              ['Responsive', 'Built for mobile and desktop'],
              ['Reusable', 'Shared auth context and toasts'],
            ].map(([title, description]) => (
              <div key={title} className="rounded-2xl border border-white/70 bg-white/75 p-4 shadow-[0_12px_30px_rgba(76,97,145,0.08)]">
                <div className="font-semibold text-slate-900">{title}</div>
                <div className="mt-1 text-slate-600">{description}</div>
              </div>
            ))}
          </div>
        </section>

        <section className="flex items-center justify-center">
          <div className="w-full max-w-xl rounded-[2rem] border border-white/70 bg-white/75 p-6 shadow-[0_30px_90px_rgba(76,97,145,0.14)] backdrop-blur-xl sm:p-8">
            <div className="mb-8 flex items-center justify-between">
              <div>
                <div className="text-sm font-semibold uppercase tracking-[0.28em] text-sky-600">VoxDocs</div>
                <h2 className="mt-2 text-3xl font-semibold tracking-tight text-slate-900">
                  {isSignup ? 'Create your account' : 'Welcome back'}
                </h2>
                <p className="mt-2 text-sm text-slate-600">
                  {isSignup
                    ? 'Create an account to keep your document assistant personal.'
                    : 'Sign in to continue your document sessions.'}
                </p>
              </div>
              <div className="hidden h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-sky-400 to-fuchsia-400 text-white shadow-lg sm:flex">
                <svg viewBox="0 0 24 24" className="h-7 w-7" fill="none" stroke="currentColor" strokeWidth="1.8">
                  <path d="M7 4h8l4 4v12H7z" />
                  <path d="M9 12h6" />
                  <path d="M9 16h6" />
                </svg>
              </div>
            </div>

            <button
              type="button"
              onClick={startGoogleLogin}
              className="group flex w-full items-center justify-center gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-3.5 text-[15px] font-semibold text-slate-700 shadow-[0_12px_30px_rgba(76,97,145,0.08)] transition duration-200 hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-[0_16px_40px_rgba(76,97,145,0.12)]"
            >
              <GoogleIcon className="h-5 w-5 transition-transform duration-200 group-hover:scale-105" />
              Continue with Google
            </button>

            <div className="my-6 flex items-center gap-4 text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">
              <span className="h-px flex-1 bg-slate-200" />
              or use email
              <span className="h-px flex-1 bg-slate-200" />
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              {isSignup ? (
                <AuthField
                  icon={<UserIcon />}
                  label="Full name"
                  value={form.name}
                  onChange={event => updateField('name', event.target.value)}
                  placeholder="Jordan Miles"
                  autoComplete="name"
                  error={errors.name}
                />
              ) : null}

              <AuthField
                icon={<MailIcon />}
                label="Email address"
                type="email"
                value={form.email}
                onChange={event => updateField('email', event.target.value)}
                placeholder="you@example.com"
                autoComplete="email"
                error={errors.email}
              />

              <AuthField
                icon={<LockIcon />}
                label="Password"
                type={showPassword ? 'text' : 'password'}
                value={form.password}
                onChange={event => updateField('password', event.target.value)}
                placeholder="Enter your password"
                autoComplete={isSignup ? 'new-password' : 'current-password'}
                error={errors.password}
                rightSlot={
                  <button
                    type="button"
                    onClick={() => setShowPassword(previous => !previous)}
                    className="rounded-full p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-700"
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? <EyeOffIcon /> : <EyeIcon />}
                  </button>
                }
              />

              {isSignup ? (
                <AuthField
                  icon={<LockIcon />}
                  label="Confirm password"
                  type={showPassword ? 'text' : 'password'}
                  value={form.confirmPassword}
                  onChange={event => updateField('confirmPassword', event.target.value)}
                  placeholder="Repeat your password"
                  autoComplete="new-password"
                  error={errors.confirmPassword}
                />
              ) : null}

              <button
                type="submit"
                disabled={loading}
                className="flex w-full items-center justify-center rounded-2xl bg-gradient-to-r from-sky-500 via-indigo-500 to-fuchsia-500 px-4 py-3.5 text-[15px] font-semibold text-white shadow-[0_18px_40px_rgba(79,70,229,0.24)] transition duration-200 hover:-translate-y-0.5 hover:shadow-[0_22px_50px_rgba(79,70,229,0.28)] disabled:cursor-not-allowed disabled:opacity-70"
              >
                {loading ? 'Please wait...' : isSignup ? 'Create account' : 'Sign in'}
              </button>
            </form>

            <div className="mt-6 text-center text-sm text-slate-600">
              {isSignup ? 'Already have an account?' : "Need an account?"}{' '}
              <Link
                to={isSignup ? '/login' : '/signup'}
                className="font-semibold text-sky-700 transition hover:text-sky-900"
              >
                {isSignup ? 'Sign in' : 'Create one'}
              </Link>
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}