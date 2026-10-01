import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { AxiosError } from 'axios';
import { ArrowRight, Check, Eye, EyeOff, ShieldCheck, UserRound, X } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { checkUsername } from '../services/api';

type AuthMode = 'login' | 'signup';
type Availability = 'idle' | 'checking' | 'available' | 'exists' | 'reserved' | 'invalid';

export const AuthPage = () => {
  const navigate = useNavigate();
  const { login, register, isLoading } = useAuth();
  const [mode, setMode] = useState<AuthMode>('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [availability, setAvailability] = useState<Availability>('idle');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (mode !== 'signup') return;
    const candidate = username.trim();
    if (!candidate) {
      setAvailability('idle');
      return;
    }
    if (!/^[a-zA-Z0-9_]{3,24}$/.test(candidate)) {
      setAvailability('invalid');
      return;
    }

    let current = true;
    setAvailability('checking');
    const timer = window.setTimeout(() => {
      checkUsername(candidate)
        .then(result => {
          if (!current) return;
          setAvailability(result.available ? 'available' : result.reason === 'RESERVED_USERNAME' ? 'reserved' : 'exists');
        })
        .catch(() => {
          if (current) setAvailability('idle');
        });
    }, 400);

    return () => {
      current = false;
      window.clearTimeout(timer);
    };
  }, [mode, username]);

  const setAuthMode = (nextMode: AuthMode) => {
    setMode(nextMode);
    setError('');
    setSuccess('');
    setPassword('');
    setConfirmPassword('');
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError('');
    setSuccess('');
    const normalizedUsername = username.trim();

    if (!normalizedUsername) return setError('Username is required.');
    if (!password) return setError('Password is required.');
    if (mode === 'signup') {
      if (!/^[a-zA-Z0-9_]{3,24}$/.test(normalizedUsername)) {
        return setError('Username must be 3-24 characters using letters, numbers, or underscores.');
      }
      if (password.length < 8 || new TextEncoder().encode(password).length > 72) {
        return setError('Password must be at least 8 characters.');
      }
      if (password !== confirmPassword) return setError('Passwords do not match.');
    }

    try {
      const user = mode === 'login'
        ? await login(normalizedUsername, password)
        : await register(normalizedUsername, password);
      if (mode === 'signup') setSuccess('Account created successfully.');
      window.setTimeout(() => navigate(user.role === 'ADMIN' ? '/admin/dashboard' : '/dashboard', { replace: true }), mode === 'signup' ? 450 : 0);
    } catch (submitError) {
      const responseMessage = (submitError as AxiosError<{ error?: string }>).response?.data?.error;
      setError(responseMessage || (mode === 'login' ? 'Incorrect username or password.' : 'Unable to create account. Please try again.'));
    }
  };

  const availabilityText: Record<Availability, string> = {
    idle: '',
    checking: 'Checking username...',
    available: 'Username is available',
    exists: 'Username already exists. Please try another username.',
    reserved: 'This username is reserved. Please try another username.',
    invalid: 'Username must be 3-24 characters using letters, numbers, or underscores.'
  };

  const availabilityColor = availability === 'available' ? 'text-emerald-700' :
    availability === 'checking' || availability === 'idle' ? 'text-slate-500' : 'text-rose-700';

  return (
    <main className="min-h-screen bg-[#f3f6fb] px-4 py-8 sm:px-8 lg:grid lg:grid-cols-[minmax(0,1fr)_minmax(420px,520px)] lg:gap-12 lg:px-14 lg:py-12">
      <section className="mx-auto flex w-full max-w-2xl flex-col justify-center py-8 lg:py-0">
        <div className="mb-8 flex items-center gap-3 lg:mb-12">
          <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-700 text-white shadow-lg shadow-blue-900/15">
            <ShieldCheck size={27} strokeWidth={2.4} />
          </span>
          <div>
            <p className="text-xl font-black tracking-tight text-slate-950">JobGuard</p>
            <p className="text-xs font-semibold uppercase tracking-[0.12em] text-blue-700">TrustGraph AI</p>
          </div>
        </div>
        <div className="max-w-xl">
          <p className="mb-4 inline-flex items-center gap-2 rounded-full border border-blue-200 bg-white px-3 py-1.5 text-xs font-bold text-blue-800">
            <span className="h-2 w-2 rounded-full bg-emerald-500" /> Evidence-led recruitment verification
          </p>
          <h1 className="text-4xl font-black leading-[1.08] text-slate-950 sm:text-5xl">Know the evidence before you trust the offer.</h1>
          <p className="mt-5 max-w-lg text-base leading-7 text-slate-600">Check recruitment notices against official records and suspicious patterns. Each result keeps the evidence and risk reasoning together.</p>
          <div className="mt-9 hidden items-center gap-4 border-t border-slate-200 pt-6 sm:flex">
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-100 text-emerald-800"><Check size={20} /></span>
            <div><p className="text-sm font-bold text-slate-900">A traceable analysis</p><p className="text-xs text-slate-500">Your investigations stay with your account.</p></div>
          </div>
        </div>
      </section>

      <section className="mx-auto w-full max-w-[520px] self-center">
        <div className="rounded-[22px] border border-slate-200 bg-white p-6 shadow-[0_24px_70px_-36px_rgba(15,23,42,.36)] sm:p-9">
          <div className="mb-7">
            <p className="text-xs font-extrabold uppercase tracking-[0.14em] text-blue-700">Secure access</p>
            <h2 className="mt-2 text-2xl font-extrabold text-slate-950">{mode === 'login' ? 'Welcome back' : 'Create your account'}</h2>
            <p className="mt-1 text-sm text-slate-500">{mode === 'login' ? 'Sign in to continue to your workspace.' : 'Choose a unique username to get started.'}</p>
          </div>

          <div className="mb-6 grid grid-cols-2 rounded-xl bg-slate-100 p-1" role="tablist" aria-label="Account access mode">
            {(['login', 'signup'] as const).map(tab => (
              <button key={tab} type="button" role="tab" aria-selected={mode === tab} onClick={() => setAuthMode(tab)}
                className={`rounded-lg py-2.5 text-sm font-bold transition-colors ${mode === tab ? 'bg-white text-slate-950 shadow-sm' : 'text-slate-500 hover:text-slate-800'}`}>
                {tab === 'login' ? 'Login' : 'Sign Up'}
              </button>
            ))}
          </div>

          <form className="space-y-4" onSubmit={handleSubmit}>
            <label className="block">
              <span className="mb-1.5 block text-sm font-bold text-slate-800">Username</span>
              <span className="relative block">
                <UserRound className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                <input autoComplete="username" value={username} onChange={event => setUsername(event.target.value)} required maxLength={24}
                  className="h-12 w-full rounded-xl border border-slate-300 bg-white pl-11 pr-4 text-sm text-slate-900 outline-none transition focus:border-blue-600 focus:ring-4 focus:ring-blue-100"
                  placeholder="Your username" />
              </span>
              {mode === 'signup' && availabilityText[availability] && (
                <span className={`mt-1.5 flex items-center gap-1.5 text-xs font-semibold ${availabilityColor}`}>
                  {availability === 'available' ? <Check size={14} /> : availability === 'exists' || availability === 'reserved' ? <X size={14} /> : null}
                  {availabilityText[availability]}
                </span>
              )}
            </label>

            <label className="block">
              <span className="mb-1.5 block text-sm font-bold text-slate-800">Password</span>
              <span className="relative block">
                <input type={showPassword ? 'text' : 'password'} autoComplete={mode === 'login' ? 'current-password' : 'new-password'} value={password}
                  onChange={event => setPassword(event.target.value)} required maxLength={72}
                  className="h-12 w-full rounded-xl border border-slate-300 bg-white px-4 pr-12 text-sm text-slate-900 outline-none transition focus:border-blue-600 focus:ring-4 focus:ring-blue-100"
                  placeholder="Enter your password" />
                <button type="button" onClick={() => setShowPassword(value => !value)} aria-label={showPassword ? 'Hide password' : 'Show password'}
                  className="absolute right-3 top-1/2 -translate-y-1/2 rounded-md p-1 text-slate-500 hover:bg-slate-100 hover:text-slate-900">
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </span>
            </label>

            {mode === 'signup' && (
              <label className="block">
                <span className="mb-1.5 block text-sm font-bold text-slate-800">Confirm password</span>
                <input type={showPassword ? 'text' : 'password'} autoComplete="new-password" value={confirmPassword} onChange={event => setConfirmPassword(event.target.value)} required maxLength={72}
                  className="h-12 w-full rounded-xl border border-slate-300 bg-white px-4 text-sm text-slate-900 outline-none transition focus:border-blue-600 focus:ring-4 focus:ring-blue-100"
                  placeholder="Re-enter your password" />
              </label>
            )}

            {error && <p role="alert" className="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2.5 text-sm font-medium text-rose-800">{error}</p>}
            {success && <p role="status" className="rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2.5 text-sm font-semibold text-emerald-800">✓ {success}</p>}

            <button type="submit" disabled={isLoading} className="group flex h-12 w-full items-center justify-center gap-2 rounded-xl bg-blue-700 px-4 text-sm font-extrabold text-white shadow-lg shadow-blue-900/15 transition hover:bg-blue-800 focus:outline-none focus:ring-4 focus:ring-blue-200 disabled:cursor-wait disabled:opacity-70">
              {isLoading ? (mode === 'login' ? 'Logging in...' : 'Creating account...') : (mode === 'login' ? 'Login' : 'Create Account')}
              {!isLoading && <ArrowRight className="transition-transform group-hover:translate-x-0.5" size={17} />}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-slate-600">
            {mode === 'login' ? "Don't have an account? " : 'Already have an account? '}
            <button type="button" onClick={() => setAuthMode(mode === 'login' ? 'signup' : 'login')} className="font-extrabold text-blue-700 hover:text-blue-900">
              {mode === 'login' ? 'Sign Up' : 'Login'}
            </button>
          </p>
        </div>
        <p className="mt-4 text-center text-xs text-slate-500">Access is protected by a secure, server-verified session.</p>
      </section>
    </main>
  );
};