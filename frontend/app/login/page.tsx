'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useLearner } from '../../context/LearnerContext';
import { Compass, AlertCircle, Loader2, ArrowRight, X, Info } from 'lucide-react';

declare global {
  interface Window {
    google?: any;
  }
}

export default function LoginPage() {
  const router = useRouter();
  const { isAuthenticated, isAuthLoading, login, googleLogin } = useLearner();

  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [googleLoading, setGoogleLoading] = useState<boolean>(false);
  const [loginError, setLoginError] = useState<string | null>(null);
  const [forgotPasswordOpen, setForgotPasswordOpen] = useState<boolean>(false);
  const [gisReady, setGisReady] = useState<boolean>(false);

  const googleButtonContainerRef = useRef<HTMLDivElement>(null);

  // If already authenticated, redirect to dashboard immediately
  useEffect(() => {
    if (!isAuthLoading && isAuthenticated) {
      router.replace('/');
    }
  }, [isAuthenticated, isAuthLoading, router]);

  // Handle Google OAuth Credential response from GIS
  const handleGoogleCredentialResponse = useCallback(
    async (response: { credential?: string; select_by?: string }) => {
      if (!response || !response.credential) {
        setLoginError('Google authentication was cancelled or returned an empty response.');
        return;
      }
      setLoginError(null);
      setGoogleLoading(true);
      try {
        const authRes = await googleLogin({ credential: response.credential });
        if (authRes.needs_onboarding) {
          router.push('/onboarding');
        } else {
          router.push('/');
        }
      } catch (err: unknown) {
        const msg =
          err instanceof Error
            ? err.message
            : 'Unable to complete Google sign-in. Please try again or use email.';
        setLoginError(msg);
      } finally {
        setGoogleLoading(false);
      }
    },
    [googleLogin, router]
  );

  // Load Google Identity Services (GIS) client script
  useEffect(() => {
    const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;

    // Helper to initialize GIS once script is loaded
    const initializeGis = () => {
      if (typeof window !== 'undefined' && window.google?.accounts?.id) {
        setGisReady(true);
        if (clientId) {
          try {
            window.google.accounts.id.initialize({
              client_id: clientId,
              callback: handleGoogleCredentialResponse,
              auto_select: false,
              cancel_on_tap_outside: true,
            });

            // If container exists, optionally render standard GIS button
            if (googleButtonContainerRef.current) {
              window.google.accounts.id.renderButton(
                googleButtonContainerRef.current,
                {
                  theme: 'outline',
                  size: 'large',
                  text: 'continue_with',
                  shape: 'rectangular',
                  width: '100%',
                  logo_alignment: 'left',
                }
              );
            }
          } catch (e) {
            console.error('Error initializing Google Identity Services:', e);
          }
        }
      }
    };

    // Check if script already loaded
    if (typeof window !== 'undefined' && window.google?.accounts?.id) {
      initializeGis();
      return;
    }

    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    script.onload = initializeGis;
    document.body.appendChild(script);

    return () => {
      // Keep script in body for page lifecycle
    };
  }, [handleGoogleCredentialResponse]);

  // Trigger Google Sign-In on button click
  const handleGoogleClick = () => {
    setLoginError(null);
    const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;

    if (!clientId) {
      setLoginError(
        'Google Client ID is not configured. Please set NEXT_PUBLIC_GOOGLE_CLIENT_ID in your environment (.env).'
      );
      return;
    }

    if (typeof window !== 'undefined' && window.google?.accounts?.id) {
      setGoogleLoading(true);
      try {
        window.google.accounts.id.prompt((notification: any) => {
          if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
            setGoogleLoading(false);
          }
        });
      } catch (err) {
        setGoogleLoading(false);
        setLoginError('Could not launch Google authentication prompt.');
      }
    } else {
      setLoginError('Google services are still initializing. Please wait a moment and try again.');
    }
  };

  // Standard Email/Password login
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginError(null);

    const cleanEmail = email.trim();
    if (!cleanEmail || !cleanEmail.includes('@')) {
      setLoginError('Please enter a valid email address.');
      return;
    }

    if (!password) {
      setLoginError('Please enter your password.');
      return;
    }

    try {
      setSubmitting(true);
      await login(cleanEmail, password);
      router.push('/');
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : 'Invalid email or password. Please verify your credentials and try again.';
      setLoginError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  if (isAuthLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
        <div className="flex items-center gap-2.5 text-xs font-semibold text-slate-600">
          <Loader2 className="w-4 h-4 text-blue-600 animate-spin" />
          <span>Verifying session…</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-between p-4 sm:p-6 lg:p-8 antialiased selection:bg-blue-100 selection:text-blue-900">
      {/* Top Brand Anchor */}
      <header className="max-w-md w-full mx-auto flex items-center justify-between pt-2 pb-6">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-xs">
            <Compass className="w-4.5 h-4.5 text-white" />
          </div>
          <span className="font-bold text-slate-900 text-base tracking-tight">
            SkillPath AI
          </span>
        </div>
      </header>

      {/* Main Authentication Container */}
      <main className="max-w-md w-full mx-auto my-auto">
        <div className="bg-white border border-slate-200 rounded-xl shadow-xs p-6 sm:p-8">
          {/* Header */}
          <div className="text-center mb-6">
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900">
              Welcome to SkillPath AI
            </h1>
            <p className="text-xs sm:text-sm text-slate-600 mt-1.5 font-normal">
              Build the skills your career actually needs.
            </p>
          </div>

          {/* Error Banner */}
          {loginError && (
            <div className="mb-5 p-3.5 bg-rose-50 border border-rose-200 rounded-lg flex items-start gap-2.5 text-xs text-rose-800 animate-in fade-in duration-150">
              <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
              <div className="flex-1">
                <span>{loginError}</span>
              </div>
              <button
                type="button"
                onClick={() => setLoginError(null)}
                className="text-rose-400 hover:text-rose-600 p-0.5"
                aria-label="Dismiss error"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          )}

          {/* 1. Continue with Google Button */}
          <div className="space-y-3">
            <button
              id="google-signin-button"
              type="button"
              onClick={handleGoogleClick}
              disabled={googleLoading || submitting}
              className="w-full flex items-center justify-center gap-3 px-4 py-2.5 bg-white hover:bg-slate-50 text-slate-700 text-sm font-medium border border-slate-300 hover:border-slate-400 rounded-lg shadow-2xs transition-all duration-150 disabled:opacity-60 cursor-pointer min-h-[44px]"
            >
              {googleLoading ? (
                <>
                  <Loader2 className="w-4 h-4 text-slate-600 animate-spin" />
                  <span>Signing you in…</span>
                </>
              ) : (
                <>
                  {/* Official Google G Multi-Color SVG Icon */}
                  <svg
                    className="w-4.5 h-4.5 shrink-0"
                    viewBox="0 0 24 24"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                      fill="#4285F4"
                    />
                    <path
                      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                      fill="#34A853"
                    />
                    <path
                      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                      fill="#FBBC05"
                    />
                    <path
                      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
                      fill="#EA4335"
                    />
                  </svg>
                  <span>Continue with Google</span>
                </>
              )}
            </button>

            {/* Hidden container for GIS button rendering if active */}
            <div ref={googleButtonContainerRef} className="hidden" />
          </div>

          {/* Divider */}
          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-200" />
            </div>
            <div className="relative flex justify-center text-xs">
              <span className="bg-white px-3 text-slate-400 font-medium uppercase tracking-wider">
                or
              </span>
            </div>
          </div>

          {/* 2. Email & Password Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label
                htmlFor="email"
                className="block text-xs font-semibold text-slate-700 mb-1"
              >
                Email
              </label>
              <input
                id="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@example.com"
                className="w-full bg-white border border-slate-300 rounded-lg px-3.5 py-2.5 text-sm font-normal text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent transition min-h-[44px]"
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-1">
                <label
                  htmlFor="password"
                  className="block text-xs font-semibold text-slate-700"
                >
                  Password
                </label>
                <button
                  type="button"
                  onClick={() => setForgotPasswordOpen(true)}
                  className="text-xs font-medium text-blue-600 hover:text-blue-700 transition cursor-pointer"
                >
                  Forgot password?
                </button>
              </div>
              <input
                id="password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-white border border-slate-300 rounded-lg px-3.5 py-2.5 text-sm font-normal text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent transition min-h-[44px]"
              />
            </div>

            <div className="pt-2">
              <button
                id="login-submit-button"
                type="submit"
                disabled={submitting || googleLoading}
                className="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm rounded-lg shadow-xs transition-colors disabled:opacity-60 min-h-[44px] cursor-pointer"
              >
                {submitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Signing in…</span>
                  </>
                ) : (
                  <>
                    <span>Sign In</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>
          </form>

          {/* 3. Create Account Link */}
          <div className="mt-6 pt-5 text-center border-t border-slate-100">
            <p className="text-xs text-slate-600">
              Don&apos;t have an account?{' '}
              <Link
                href="/onboarding"
                className="font-semibold text-blue-600 hover:text-blue-700 transition inline-flex items-center gap-0.5 ml-1"
              >
                Create account
              </Link>
            </p>
          </div>
        </div>
      </main>

      {/* Forgot Password Modal */}
      {forgotPasswordOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs">
          <div className="bg-white rounded-xl border border-slate-200 shadow-xl max-w-sm w-full p-6 space-y-4 animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-slate-900 font-bold text-sm">
                <Info className="w-4.5 h-4.5 text-blue-600" />
                <span>Password Recovery</span>
              </div>
              <button
                onClick={() => setForgotPasswordOpen(false)}
                className="text-slate-400 hover:text-slate-600 p-1"
                aria-label="Close dialog"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              Automated self-service password reset is managed through workspace administration.
              If you need your credentials reset, please contact your administrator or email{' '}
              <span className="font-semibold text-slate-800">support@skillpath.ai</span> with your
              registered email address.
            </p>
            <div className="pt-2">
              <button
                type="button"
                onClick={() => setForgotPasswordOpen(false)}
                className="w-full py-2 px-3 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg transition"
              >
                Got it
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="max-w-md w-full mx-auto text-center text-xs text-slate-400 pt-6 pb-2">
        &copy; 2026 SkillPath AI
      </footer>
    </div>
  );
}
