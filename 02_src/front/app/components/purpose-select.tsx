'use client';

import { useState } from 'react';

export interface PurposeOption {
  id: number;
  description: string;
  tenant_id: number;
}

interface PurposeSelectProps {
  purposes: PurposeOption[];
  value: string;
  tenantId: number | null;
  token: string;
  onChange: (value: string) => void;
  onCreated: (purpose: PurposeOption) => void;
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
  return 'Não foi possível adicionar a finalidade.';
}

export function PurposeSelect({
  purposes,
  value,
  tenantId,
  token,
  onChange,
  onCreated,
}: PurposeSelectProps) {
  const [description, setDescription] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const trimmedDescription = description.trim();
  const existingPurpose = purposes.find(
    (purpose) =>
      purpose.tenant_id === tenantId &&
      purpose.description.localeCompare(trimmedDescription, undefined, {
        sensitivity: 'accent',
      }) === 0,
  );

  async function addPurpose() {
    if (!tenantId || !trimmedDescription) return;

    setSaving(true);
    setError(null);
    setNotice(null);
    try {
      if (existingPurpose) {
        onChange(String(existingPurpose.id));
        setDescription('');
        setNotice('A finalidade existente foi selecionada.');
        return;
      }

      const response = await fetch(`${apiBaseUrl}/purposes`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          description: trimmedDescription,
          tenant_id: tenantId,
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(responseError(data));

      const purpose = data?.mydetails as PurposeOption | undefined;
      if (
        !purpose ||
        typeof purpose.id !== 'number' ||
        typeof purpose.description !== 'string' ||
        typeof purpose.tenant_id !== 'number'
      ) {
        throw new Error('A API retornou dados em formato inesperado.');
      }

      onCreated(purpose);
      onChange(String(purpose.id));
      setDescription('');
      setNotice('Finalidade adicionada e selecionada.');
    } catch (saveError) {
      setError(
        saveError instanceof Error
          ? saveError.message
          : 'Não foi possível adicionar a finalidade.',
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="flex flex-col gap-2 text-sm font-medium text-zinc-700">
      <label htmlFor="reservation-purpose">Finalidade</label>
      <select
        className="rounded-lg border border-zinc-300 bg-white px-3 py-2.5"
        id="reservation-purpose"
        onChange={(event) => onChange(event.target.value)}
        required
        value={value}
      >
        <option value="">Selecione uma finalidade</option>
        {purposes.map((purpose) => (
          <option key={purpose.id} value={purpose.id}>
            {purpose.description}
          </option>
        ))}
      </select>
      <div className="flex flex-col gap-2 sm:flex-row">
        <input
          aria-label="Nova finalidade"
          className="min-w-0 flex-1 rounded-lg border border-zinc-300 px-3 py-2.5"
          disabled={!tenantId || saving}
          onChange={(event) => {
            setDescription(event.target.value);
            setError(null);
            setNotice(null);
          }}
          onKeyDown={(event) => {
            if (event.key === 'Enter') {
              event.preventDefault();
              void addPurpose();
            }
          }}
          placeholder="Digite uma finalidade para adicionar"
          value={description}
        />
        <button
          className="rounded-lg border border-blue-700 px-4 py-2.5 font-semibold text-blue-700 hover:bg-blue-50 disabled:cursor-not-allowed disabled:opacity-50"
          disabled={!tenantId || !trimmedDescription || saving}
          onClick={() => void addPurpose()}
          type="button"
        >
          {saving
            ? 'Salvando…'
            : existingPurpose
              ? 'Usar existente'
              : 'Adicionar'}
        </button>
      </div>
      {!tenantId && (
        <p className="text-xs font-normal text-zinc-500">
          Selecione um artefato antes de adicionar uma finalidade.
        </p>
      )}
      {error && <p className="text-xs font-normal text-red-700" role="alert">{error}</p>}
      {notice && <p className="text-xs font-normal text-green-700" role="status">{notice}</p>}
    </div>
  );
}
