'use client';

import { useEffect, useState } from 'react';
import { GoogleLogin, CredentialResponse } from '@react-oauth/google';
import Link from 'next/link';

interface UserProfile {
  email: string;
  name: string;
  picture: string;
}

export default function LoginPage() {
  const [user, setUser] = useState<UserProfile | null>(null);
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:5000';
  console.log('API Base URL:', apiBaseUrl);

  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');

    if (savedToken && savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
    }
  }, []);

  const handleSuccess = async (credentialResponse: CredentialResponse) => {
    console.log('Google response:', {
    hasCredential: !!credentialResponse.credential,
    credentialLength: credentialResponse.credential?.length,
  });
    try {
      const response = await fetch(`${apiBaseUrl}/api/auth/google`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          credential: credentialResponse.credential,
        }),
      });

      const data = await response.json();

      console.log('Authentication API response:', {
      status: response.status,
      ok: response.ok,
      data,
    });
    
      if (response.ok) {
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        setUser(data.user);
      } else {
        console.error('Authentication failed:', {
    status: response.status,
    statusText: response.statusText,
    data,
  });
      }
    } catch (error) {
      console.error('Network or server error:', error);
    }
  };

  const handleError = () => {
    console.error('Google Sign-In failed');
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  return (
    <div style={{ display: 'grid', placeItems: 'center', minHeight: '100vh' }}>
      <Link href="/" style={{ position: 'absolute', top: '20px', left: '20px', textDecoration: 'none', color: '#1a202c' }}>
        &larr; Voltar à Página Inicial
      </Link>

      {user ? (
        <div style={{ textAlign: 'center' }}>
          <h1>Você está LOGADO!</h1>
          <img
            src={user.picture}
            alt={user.name}
            style={{ borderRadius: '50%', width: '80px', height: '80px' }}
          />
          <h2>Bem-vindo(a), {user.name}!</h2>
          <p>{user.email}</p>

          <button
            onClick={handleLogout}
            style={{
              padding: '8px 16px',
              backgroundColor: '#e53e3e',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              marginTop: '12px'
            }}
          >
            Terminar Sessão
          </button>
        </div>
      ) : (
        <div style={{ textAlign: 'center' }}>
          <h2>Iniciar Sessão</h2>
          <GoogleLogin
            onSuccess={handleSuccess}
            onError={handleError}
          />
        </div>
      )}
    </div>
  );
}