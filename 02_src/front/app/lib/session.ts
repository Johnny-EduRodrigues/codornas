'use client';

import { useSyncExternalStore } from 'react';

export interface SessionUser {
  name?: string;
  email?: string;
  picture?: string;
  super_admin?: boolean;
}

interface Session {
  token: string | null;
  user: SessionUser | null;
}

const sessionChangeEvent = 'sirah-session-change';

function getSnapshot(): string {
  if (typeof window === 'undefined') return '';
  return JSON.stringify({
    token: localStorage.getItem('token'),
    user: localStorage.getItem('user'),
  });
}

function subscribe(onChange: () => void) {
  window.addEventListener('storage', onChange);
  window.addEventListener(sessionChangeEvent, onChange);
  return () => {
    window.removeEventListener('storage', onChange);
    window.removeEventListener(sessionChangeEvent, onChange);
  };
}

export function useSession(): Session {
  const snapshot = useSyncExternalStore(subscribe, getSnapshot, () => '');
  if (!snapshot) return { token: null, user: null };

  try {
    const stored = JSON.parse(snapshot) as {
      token: string | null;
      user: string | null;
    };
    const user = stored.user ? JSON.parse(stored.user) as SessionUser : null;
    return { token: stored.token, user };
  } catch {
    return { token: null, user: null };
  }
}

export function saveSession(token: string, user: SessionUser) {
  localStorage.setItem('token', token);
  localStorage.setItem('user', JSON.stringify(user));
  window.dispatchEvent(new Event(sessionChangeEvent));
}

export function clearSession() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  window.dispatchEvent(new Event(sessionChangeEvent));
}
