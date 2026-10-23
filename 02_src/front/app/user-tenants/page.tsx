'use client';

import Link from 'next/link';
import { type FormEvent, useEffect, useState } from 'react';
import { useSession } from '../lib/session';

interface Tenant {
  id: number;
  name: string;
}

interface UserTenantRow {
  user_id: number;
  name: string;
  tenants: Tenant[];
}

interface UserTenantsResponse {
  mydetails: UserTenantRow[];
  manageable_tenants: Tenant[];
  view: 'public' | 'admin';
}

interface LoadedData extends UserTenantsResponse {
  requestedToken: string;
}

const apiBaseUrl =
  (process.env.NEXT_PUBLIC_API_BASE_URL ??
    process.env.NEXT_PUBLIC_API_URL ??
    'http://localhost:5000').replace(/\/$/, '');

function errorMessage(data: unknown): string {
  if (typeof data === 'object' && data !== null && 'mydetails' in data) {
    const details = data.mydetails;
    if (typeof details === 'string') return details;
  }
  return 'A solicitação não foi concluída.';
}

async function fetchUserTenants(token: string): Promise<UserTenantsResponse> {
  const response = await fetch(`${apiBaseUrl}/users/tenants`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  const data = await response.json();
  if (!response.ok) throw new Error(errorMessage(data));
  if (
    !Array.isArray(data?.mydetails)
    || !Array.isArray(data?.manageable_tenants)
    || (data.view !== 'public' && data.view !== 'admin')
  ) {
    throw new Error('A API retornou dados em formato inesperado.');
  }
  return {
    mydetails: data.mydetails as UserTenantRow[],
    manageable_tenants: data.manageable_tenants as Tenant[],
    view: data.view,
  };
}

export default function UserTenantsPage() {
  const { token, user } = useSession();
  const [loaded, setLoaded] = useState<LoadedData | null>(null);
  const [selectedUserId, setSelectedUserId] = useState('');
  const [selectedTenantId, setSelectedTenantId] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const data = loaded?.requestedToken === token ? loaded : null;
  const rows = data?.mydetails ?? [];
  const manageableTenants = data?.manageable_tenants ?? [];
  const isSuperAdmin = Boolean(token && user?.super_admin === true && data?.view === 'admin');

  useEffect(() => {
    if (!token) return;
    let mounted = true;
    fetchUserTenants(token)
      .then((response) => {
        if (mounted) setLoaded({ ...response, requestedToken: token });
      })
      .catch((loadError: unknown) => {
        if (mounted) {
          setError(
            loadError instanceof Error
              ? loadError.message
              : 'Não foi possível carregar os vínculos.',
          );
        }
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, [token]);

  async function refresh(currentToken: string) {
    const response = await fetchUserTenants(currentToken);
    setLoaded({ ...response, requestedToken: currentToken });
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !isSuperAdmin) {
      setError('É necessário entrar como superadmin para associar usuários.');
      return;
    }
    if (!selectedUserId || !selectedTenantId) {
      setError('Selecione um usuário e uma organização.');
      return;
    }

    setSaving(true);
    setError(null);
    setNotice(null);
    try {
      const response = await fetch(`${apiBaseUrl}/users/tenants`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          user_id: Number(selectedUserId),
          tenant_id: Number(selectedTenantId),
        }),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(errorMessage(result));
      setSelectedUserId('');
      setSelectedTenantId('');
      setNotice('Usuário associado à organização.');
      await refresh(token);
    } catch (saveError) {
      setError(
        saveError instanceof Error
          ? saveError.message
          : 'Não foi possível associar o usuário.',
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <main className="mx-auto w-full max-w-6xl flex-1 px-5 py-10 sm:px-8">
      <nav className="mb-8 flex flex-wrap items-center gap-3 text-sm">
        <Link className="font-medium text-blue-700 hover:underline" href="/">Início</Link>
        <Link className="text-blue-700 hover:underline" href="/users">Usuários</Link>
        <Link className="text-blue-700 hover:underline" href="/categories">Categorias</Link>
        <Link className="text-blue-700 hover:underline" href="/groups">Grupos</Link>
        <Link className="text-blue-700 hover:underline" href="/artifacts">Artefatos</Link>
        {!token && <Link className="ml-auto text-blue-700 hover:underline" href="/login">Entrar</Link>}
      </nav>

      <header className="mb-8">
        <p className="mb-2 text-sm font-semibold uppercase tracking-wide text-blue-700">Administração</p>
        <h1 className="text-3xl font-bold tracking-tight">Usuários e organizações</h1>
        <p className="mt-2 text-zinc-600">
          Consulte a quais organizações os usuários pertencem. Superadmins podem associá-los a qualquer organização cadastrada.
        </p>
      </header>

      {error && (
        <div role="alert" className="mb-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
          {error}
        </div>
      )}
      {notice && (
        <div role="status" className="mb-6 rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-800">
          {notice}
        </div>
      )}

      {!token ? (
        <p className="mb-8 rounded-lg bg-zinc-100 px-4 py-3 text-sm text-zinc-700">
          Entre para consultar os usuários e suas organizações.
        </p>
      ) : isSuperAdmin ? (
        <section className="mb-10 rounded-xl border border-zinc-200 bg-white p-5 shadow-sm sm:p-7">
          <h2 className="mb-5 text-xl font-semibold">Associar usuário a uma organização</h2>
          <form className="grid gap-5 sm:grid-cols-2" onSubmit={handleSubmit}>
            <label className="flex flex-col gap-2 text-sm font-medium text-zinc-700">
              Usuário
              <select
                className="rounded-lg border border-zinc-300 bg-white px-3 py-2.5"
                onChange={(event) => setSelectedUserId(event.target.value)}
                required
                value={selectedUserId}
              >
                <option value="">Selecione um usuário</option>
                {rows.map((row) => (
                  <option key={row.user_id} value={row.user_id}>
                    {row.name} (#{row.user_id})
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-2 text-sm font-medium text-zinc-700">
              Organização
              <select
                className="rounded-lg border border-zinc-300 bg-white px-3 py-2.5"
                onChange={(event) => setSelectedTenantId(event.target.value)}
                required
                value={selectedTenantId}
              >
                <option value="">Selecione uma organização</option>
                {manageableTenants.map((tenant) => (
                  <option key={tenant.id} value={tenant.id}>{tenant.name}</option>
                ))}
              </select>
            </label>
            <div className="sm:col-span-2">
              <button
                className="rounded-lg bg-blue-700 px-5 py-2.5 font-semibold text-white hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-60"
                disabled={saving || rows.length === 0 || manageableTenants.length === 0}
                type="submit"
              >
                {saving ? 'Salvando…' : 'Associar'}
              </button>
              {manageableTenants.length === 0 && (
                <p className="mt-2 text-sm text-zinc-600">
                  Não há organizações cadastradas para associar.
                </p>
              )}
            </div>
          </form>
        </section>
      ) : (
        <p className="mb-8 rounded-lg bg-blue-50 px-4 py-3 text-sm text-blue-900">
          A consulta está disponível para usuários autenticados. Somente superadmins podem criar associações.
        </p>
      )}

      <section>
        <div className="mb-4 flex items-end justify-between gap-4">
          <div>
            <h2 className="text-xl font-semibold">Vínculos atuais</h2>
            <p className="mt-1 text-sm text-zinc-600">{rows.length} usuários</p>
          </div>
          {token && (
            <button
              className="rounded-lg border border-zinc-300 px-3 py-2 text-sm font-medium hover:bg-zinc-100"
              onClick={async () => {
                setLoading(true);
                try {
                  await refresh(token);
                  setError(null);
                } catch (refreshError) {
                  setError(
                    refreshError instanceof Error
                      ? refreshError.message
                      : 'Não foi possível atualizar os vínculos.',
                  );
                } finally {
                  setLoading(false);
                }
              }}
              type="button"
            >
              Atualizar
            </button>
          )}
        </div>
        {!token ? null : loading ? (
          <p className="py-8 text-zinc-600">Carregando vínculos…</p>
        ) : rows.length === 0 ? (
          <p className="rounded-lg border border-dashed border-zinc-300 px-4 py-8 text-center text-zinc-600">
            Nenhum usuário encontrado.
          </p>
        ) : (
          <div className="overflow-x-auto rounded-xl border border-zinc-200 bg-white">
            <table className="w-full text-left text-sm">
              <thead className="bg-zinc-100 text-zinc-700">
                <tr>
                  <th className="px-4 py-3 font-semibold">Usuário</th>
                  <th className="px-4 py-3 font-semibold">Organizações</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-100">
                {rows.map((row) => (
                  <tr key={row.user_id}>
                    <td className="px-4 py-3 font-medium text-zinc-800">{row.name}</td>
                    <td className="px-4 py-3 text-zinc-700">
                      {row.tenants.length
                        ? row.tenants.map((tenant) => tenant.name).join(', ')
                        : 'Nenhuma organização associada'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  );
}
