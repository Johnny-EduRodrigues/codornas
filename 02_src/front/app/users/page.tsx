'use client';

import { type FormEvent, useEffect, useState } from 'react';
import { useSession } from '../lib/session';

interface Tenant {
  id: number;
  name: string;
}

interface ManagedUser {
  id?: number;
  name: string;
  email?: string;
  timestamp_email_verified?: string | null;
  created_at: string;
  obs?: string | null;
  super_admin?: boolean;
  active?: boolean;
  tenants: string[] | Tenant[];
  authentication_identities?: {
    provider: string;
    identificator_login: string;
    identificator_external: string;
  }[];
}

interface UsersResponse {
  mydetails: ManagedUser[];
  manageable_tenants?: Tenant[];
  view: 'public' | 'admin';
}

interface LoadedUsers extends UsersResponse {
  requestedToken: string;
}

const apiBaseUrl =
  (process.env.NEXT_PUBLIC_API_BASE_URL ??
    process.env.NEXT_PUBLIC_API_URL ??
    'http://localhost:5000').replace(/\/$/, '');

function errorMessage(data: unknown) {
  if (typeof data === 'object' && data !== null && 'mydetails' in data) {
    const details = data.mydetails;
    if (typeof details === 'string') return details;
  }
  return 'A solicitação não foi concluída.';
}

