'use client';

import Link from 'next/dist/client/link';
import { useEffect, useState } from 'react';

interface UserProfile {
  email: string;
  name: string;
  picture: string;
}

export default function Home() {
  const [user, setUser] = useState<UserProfile | null>(null);

  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch {
        localStorage.removeItem('user');
      }
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  return (
    <div className="flex flex-col flex-1 items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <main className="flex flex-1 w-full max-w-3xl flex-col items-center justify-between py-32 px-16 bg-white dark:bg-black sm:items-start gap-6">
        
        {user ? (
          <div className="flex flex-col items-center gap-3 text-center">
            <img src={user.picture} alt={user.name} className="h-16 w-16 rounded-full" />
            <h1 className="text-2xl font-semibold">Bem-vindo(a), {user.name}</h1>
            <p className="text-sm text-gray-600">{user.email}</p>

            Você JÁ está logado, mas caso queira ir para a página de login:
            <Link href="/login" className="text-blue-500 hover:underline">
              Login
            </Link>

            Outra opção interessante é fazer o LOGOUT!

            <button
              onClick={handleLogout}
              className="rounded bg-red-500 px-4 py-2 text-white"
            >
              Terminar Sessão
            </button>
          </div>
        ) : (
          <div className="flex flex-col gap-4">
            <h1 className="text-2xl font-semibold">Você não está autenticado</h1>
            <Link href="/login" className="text-blue-500 hover:underline">
              Login
            </Link>
          </div>
        )}
      </main>
    </div>
  );
}
