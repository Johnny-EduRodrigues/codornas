'use client';

import Link from 'next/link';
import { clearSession, useSession } from '../lib/session';

const links = [
  { href: '/categories', label: 'Categorias' },
  { href: '/groups', label: 'Grupos' },
  { href: '/artifacts', label: 'Artefatos' },
  { href: '/artifact-categories', label: 'Categorias (art)' },
  { href: '/users', label: 'Usuários' },
  { href: '/user-tenants', label: 'Us & Org' },
  { href: '/tenants', label: 'Organizações' },
  { href: '/reservations', label: 'Reservas' },
];

export function AppNavigation() {
  const { token, user } = useSession();

  return (
    <header className="border-b border-zinc-200 bg-white">
      <nav
        aria-label="Navegação principal"
        className="mx-auto flex w-full max-w-6xl flex-wrap items-center gap-x-5 gap-y-3 px-5 py-4 text-sm sm:px-8"
      >
        <Link className="mr-1 font-bold text-zinc-900 hover:text-blue-700" href="/">
          SIRA
        </Link>
        {links.map((link) => (
          <Link
            className="text-zinc-700 hover:text-blue-700 hover:underline"
            href={link.href}
            key={link.href}
          >
            {link.label}
          </Link>
        ))}
        <div className="ml-auto flex items-center gap-4">
          {token ? (
            <>
              {user?.name && (
                <span className="hidden text-zinc-600 sm:inline">{user.name}</span>
              )}
              <button
                className="font-medium text-red-700 hover:underline"
                onClick={clearSession}
                type="button"
              >
                Sair
              </button>
            </>
          ) : (
            <Link className="font-medium text-blue-700 hover:underline" href="/login">
              Entrar
            </Link>
          )}
        </div>
      </nav>
    </header>
  );
}
