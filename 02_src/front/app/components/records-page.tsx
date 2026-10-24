'use client';

import { type FormEvent, useEffect, useState } from 'react';
import { useSession } from '../lib/session';

type RecordData = Record<string, unknown>;

interface Tenant {
  id: number;
  name: string;
}

interface FormField {
  name: string;
  label: string;
  kind: 'text' | 'textarea' | 'tenant' | 'checkbox';
  required?: boolean;
  defaultValue?: string | boolean;
}

interface RecordPageConfig {
  endpoint: string;
  title: string;
  description: string;
  fields: FormField[];
  columns: { key: string; label: string }[];
}

const apiBaseUrl =
  (process.env.NEXT_PUBLIC_API_BASE_URL ??
    process.env.NEXT_PUBLIC_API_URL ??
    'http://localhost:5000').replace(/\/$/, '');

function apiErrorMessage(data: unknown): string {
  if (typeof data === 'object' && data !== null && 'mydetails' in data) {
    const details = data.mydetails;
    if (typeof details === 'string') return details;
  }
  if (typeof data === 'object' && data !== null && 'error' in data) {
    const error = data.error;
    if (typeof error === 'string') return error;
  }
  return 'A solicitação não foi concluída.';
}

async function fetchPageData(endpoint: string) {
  const [recordsResponse, tenantsResponse] = await Promise.all([
    fetch(`${apiBaseUrl}${endpoint}`),
    fetch(`${apiBaseUrl}/tenants`),
  ]);
  const [recordsData, tenantsData] = await Promise.all([
    recordsResponse.json(),
    tenantsResponse.json(),
  ]);
  if (!recordsResponse.ok) throw new Error(apiErrorMessage(recordsData));
  if (!tenantsResponse.ok) throw new Error(apiErrorMessage(tenantsData));
  const records = recordsData?.mydetails;
  const tenants = tenantsData?.mydetails;
  if (!Array.isArray(records) || !Array.isArray(tenants)) {
    throw new Error('A API retornou dados em formato inesperado.');
  }
  return {
    records: records as RecordData[],
    tenants: tenants as Tenant[],
  };
}

