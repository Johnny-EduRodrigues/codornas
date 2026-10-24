'use client';

import { useSession } from './lib/session';

export default function Home() {
  const { user } = useSession();

  return (
    <div className="flex flex-col flex-1 items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <main className="flex flex-1 w-full max-w-3xl flex-col items-center justify-between py-32 px-16 bg-white dark:bg-black sm:items-start gap-6">
        {user ? (
          <div className="flex flex-col items-center gap-3 text-center">
            {user.picture && <img src={user.picture} alt={user.name ?? ''} className="h-16 w-16 rounded-full" />}
            <h1 className="text-2xl font-semibold">Bem-vindo(a), {user.name}</h1>
            <p className="text-sm text-gray-600">{user.email}</p>

          </div>
        ) : (
          <div className="flex flex-col gap-4">
            <h1 className="text-2xl font-semibold">Você não está autenticado</h1>
          </div>
        )}
      </main>
    </div>
  );
}
