'use client';

import { type FormEvent, useEffect, useState } from 'react';
import { PurposeSelect, type PurposeOption } from '../components/purpose-select';
import { useSession } from '../lib/session';

interface Artifact {
  id: number;
  name: string;
  active: boolean;
  tenant_id: number;
}

interface Group {
  id: number;
  acronym: string;
  name: string;
  active: boolean;
}

interface Reservation {
  id: number;
  user_id: number;
  artifact_id: number;
  purpose_id: number;
  group_id: number | null;
  date: string;
  start_time: string;
  end_time: string;
  active: boolean;
  obs: string | null;
}

interface ReservationPageData {
  reservations: Reservation[];
  artifacts: Artifact[];
  purposes: PurposeOption[];
  groups: Group[];
}

const apiBaseUrl =
  (process.env.NEXT_PUBLIC_API_BASE_URL ??
    process.env.NEXT_PUBLIC_API_URL ??
    'http://localhost:5000').replace(/\/$/, '');

function responseError(data: unknown): string {
  if (typeof data === 'object' && data !== null && 'mydetails' in data) {
    const details = data.mydetails;
    if (typeof details === 'string') return details;
  }
  return 'A solicitação não foi concluída.';
}

async function fetchList<T>(endpoint: string): Promise<T[]> {
  const response = await fetch(`${apiBaseUrl}${endpoint}`);
  const data = await response.json();
  if (!response.ok) throw new Error(responseError(data));
  if (!Array.isArray(data?.mydetails)) {
    throw new Error('A API retornou dados em formato inesperado.');
  }
  return data.mydetails as T[];
}

async function fetchPageData(): Promise<ReservationPageData> {
  const [reservations, artifacts, purposes, groups] = await Promise.all([
    fetchList<Reservation>('/reservations'),
    fetchList<Artifact>('/artifacts'),
    fetchList<PurposeOption>('/purposes'),
    fetchList<Group>('/groups'),
  ]);
  return { reservations, artifacts, purposes, groups };
}