export default function UsersPage() {
  const { token, user } = useSession();
  const [loaded, setLoaded] = useState<LoadedUsers | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [selectedTenantIds, setSelectedTenantIds] = useState<number[]>([]);
  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    active: true,
    obs: '',
  });
  const isSuperAdmin = Boolean(token && user?.super_admin === true);
  const users = loaded?.requestedToken === token ? loaded.mydetails : [];
  const tenants = loaded?.requestedToken === token
    ? loaded.manageable_tenants ?? []
    : [];
  const view = loaded?.requestedToken === token ? loaded.view : null;

  async function fetchUsers(currentToken: string): Promise<UsersResponse> {
    const response = await fetch(`${apiBaseUrl}/users`, {
      headers: { Authorization: `Bearer ${currentToken}` },
    });
    const data = await response.json();
    if (!response.ok) throw new Error(errorMessage(data));
    if (
      !Array.isArray(data?.mydetails)
      || (data.view !== 'admin' && data.view !== 'public')
    ) {
      throw new Error('A API retornou dados em formato inesperado.');
    }
    return {
      mydetails: data.mydetails as ManagedUser[],
      manageable_tenants: Array.isArray(data.manageable_tenants)
        ? data.manageable_tenants as Tenant[]
        : [],
      view: data.view,
    };
  }

  useEffect(() => {
    if (!token) return;
    let mounted = true;
    fetchUsers(token)
      .then((data) => {
        if (mounted) setLoaded({ ...data, requestedToken: token });
      })
      .catch((loadError: unknown) => {
        if (mounted) {
          setError(
            loadError instanceof Error
              ? loadError.message
              : 'Não foi possível carregar os usuários.',
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

  function toggleTenant(id: number) {
    setSelectedTenantIds((current) => current.includes(id)
      ? current.filter((tenantId) => tenantId !== id)
      : [...current, id]);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !isSuperAdmin || view !== 'admin') {
      setError('É necessário entrar como superadmin para inserir usuários.');
      return;
    }
    if (selectedTenantIds.length === 0) {
      setError('Selecione ao menos uma organização para o usuário.');
      return;
    }

    setSaving(true);
    setError(null);
    setNotice(null);
    try {
      const response = await fetch(`${apiBaseUrl}/users`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          ...form,
          name: form.name.trim(),
          email: form.email.trim(),
          obs: form.obs.trim() || null,
          tenant_ids: selectedTenantIds,
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(errorMessage(data));

      setForm({
        name: '',
        email: '',
        password: '',
        active: true,
        obs: '',
      });
      setSelectedTenantIds([]);
      setNotice('Usuário criado com sucesso.');
      setLoading(true);
      setLoaded({ ...(await fetchUsers(token)), requestedToken: token });
    } catch (saveError) {
      setError(
        saveError instanceof Error
          ? saveError.message
          : 'Não foi possível criar o usuário.',
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <main className="mx-auto w-full max-w-6xl flex-1 px-5 py-10 sm:px-8">
      <header className="mb-8">
        <p className="mb-2 text-sm font-semibold uppercase tracking-wide text-blue-700">Administração</p>
        <h1 className="text-3xl font-bold tracking-tight">Usuários</h1>
        <p className="mt-2 text-zinc-600">
          Consulte os usuários e as organizações às quais pertencem.
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
          Entre para consultar a lista de usuários.
        </p>
      ) : view === 'admin' && isSuperAdmin ? (
        <section className="mb-10 rounded-xl border border-zinc-200 bg-white p-5 shadow-sm sm:p-7">
          <h2 className="mb-5 text-xl font-semibold">Inserir usuário</h2>
          <form className="grid gap-5 sm:grid-cols-2" onSubmit={handleSubmit}>
            <label className="flex flex-col gap-2 text-sm font-medium text-zinc-700">
              Nome
              <input
                autoComplete="name"
                className="rounded-lg border border-zinc-300 px-3 py-2.5"
                onChange={(event) => setForm({ ...form, name: event.target.value })}
                required
                value={form.name}
              />
            </label>
            <label className="flex flex-col gap-2 text-sm font-medium text-zinc-700">
              Email
              <input
                autoComplete="email"
                className="rounded-lg border border-zinc-300 px-3 py-2.5"
                onChange={(event) => setForm({ ...form, email: event.target.value })}
                required
                type="email"
                value={form.email}
              />
            </label>
            <label className="flex flex-col gap-2 text-sm font-medium text-zinc-700">
              Senha inicial
              <input
                autoComplete="new-password"
                className="rounded-lg border border-zinc-300 px-3 py-2.5"
                onChange={(event) => setForm({ ...form, password: event.target.value })}
                required
                type="password"
                value={form.password}
              />
            </label>
            <label className="flex items-center gap-3 text-sm font-medium text-zinc-700">
              <input
                checked={form.active}
                className="h-4 w-4 rounded border-zinc-300"
                onChange={(event) => setForm({ ...form, active: event.target.checked })}
                type="checkbox"
              />
              Usuário ativo
            </label>
            <label className="flex flex-col gap-2 text-sm font-medium text-zinc-700 sm:col-span-2">
              Observações
              <textarea
                className="min-h-20 rounded-lg border border-zinc-300 px-3 py-2.5"
                onChange={(event) => setForm({ ...form, obs: event.target.value })}
                value={form.obs}
              />
            </label>
            <fieldset className="sm:col-span-2">
              <legend className="mb-2 text-sm font-medium text-zinc-700">Organizações do usuário</legend>
              <div className="grid gap-2 sm:grid-cols-2">
                {tenants.map((tenant) => (
                  <label
                    className="flex items-center gap-3 rounded-lg border border-zinc-200 px-3 py-2 text-sm"
                    key={tenant.id}
                  >
                    <input
                      checked={selectedTenantIds.includes(tenant.id)}
                      className="h-4 w-4 rounded border-zinc-300"
                      onChange={() => toggleTenant(tenant.id)}
                      type="checkbox"
                    />
                    {tenant.name}
                  </label>
                ))}
              </div>
              {tenants.length === 0 && (
                <p className="text-sm text-zinc-600">Sua conta ainda não pertence a nenhuma organização.</p>
              )}
            </fieldset>
            <div className="sm:col-span-2">
              <button
                className="rounded-lg bg-blue-700 px-5 py-2.5 font-semibold text-white hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-60"
                disabled={saving || tenants.length === 0}
                type="submit"
              >
                {saving ? 'Salvando…' : 'Criar usuário'}
              </button>
            </div>
          </form>
        </section>
      ) : token ? (
        <p className="mb-8 rounded-lg bg-blue-50 px-4 py-3 text-sm text-blue-900">
          A lista mostra apenas nome, organizações e data de criação. Somente superadmins podem consultar os demais dados e cadastrar usuários.
        </p>
      ) : null}

      <section>
        <div className="mb-4 flex items-end justify-between gap-4">
          <div>
            <h2 className="text-xl font-semibold">Usuários cadastrados</h2>
            <p className="mt-1 text-sm text-zinc-600">{users.length} no total</p>
          </div>
          {token && (
            <button
              className="rounded-lg border border-zinc-300 px-3 py-2 text-sm font-medium hover:bg-zinc-100"
              onClick={async () => {
                setLoading(true);
                try {
                  setLoaded({ ...(await fetchUsers(token)), requestedToken: token });
                  setError(null);
                } catch (refreshError) {
                  setError(
                    refreshError instanceof Error
                      ? refreshError.message
                      : 'Não foi possível atualizar os usuários.',
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
          <p className="py-8 text-zinc-600">Carregando usuários…</p>
        ) : users.length === 0 ? (
          <p className="rounded-lg border border-dashed border-zinc-300 px-4 py-8 text-center text-zinc-600">
            Nenhum usuário encontrado nas organizações permitidas.
          </p>
        ) : view === 'admin' ? (
          <div className="space-y-4">
            {users.map((managedUser, index) => (
              <article
                className="rounded-xl border border-zinc-200 bg-white p-5 shadow-sm"
                key={managedUser.id ?? `${managedUser.email}-${index}`}
              >
                <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <h3 className="text-lg font-semibold">{managedUser.name}</h3>
                    <p className="text-sm text-zinc-600">{managedUser.email}</p>
                  </div>
                  <span className={`rounded-full px-3 py-1 text-xs font-semibold ${managedUser.active ? 'bg-green-100 text-green-800' : 'bg-zinc-200 text-zinc-700'}`}>
                    {managedUser.active ? 'Ativo' : 'Inativo'}
                  </span>
                </div>
                <dl className="grid gap-3 text-sm sm:grid-cols-2">
                  <div>
                    <dt className="font-medium text-zinc-500">Organizações</dt>
                    <dd>{(managedUser.tenants as Tenant[]).map((tenant) => tenant.name).join(', ') || '—'}</dd>
                  </div>
                  <div>
                    <dt className="font-medium text-zinc-500">Criado em</dt>
                    <dd>{new Date(managedUser.created_at).toLocaleString()}</dd>
                  </div>
                  <div>
                    <dt className="font-medium text-zinc-500">Email verificado em</dt>
                    <dd>{managedUser.timestamp_email_verified ? new Date(managedUser.timestamp_email_verified).toLocaleString() : 'Não verificado'}</dd>
                  </div>
                  <div>
                    <dt className="font-medium text-zinc-500">Superadmin</dt>
                    <dd>{managedUser.super_admin ? 'Sim' : 'Não'}</dd>
                  </div>
                  <div className="sm:col-span-2">
                    <dt className="font-medium text-zinc-500">Observações</dt>
                    <dd>{managedUser.obs || '—'}</dd>
                  </div>
                  <div className="sm:col-span-2">
                    <dt className="font-medium text-zinc-500">Identidades de autenticação</dt>
                    <dd>
                      {managedUser.authentication_identities?.length
                        ? managedUser.authentication_identities.map((identity) => (
                          <span className="mr-3 inline-block" key={`${identity.provider}-${identity.identificator_external}`}>
                            {identity.provider}: {identity.identificator_login} ({identity.identificator_external})
                          </span>
                        ))
                        : 'Nenhuma'}
                    </dd>
                  </div>
                </dl>
              </article>
            ))}
          </div>
        ) : (
          <div className="overflow-x-auto rounded-xl border border-zinc-200 bg-white">
            <table className="w-full text-left text-sm">
              <thead className="bg-zinc-100 text-zinc-700">
                <tr>
                  <th className="px-4 py-3 font-semibold">Nome</th>
                  <th className="px-4 py-3 font-semibold">Organizações</th>
                  <th className="px-4 py-3 font-semibold">Criado em</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-100">
                {users.map((managedUser, index) => (
                  <tr key={`${managedUser.name}-${index}`}>
                    <td className="px-4 py-3 text-zinc-800">{managedUser.name}</td>
                    <td className="px-4 py-3 text-zinc-800">{(managedUser.tenants as string[]).join(', ') || '—'}</td>
                    <td className="px-4 py-3 text-zinc-800">{new Date(managedUser.created_at).toLocaleString()}</td>
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