export function RecordsPage({ config }: { config: RecordPageConfig }) {
  const [records, setRecords] = useState<RecordData[]>([]);
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const { token, user } = useSession();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [form, setForm] = useState<Record<string, string | boolean>>(
    () => Object.fromEntries(
      config.fields
        .filter((field) => field.kind !== 'tenant')
        .map((field) => [field.name, field.defaultValue ?? '']),
    ),
  );

  const isSuperAdmin = Boolean(token && user?.super_admin === true);
  const requiresTenant = config.fields.some((field) => field.kind === 'tenant');

  async function loadData() {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchPageData(config.endpoint);
      setRecords(data.records);
      setTenants(data.tenants);
    } catch (loadError) {
      setError(
        loadError instanceof Error
          ? loadError.message
          : 'Não foi possível carregar os dados.',
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    let mounted = true;
    fetchPageData(config.endpoint)
      .then((data) => {
        if (!mounted) return;
        setRecords(data.records);
        setTenants(data.tenants);
      })
      .catch((loadError: unknown) => {
        if (!mounted) return;
        setError(
          loadError instanceof Error
            ? loadError.message
            : 'Não foi possível carregar os dados.',
        );
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, [config.endpoint]);

  function updateField(name: string, value: string | boolean) {
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !isSuperAdmin) {
      setError('É necessário entrar como superadmin para inserir dados.');
      return;
    }

    setSaving(true);
    setError(null);
    setNotice(null);
    try {
      const payload: Record<string, string | number | boolean | null> = {};
      for (const field of config.fields) {
        if (field.kind === 'tenant') {
          payload[field.name] = Number(form[field.name] ?? 0);
        } else if (field.kind === 'checkbox') {
          payload[field.name] = form[field.name] === true;
        } else {
          const value = String(form[field.name] ?? '').trim();
          payload[field.name] = value || (field.required ? '' : null);
        }
      }

      const response = await fetch(`${apiBaseUrl}${config.endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(apiErrorMessage(data));

      setNotice('Registro criado com sucesso.');
      setForm(Object.fromEntries(
        config.fields
          .filter((field) => field.kind !== 'tenant')
          .map((field) => [field.name, field.defaultValue ?? '']),
      ));
      await loadData();
    } catch (saveError) {
      setError(
        saveError instanceof Error
          ? saveError.message
          : 'Não foi possível salvar o registro.',
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <main className="mx-auto w-full max-w-6xl flex-1 px-5 py-10 sm:px-8">
      <header className="mb-8">
        <p className="mb-2 text-sm font-semibold uppercase tracking-wide text-blue-700">Catálogo público</p>
        <h1 className="text-3xl font-bold tracking-tight">{config.title}</h1>
        <p className="mt-2 text-zinc-600">{config.description}</p>
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

      {isSuperAdmin ? (
        <section className="mb-10 rounded-xl border border-zinc-200 bg-white p-5 shadow-sm sm:p-7">
          <h2 className="mb-5 text-xl font-semibold">Inserir {config.title.toLowerCase()}</h2>
          <form className="grid gap-5 sm:grid-cols-2" onSubmit={handleSubmit}>
            {config.fields.map((field) => (
              <label
                className={`flex flex-col gap-2 text-sm font-medium text-zinc-700 ${field.kind === 'textarea' ? 'sm:col-span-2' : ''}`}
                key={field.name}
              >
                {field.kind === 'checkbox' ? (
                  <span className="flex items-center gap-3">
                    <input
                      checked={form[field.name] === true}
                      className="h-4 w-4 rounded border-zinc-300"
                      onChange={(event) => updateField(field.name, event.target.checked)}
                      type="checkbox"
                    />
                    {field.label}
                  </span>
                ) : field.kind === 'tenant' ? (
                  <>
                    {field.label}
                    <select
                      className="rounded-lg border border-zinc-300 bg-white px-3 py-2.5"
                      onChange={(event) => updateField(field.name, event.target.value)}
                      required
                      value={String(form[field.name] ?? '')}
                    >
                      <option value="">Selecione uma organização</option>
                      {tenants.map((tenant) => (
                        <option key={tenant.id} value={tenant.id}>{tenant.name}</option>
                      ))}
                    </select>
                  </>
                ) : field.kind === 'textarea' ? (
                  <>
                    {field.label}
                    <textarea
                      className="min-h-24 rounded-lg border border-zinc-300 px-3 py-2.5"
                      onChange={(event) => updateField(field.name, event.target.value)}
                      required={field.required}
                      value={String(form[field.name] ?? '')}
                    />
                  </>
                ) : (
                  <>
                    {field.label}
                    <input
                      className="rounded-lg border border-zinc-300 px-3 py-2.5"
                      onChange={(event) => updateField(field.name, event.target.value)}
                      required={field.required}
                      type="text"
                      value={String(form[field.name] ?? '')}
                    />
                  </>
                )}
              </label>
            ))}
            <div className="sm:col-span-2">
              <button
                className="rounded-lg bg-blue-700 px-5 py-2.5 font-semibold text-white hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-60"
                disabled={saving || (requiresTenant && tenants.length === 0)}
                type="submit"
              >
                {saving ? 'Salvando…' : 'Salvar'}
              </button>
              {requiresTenant && tenants.length === 0 && (
                <p className="mt-2 text-sm text-zinc-600">Cadastre uma organização antes de inserir este registro.</p>
              )}
            </div>
          </form>
        </section>
      ) : token ? (
        <p className="mb-8 rounded-lg bg-blue-50 px-4 py-3 text-sm text-blue-900">
          Você pode consultar os dados. Somente um usuário superadmin pode inserir registros.
        </p>
      ) : (
        <p className="mb-8 rounded-lg bg-zinc-100 px-4 py-3 text-sm text-zinc-700">
          A consulta é pública. Para inserir registros, entre com uma conta superadmin.
        </p>
      )}

      <section>
        <div className="mb-4 flex items-end justify-between gap-4">
          <div>
            <h2 className="text-xl font-semibold">Registros</h2>
            <p className="mt-1 text-sm text-zinc-600">{records.length} no total</p>
          </div>
          <button
            className="rounded-lg border border-zinc-300 px-3 py-2 text-sm font-medium hover:bg-zinc-100"
            onClick={() => void loadData()}
            type="button"
          >
            Atualizar
          </button>
        </div>

        {loading ? (
          <p className="py-8 text-zinc-600">Carregando registros…</p>
        ) : records.length === 0 ? (
          <p className="rounded-lg border border-dashed border-zinc-300 px-4 py-8 text-center text-zinc-600">
            Nenhum registro encontrado.
          </p>
        ) : (
          <div className="overflow-x-auto rounded-xl border border-zinc-200 bg-white">
            <table className="w-full text-left text-sm">
              <thead className="bg-zinc-100 text-zinc-700">
                <tr>
                  {config.columns.map((column) => (
                    <th className="whitespace-nowrap px-4 py-3 font-semibold" key={column.key}>{column.label}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-100">
                {records.map((record, index) => (
                  <tr key={String(record.id ?? index)}>
                    {config.columns.map((column) => (
                      <td className="px-4 py-3 text-zinc-800" key={column.key}>
                        {record[column.key] === null || record[column.key] === undefined
                          ? '—'
                          : String(record[column.key])}
                      </td>
                    ))}
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