export default function ReservationsPage() {
  const { token } = useSession();
  const [pageData, setPageData] = useState<ReservationPageData>({
    reservations: [],
    artifacts: [],
    purposes: [],
    groups: [],
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [form, setForm] = useState({
    artifact_id: '',
    purpose_id: '',
    date: '',
    start_time: '',
    end_time: '',
    group_id: '',
    obs: '',
  });

  const selectedArtifact = pageData.artifacts.find(
    (artifact) => String(artifact.id) === form.artifact_id,
  );

  async function refresh() {
    setLoading(true);
    setError(null);
    try {
      setPageData(await fetchPageData());
    } catch (loadError) {
      setError(
        loadError instanceof Error
          ? loadError.message
          : 'Não foi possível carregar as reservas.',
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    let mounted = true;
    fetchPageData()
      .then((data) => {
        if (mounted) setPageData(data);
      })
      .catch((loadError: unknown) => {
        if (mounted) {
          setError(
            loadError instanceof Error
              ? loadError.message
              : 'Não foi possível carregar as reservas.',
          );
        }
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      setError('Entre para criar uma reserva.');
      return;
    }

    setSaving(true);
    setError(null);
    setNotice(null);
    try {
      const response = await fetch(`${apiBaseUrl}/reservations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          artifact_id: Number(form.artifact_id),
          purpose_id: Number(form.purpose_id),
          date: form.date,
          start_time: form.start_time,
          end_time: form.end_time,
          group_id: form.group_id ? Number(form.group_id) : null,
          obs: form.obs.trim() || null,
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(responseError(data));

      setForm({
        artifact_id: '',
        purpose_id: '',
        date: '',
        start_time: '',
        end_time: '',
        group_id: '',
        obs: '',
      });
      setNotice('Reserva criada com sucesso.');
      await refresh();
    } catch (saveError) {
      setError(
        saveError instanceof Error
          ? saveError.message
          : 'Não foi possível criar a reserva.',
      );
    } finally {
      setSaving(false);
    }
  }

  const artifacts = new Map(
    pageData.artifacts.map((artifact) => [artifact.id, artifact.name]),
  );
  const purposes = new Map(
    pageData.purposes.map((purpose) => [purpose.id, purpose.description]),
  );
  const groups = new Map(
    pageData.groups.map((group) => [group.id, `${group.acronym} - ${group.name}`]),
  );

  return (
    <main className="mx-auto w-full max-w-6xl flex-1 px-5 py-10 sm:px-8">
      <header className="mb-8">
        <p className="mb-2 text-sm font-semibold uppercase tracking-wide text-blue-700">Reservas</p>
        <h1 className="text-3xl font-bold tracking-tight">Reservas de artefatos</h1>
        <p className="mt-2 text-zinc-600">
          Consulte as reservas existentes. Usuários autenticados podem criar novas reservas.
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

      {token ? (
        <section className="mb-10 rounded-xl border border-zinc-200 bg-white p-5 shadow-sm sm:p-7">
          <h2 className="mb-5 text-xl font-semibold">Criar reserva</h2>
          <form className="grid gap-5 sm:grid-cols-2" onSubmit={handleSubmit}>
            <label className="flex flex-col gap-2 text-sm font-medium text-zinc-700">
              Artefato
              <select
                className="rounded-lg border border-zinc-300 bg-white px-3 py-2.5"
                onChange={(event) => setForm({ ...form, artifact_id: event.target.value })}
                required
                value={form.artifact_id}
              >
                <option value="">Selecione um artefato</option>
                {pageData.artifacts.filter((item) => item.active).map((artifact) => (
                  <option key={artifact.id} value={artifact.id}>{artifact.name}</option>
                ))}
              </select>
            </label>
            <PurposeSelect
              onChange={(purpose_id) => setForm((current) => ({ ...current, purpose_id }))}
              onCreated={(purpose) =>
                setPageData((current) => ({
                  ...current,
                  purposes: [...current.purposes, purpose],
                }))
              }
              purposes={pageData.purposes}
              tenantId={selectedArtifact?.tenant_id ?? null}
              token={token}
              value={form.purpose_id}
            />
            <label className="flex flex-col gap-2 text-sm font-medium text-zinc-700">
              Data
              <input
                className="rounded-lg border border-zinc-300 px-3 py-2.5"
                onChange={(event) => setForm({ ...form, date: event.target.value })}
                required
                type="date"
                value={form.date}
              />
            </label>
            <div className="grid grid-cols-2 gap-3">
              <label className="flex flex-col gap-2 text-sm font-medium text-zinc-700">
                Início
                <input
                  className="rounded-lg border border-zinc-300 px-3 py-2.5"
                  onChange={(event) => setForm({ ...form, start_time: event.target.value })}
                  required
                  type="time"
                  value={form.start_time}
                />
              </label>
              <label className="flex flex-col gap-2 text-sm font-medium text-zinc-700">
                Término
                <input
                  className="rounded-lg border border-zinc-300 px-3 py-2.5"
                  onChange={(event) => setForm({ ...form, end_time: event.target.value })}
                  required
                  type="time"
                  value={form.end_time}
                />
              </label>
            </div>
            <label className="flex flex-col gap-2 text-sm font-medium text-zinc-700">
              Grupo (opcional)
              <select
                className="rounded-lg border border-zinc-300 bg-white px-3 py-2.5"
                onChange={(event) => setForm({ ...form, group_id: event.target.value })}
                value={form.group_id}
              >
                <option value="">Nenhum grupo</option>
                {pageData.groups.filter((item) => item.active).map((group) => (
                  <option key={group.id} value={group.id}>{group.acronym} - {group.name}</option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-2 text-sm font-medium text-zinc-700 sm:col-span-2">
              Observações (opcional)
              <textarea
                className="min-h-20 rounded-lg border border-zinc-300 px-3 py-2.5"
                onChange={(event) => setForm({ ...form, obs: event.target.value })}
                value={form.obs}
              />
            </label>
            <div className="sm:col-span-2">
              <button
                className="rounded-lg bg-blue-700 px-5 py-2.5 font-semibold text-white hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-60"
                disabled={saving || pageData.artifacts.filter((item) => item.active).length === 0}
                type="submit"
              >
                {saving ? 'Salvando…' : 'Criar reserva'}
              </button>
            </div>
          </form>
        </section>
      ) : (
        <p className="mb-8 rounded-lg bg-blue-50 px-4 py-3 text-sm text-blue-900">
          A consulta é pública. Entre para criar uma reserva.
        </p>
      )}

      <section>
        <div className="mb-4 flex items-end justify-between gap-4">
          <div>
            <h2 className="text-xl font-semibold">Reservas existentes</h2>
            <p className="mt-1 text-sm text-zinc-600">{pageData.reservations.length} no total</p>
          </div>
          <button
            className="rounded-lg border border-zinc-300 px-3 py-2 text-sm font-medium hover:bg-zinc-100"
            onClick={() => void refresh()}
            type="button"
          >
            Atualizar
          </button>
        </div>
        {loading ? (
          <p className="py-8 text-zinc-600">Carregando reservas…</p>
        ) : pageData.reservations.length === 0 ? (
          <p className="rounded-lg border border-dashed border-zinc-300 px-4 py-8 text-center text-zinc-600">
            Nenhuma reserva encontrada.
          </p>
        ) : (
          <div className="overflow-x-auto rounded-xl border border-zinc-200 bg-white">
            <table className="w-full text-left text-sm">
              <thead className="bg-zinc-100 text-zinc-700">
                <tr>
                  <th className="px-4 py-3 font-semibold">Artefato</th>
                  <th className="px-4 py-3 font-semibold">Data</th>
                  <th className="px-4 py-3 font-semibold">Horário</th>
                  <th className="px-4 py-3 font-semibold">Finalidade</th>
                  <th className="px-4 py-3 font-semibold">Grupo</th>
                  <th className="px-4 py-3 font-semibold">Usuário (ID)</th>
                  <th className="px-4 py-3 font-semibold">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-100">
                {pageData.reservations.map((reservation) => (
                  <tr key={reservation.id}>
                    <td className="px-4 py-3 text-zinc-800">{artifacts.get(reservation.artifact_id) ?? `#${reservation.artifact_id}`}</td>
                    <td className="whitespace-nowrap px-4 py-3 text-zinc-800">{reservation.date}</td>
                    <td className="whitespace-nowrap px-4 py-3 text-zinc-800">{reservation.start_time}–{reservation.end_time}</td>
                    <td className="px-4 py-3 text-zinc-800">{purposes.get(reservation.purpose_id) ?? `#${reservation.purpose_id}`}</td>
                    <td className="px-4 py-3 text-zinc-800">{reservation.group_id ? groups.get(reservation.group_id) ?? `#${reservation.group_id}` : '—'}</td>
                    <td className="px-4 py-3 text-zinc-800">{reservation.user_id}</td>
                    <td className="px-4 py-3 text-zinc-800">{reservation.active ? 'Ativa' : 'Cancelada'}</td>
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
