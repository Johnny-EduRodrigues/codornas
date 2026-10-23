'use client';

import Link from 'next/link';
import { type FormEvent, useEffect, useMemo, useState } from 'react';
import { useSession } from '../lib/session';

interface Artifact {
  id: number;
  name: string;
  tenant_id: number;
}

interface Category {
  id: number;
  name: string;
  tenant_id: number;
}

interface ArtifactCategory {
  artifact_id: number;
  artifact_name: string;
  category_id: number;
  category_name: string;
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

export default function ArtifactCategoriesPage() {
  const { token, user } = useSession();
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [associations, setAssociations] = useState<ArtifactCategory[]>([]);
  const [artifactId, setArtifactId] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const isSuperAdmin = Boolean(token && user?.super_admin === true);

  const artifact = artifacts.find((item) => String(item.id) === artifactId);
  const availableCategories = useMemo(
    () => categories.filter((item) => item.tenant_id === artifact?.tenant_id),
    [categories, artifact?.tenant_id],
  );

  async function loadData() {
    setLoading(true);
    setError(null);
    try {
      const [artifactResponse, categoryResponse, associationResponse] =
        await Promise.all([
          fetch(`${apiBaseUrl}/artifacts`),
          fetch(`${apiBaseUrl}/categories`),
          fetch(`${apiBaseUrl}/artifacts/categories`),
        ]);
      const [artifactData, categoryData, associationData] = await Promise.all([
        artifactResponse.json(),
        categoryResponse.json(),
        associationResponse.json(),
      ]);
      if (!artifactResponse.ok) throw new Error(responseError(artifactData));
      if (!categoryResponse.ok) throw new Error(responseError(categoryData));
      if (!associationResponse.ok) {
        throw new Error(responseError(associationData));
      }
      if (
        !Array.isArray(artifactData?.mydetails)
        || !Array.isArray(categoryData?.mydetails)
        || !Array.isArray(associationData?.mydetails)
      ) {
        throw new Error('A API retornou dados em formato inesperado.');
      }
      setArtifacts(artifactData.mydetails as Artifact[]);
      setCategories(categoryData.mydetails as Category[]);
      setAssociations(associationData.mydetails as ArtifactCategory[]);
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
    Promise.all([
      fetch(`${apiBaseUrl}/artifacts`).then(async (response) => ({
        response,
        data: await response.json(),
      })),
      fetch(`${apiBaseUrl}/categories`).then(async (response) => ({
        response,
        data: await response.json(),
      })),
      fetch(`${apiBaseUrl}/artifacts/categories`).then(async (response) => ({
        response,
        data: await response.json(),
      })),
    ])
      .then(([artifactResult, categoryResult, associationResult]) => {
        if (!mounted) return;
        if (!artifactResult.response.ok) {
          throw new Error(responseError(artifactResult.data));
        }
        if (!categoryResult.response.ok) {
          throw new Error(responseError(categoryResult.data));
        }
        if (!associationResult.response.ok) {
          throw new Error(responseError(associationResult.data));
        }
        if (
          !Array.isArray(artifactResult.data?.mydetails)
          || !Array.isArray(categoryResult.data?.mydetails)
          || !Array.isArray(associationResult.data?.mydetails)
        ) {
          throw new Error('A API retornou dados em formato inesperado.');
        }
        setArtifacts(artifactResult.data.mydetails as Artifact[]);
        setCategories(categoryResult.data.mydetails as Category[]);
        setAssociations(associationResult.data.mydetails as ArtifactCategory[]);
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
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !isSuperAdmin) {
      setError('É necessário entrar como superadmin para associar artefatos.');
      return;
    }
    if (!artifactId || !categoryId) {
      setError('Selecione um artefato e uma categoria.');
      return;
    }

    setSaving(true);
    setError(null);
    setNotice(null);
    try {
      const response = await fetch(`${apiBaseUrl}/artifacts/categories`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          artifact_id: Number(artifactId),
          category_id: Number(categoryId),
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(responseError(data));
      setNotice('Categoria associada ao artefato.');
      setArtifactId('');
      setCategoryId('');
      await loadData();
    } catch (saveError) {
      setError(
        saveError instanceof Error
          ? saveError.message
          : 'Não foi possível associar a categoria.',
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <main className="mx-auto w-full max-w-6xl flex-1 px-5 py-10 sm:px-8">
      <nav className="mb-8 flex flex-wrap items-center gap-3 text-sm">
        <Link className="font-medium text-blue-700 hover:underline" href="/">Início</Link>
        <Link className="text-blue-700 hover:underline" href="/categories">Categorias</Link>
        <Link className="text-blue-700 hover:underline" href="/groups">Grupos</Link>
        <Link className="text-blue-700 hover:underline" href="/artifacts">Artefatos</Link>
        {!token && <Link className="ml-auto text-blue-700 hover:underline" href="/login">Entrar</Link>}
      </nav>

      <header className="mb-8">
        <p className="mb-2 text-sm font-semibold uppercase tracking-wide text-blue-700">Catálogo público</p>
        <h1 className="text-3xl font-bold tracking-tight">Categorias dos artefatos</h1>
        <p className="mt-2 text-zinc-600">
          Consulte as associações existentes ou, como superadmin, associe uma categoria a um artefato.
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

      {isSuperAdmin ? (
        <section className="mb-10 rounded-xl border border-zinc-200 bg-white p-5 shadow-sm sm:p-7">
          <h2 className="mb-5 text-xl font-semibold">Nova associação</h2>
          <form className="grid gap-5 sm:grid-cols-2" onSubmit={handleSubmit}>
            <label className="flex flex-col gap-2 text-sm font-medium text-zinc-700">
              Artefato
              <select
                className="rounded-lg border border-zinc-300 bg-white px-3 py-2.5"
                onChange={(event) => {
                  setArtifactId(event.target.value);
                  setCategoryId('');
                }}
                required
                value={artifactId}
              >
                <option value="">Selecione um artefato</option>
                {artifacts.map((item) => (
                  <option key={item.id} value={item.id}>{item.name}</option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-2 text-sm font-medium text-zinc-700">
              Categoria
              <select
                className="rounded-lg border border-zinc-300 bg-white px-3 py-2.5"
                disabled={!artifactId}
                onChange={(event) => setCategoryId(event.target.value)}
                required
                value={categoryId}
              >
                <option value="">Selecione uma categoria</option>
                {availableCategories.map((item) => (
                  <option key={item.id} value={item.id}>{item.name}</option>
                ))}
              </select>
            </label>
            <div className="sm:col-span-2">
              <button
                className="rounded-lg bg-blue-700 px-5 py-2.5 font-semibold text-white hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-60"
                disabled={saving || artifacts.length === 0 || availableCategories.length === 0}
                type="submit"
              >
                {saving ? 'Salvando…' : 'Associar categoria'}
              </button>
              {artifactId && availableCategories.length === 0 && (
                <p className="mt-2 text-sm text-zinc-600">
                  Não há categorias cadastradas para a organização deste artefato.
                </p>
              )}
            </div>
          </form>
        </section>
      ) : (
        <p className="mb-8 rounded-lg bg-zinc-100 px-4 py-3 text-sm text-zinc-700">
          A consulta é pública. Para criar associações, entre com uma conta superadmin.
        </p>
      )}

      <section>
        <div className="mb-4 flex items-end justify-between gap-4">
          <div>
            <h2 className="text-xl font-semibold">Associações existentes</h2>
            <p className="mt-1 text-sm text-zinc-600">{associations.length} no total</p>
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
          <p className="py-8 text-zinc-600">Carregando associações…</p>
        ) : associations.length === 0 ? (
          <p className="rounded-lg border border-dashed border-zinc-300 px-4 py-8 text-center text-zinc-600">
            Nenhuma associação encontrada.
          </p>
        ) : (
          <div className="overflow-x-auto rounded-xl border border-zinc-200 bg-white">
            <table className="w-full text-left text-sm">
              <thead className="bg-zinc-100 text-zinc-700">
                <tr>
                  <th className="px-4 py-3 font-semibold">Artefato</th>
                  <th className="px-4 py-3 font-semibold">Categoria</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-100">
                {associations.map((item) => (
                  <tr key={`${item.artifact_id}-${item.category_id}`}>
                    <td className="px-4 py-3 text-zinc-800">{item.artifact_name}</td>
                    <td className="px-4 py-3 text-zinc-800">{item.category_name}</td>
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
