'use client';

import { useState } from 'react';
import { GoogleLogin, CredentialResponse } from '@react-oauth/google';
import { saveSession, useSession } from '../lib/session';

export default function LoginPage() {
  const { token, user } = useSession();
  const [loginError, setLoginError] = useState<string | null>(null);
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:5000';
  const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;

  const handleSuccess = async (credentialResponse: CredentialResponse) => {
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

      if (response.ok) {
        saveSession(data.token, data.user);
      } else {
        setLoginError('Não foi possível autenticar com Google.');
      }
    } catch {
      setLoginError('Não foi possível conectar ao servidor.');
    }
  };

  const handleError = () => {
    setLoginError('O login com Google falhou. Tente novamente.');
  };

  return (
    <div style={{ display: 'grid', placeItems: 'center', minHeight: '100vh' }}>
      {token && user ? (
        <div style={{ textAlign: 'center' }}>
          <h1>Você está LOGADO!</h1>
          {user.picture && <img
            src={user.picture}
            alt={user.name ?? ''}
            style={{ borderRadius: '50%', width: '80px', height: '80px' }}
          />}
          <h2>Bem-vindo(a), {user.name}!</h2>
          <p>{user.email}</p>

        </div>
      ) : (
        <div style={{ textAlign: 'center' }}>
          <h2>Iniciar Sessão</h2>
          {loginError && <p role="alert">{loginError}</p>}
          {clientId ? (
            <GoogleLogin
              onSuccess={handleSuccess}
              onError={handleError}
            />
          ) : (
            <p>Login com Google indisponível: configure NEXT_PUBLIC_GOOGLE_CLIENT_ID.</p>
          )}
        </div>
      )}
    </div>
  );
}