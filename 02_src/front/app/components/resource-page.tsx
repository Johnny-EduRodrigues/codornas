'use client';

import Link from 'next/link';
import { type FormEvent, useCallback, useEffect, useMemo, useState } from 'react';
import { apiList, apiRequest, formatCurrency, formatDate, formatDateTime } from '../lib/api';
import { recordLabel, resourcesBySlug, type FieldConfig, type ResourceConfig } from '../lib/farm-config';

type RecordData = Record<string, unknown> & { id: number };
type FormData = Record<string, string | boolean>;
type RelatedData = Record<string, RecordData[]>;

async function fetchResourceData(config: ResourceConfig): Promise<{ records: RecordData[]; related: RelatedData }> {
  const relatedSlugs = [...new Set(config.fields.flatMap((field) => field.relation ? [field.relation] : []))];
  const [records, ...relatedLists] = await Promise.all([
    apiList<RecordData>(config.endpoint),
    ...relatedSlugs.map((relatedSlug) => apiList<RecordData>(resourcesBySlug[relatedSlug].endpoint)),
  ]);
  return {
    records,
    related: Object.fromEntries(relatedSlugs.map((relatedSlug, index) => [relatedSlug, relatedLists[index]])),
  };
}

function initialForm(config: ResourceConfig): FormData {
  return Object.fromEntries(
    config.fields.map((field) => {
      if (field.defaultValue !== undefined) return [field.name, field.defaultValue];
      if (field.kind === 'boolean') return [field.name, false];
      if (field.kind === 'date' && field.required) {
        const now = new Date();
        return [field.name, `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`];
      }
      if (field.kind === 'datetime-local') {
        const now = new Date();
        return [field.name, new Date(now.getTime() - now.getTimezoneOffset() * 60_000).toISOString().slice(0, 16)];
      }
      return [field.name, ''];
    }),
  );
}

function inputValue(field: FieldConfig, value: unknown): string | boolean {
  if (field.kind === 'boolean') return value === true;
  if (value === null || value === undefined) return '';
  if (field.kind === 'datetime-local' && typeof value === 'string') {
    const date = new Date(value);
    if (!Number.isNaN(date.getTime())) {
      const local = new Date(date.getTime() - date.getTimezoneOffset() * 60_000);
      return local.toISOString().slice(0, 16);
    }
  }
  return String(value);
}

function displayValue(config: ResourceConfig, fieldName: string, value: unknown, related: RelatedData): string {
  if (value === null || value === undefined || value === '') return '—';
  const field = config.fields.find((item) => item.name === fieldName);
  if (field?.relation) {
    const relatedConfig = resourcesBySlug[field.relation];
    const match = related[field.relation]?.find((record) => String(record.id) === String(value));
    return match && relatedConfig ? recordLabel(match, relatedConfig) : `#${String(value)}`;
  }
  if (field?.kind === 'date' || fieldName.startsWith('data_') || fieldName === 'proxima_aplicacao') return formatDate(value);
  if (field?.kind === 'datetime-local' || fieldName.endsWith('_em')) return formatDateTime(value);
  if (fieldName.startsWith('valor') || fieldName.startsWith('custo')) return formatCurrency(value);
  if (typeof value === 'boolean') return value ? 'Sim' : 'Não';
  if (typeof value === 'number') return new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 3 }).format(value);
  return String(value);
}

function columnLabel(config: ResourceConfig, fieldName: string): string {
  const field = config.fields.find((item) => item.name === fieldName);
  if (field) return field.label;
  if (fieldName === 'atualizado_em') return 'Atualizado em';
  return fieldName.replaceAll('_', ' ');
}

export function ResourcePage({ slug }: { slug: string }) {
  const config = resourcesBySlug[slug];
  const [records, setRecords] = useState<RecordData[]>([]);
  const [related, setRelated] = useState<RelatedData>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [activeRecord, setActiveRecord] = useState<number | null>(null);
  const [editorOpen, setEditorOpen] = useState(false);
  const [editLoading, setEditLoading] = useState(false);
  const [deletingRecord, setDeletingRecord] = useState<number | null>(null);
  const [form, setForm] = useState<FormData>(() => config ? initialForm(config) : {});
  const [search, setSearch] = useState('');
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [modalError, setModalError] = useState('');

  const loadData = useCallback(async () => {
    if (!config) return;
    setLoading(true);
    setError('');
    try {
      const result = await fetchResourceData(config);
      setRecords(result.records);
      setRelated(result.related);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Não foi possível carregar os registros.');
    } finally {
      setLoading(false);
    }
  }, [config]);

  useEffect(() => {
    if (!config) return;
    let active = true;
    fetchResourceData(config)
      .then((result) => {
        if (!active) return;
        setRecords(result.records);
        setRelated(result.related);
      })
      .catch((loadError: unknown) => {
        if (!active) return;
        setError(loadError instanceof Error ? loadError.message : 'Não foi possível carregar os registros.');
      })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [config]);

  const filteredRecords = useMemo(() => {
    const query = search.trim().toLocaleLowerCase('pt-BR');
    if (!query || !config) return records;
    return records.filter((record) =>
      Object.entries(record).some(([key, value]) => displayValue(config, key, value, related).toLocaleLowerCase('pt-BR').includes(query)),
    );
  }, [config, records, related, search]);

  if (!config) {
    return <main className="page-main"><div className="empty-state"><h1>Página não encontrada</h1><Link className="button button-primary" href="/">Voltar ao painel</Link></div></main>;
  }

  function openCreate() {
    setActiveRecord(null);
    setEditorOpen(true);
    setEditLoading(false);
    setForm(initialForm(config));
    setModalError('');
    setError('');
    setNotice('');
  }

  async function openEdit(record: RecordData) {
    setError('');
    setNotice('');
    setModalError('');
    setActiveRecord(record.id);
    setEditorOpen(true);
    setEditLoading(true);
    setForm(initialForm(config));
    try {
      const details = await apiRequest<RecordData>(`${config.endpoint}/${record.id}`);
      setForm(Object.fromEntries(config.fields.map((field) => [field.name, inputValue(field, details[field.name])])));
    } catch (editError) {
      setActiveRecord(null);
      setEditorOpen(false);
      setError(editError instanceof Error ? editError.message : 'Não foi possível abrir o registro.');
    } finally {
      setEditLoading(false);
    }
  }

  function updateField(name: string, value: string | boolean) {
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setModalError('');
    try {
      if ((slug === 'alimentacoes' || slug === 'mortalidades') && !form.codorna_id && !form.lote_id) {
        throw new Error('Vincule o registro a uma codorna ou a um lote.');
      }

      const payload: Record<string, string | number | boolean | null> = {};
      for (const field of config.fields) {
        const value = form[field.name];
        if (field.kind === 'boolean') payload[field.name] = value === true;
        else if (typeof value !== 'string' || value.trim() === '') {
          if (field.omitWhenEmpty) continue;
          payload[field.name] = field.required ? '' : null;
        } else if (field.kind === 'number' || field.relation) {
          const number = Number(value);
          if (field.omitWhenZero && number === 0) continue;
          payload[field.name] = number;
        }
        else payload[field.name] = value.trim();
      }

      await apiRequest(
        activeRecord === null ? config.endpoint : `${config.endpoint}/${activeRecord}`,
        { method: activeRecord === null ? 'POST' : 'PUT', body: JSON.stringify(payload) },
      );
      setEditorOpen(false);
      setActiveRecord(null);
      setNotice(activeRecord === null ? 'Registro criado com sucesso.' : 'Registro atualizado com sucesso.');
      setForm(initialForm(config));
      await loadData();
    } catch (saveError) {
      setModalError(saveError instanceof Error ? saveError.message : 'Não foi possível salvar o registro.');
    } finally {
      setSaving(false);
    }
  }

  async function deleteRecord(record: RecordData) {
    const label = recordLabel(record, config);
    if (!window.confirm(`Excluir ${config.singular} “${label}”? Esta ação não pode ser desfeita.`)) return;
    setDeletingRecord(record.id);
    setError('');
    setNotice('');
    try {
      await apiRequest(`${config.endpoint}/${record.id}`, { method: 'DELETE' });
      setNotice(`${config.singular[0].toLocaleUpperCase('pt-BR')}${config.singular.slice(1)} excluído com sucesso.`);
      await loadData();
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : 'Não foi possível excluir o registro.');
    } finally {
      setDeletingRecord(null);
    }
  }

  const editing = activeRecord !== null;

  return (
    <main className="page-main">
      <div className="breadcrumb"><Link href="/">Painel</Link><span>/</span><span>{config.title}</span></div>
      <header className="page-heading">
        <div>
          <p className="eyebrow">{config.group}</p>
          <h1>{config.title}</h1>
          <p className="page-description">{config.description}</p>
        </div>
        <button className="button button-primary" onClick={openCreate} type="button">
          <span aria-hidden="true">＋</span> Novo registro
        </button>
      </header>

      {error && <div className="alert alert-error" role="alert"><span>{error}</span><button aria-label="Fechar mensagem" onClick={() => setError('')} type="button">×</button></div>}
      {notice && <div className="alert alert-success" role="status"><span>{notice}</span><button aria-label="Fechar mensagem" onClick={() => setNotice('')} type="button">×</button></div>}

      <section className="panel records-panel">
        <div className="records-toolbar">
          <div><h2>Registros</h2><p>{loading ? 'Carregando…' : `${filteredRecords.length} de ${records.length} ${records.length === 1 ? 'registro' : 'registros'}`}</p></div>
          <div className="toolbar-actions">
            <label className="search-box"><span aria-hidden="true">⌕</span><input aria-label={`Buscar em ${config.title.toLowerCase()}`} onChange={(event) => setSearch(event.target.value)} placeholder="Buscar registros…" type="search" value={search} /></label>
            <button aria-label="Atualizar lista" className="button button-secondary refresh-button" disabled={loading} onClick={() => void loadData()} type="button">↻</button>
          </div>
        </div>

        {loading ? (
          <div className="loading-state"><span className="spinner" /> Carregando dados da API…</div>
        ) : filteredRecords.length === 0 ? (
          <div className="empty-state"><span className="empty-icon" aria-hidden="true">⌕</span><h3>{records.length ? 'Nenhum resultado encontrado' : 'Ainda não há registros'}</h3><p>{records.length ? 'Tente outra busca.' : `Cadastre o primeiro ${config.singular} para começar.`}</p>{!records.length && <button className="button button-secondary" onClick={openCreate} type="button">Cadastrar {config.singular}</button>}</div>
        ) : (
          <div className="table-scroll">
            <table className="data-table">
              <thead><tr>{config.columns.map((column) => <th key={column}>{columnLabel(config, column)}</th>)}<th className="actions-heading">Ações</th></tr></thead>
              <tbody>
                {filteredRecords.map((record) => (
                  <tr key={record.id}>
                    {config.columns.map((column) => <td key={column} title={displayValue(config, column, record[column], related)}>{displayValue(config, column, record[column], related)}</td>)}
                    <td className="row-actions">
                      <button aria-label={`Editar ${recordLabel(record, config)}`} className="icon-button" disabled={deletingRecord === record.id} onClick={() => void openEdit(record)} title="Editar" type="button">✎</button>
                      <button aria-label={`Excluir ${recordLabel(record, config)}`} className="icon-button icon-danger" disabled={deletingRecord === record.id} onClick={() => void deleteRecord(record)} title="Excluir" type="button">{deletingRecord === record.id ? '…' : '⌫'}</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {editorOpen && editLoading && <div className="modal-backdrop"><div aria-live="polite" className="modal-loading"><span className="spinner" /> Carregando registro…</div></div>}
      {editorOpen && !editLoading && form && (
        <div className="modal-backdrop" onMouseDown={(event) => { if (event.target === event.currentTarget && !saving) { setEditorOpen(false); setActiveRecord(null); } }}>
          <section aria-labelledby="record-form-title" aria-modal="true" className="modal" role="dialog">
            <header className="modal-header"><div><p className="eyebrow">{editing ? 'Editar cadastro' : 'Novo cadastro'}</p><h2 id="record-form-title">{editing ? 'Editar ' : 'Cadastrar '}{config.singular}</h2></div><button aria-label="Fechar" className="icon-button modal-close" disabled={saving} onClick={() => { setEditorOpen(false); setActiveRecord(null); }} type="button">×</button></header>
            {modalError && <div className="alert alert-error" role="alert">{modalError}</div>}
            <form key={`${slug}-${activeRecord ?? 'new'}`} onSubmit={handleSubmit}>
              <div className="form-grid">
                {config.fields.map((field) => {
                  const className = `form-field${field.kind === 'textarea' ? ' form-field-wide' : ''}`;
                  const value = form[field.name];
                  if (field.kind === 'boolean') return <label className={`${className} checkbox-field`} key={field.name}><input checked={value === true} onChange={(event) => updateField(field.name, event.target.checked)} type="checkbox" /><span>{field.label}</span></label>;
                  if (field.kind === 'textarea') return <label className={className} key={field.name}><span>{field.label}</span><textarea onChange={(event) => updateField(field.name, event.target.value)} required={field.required} value={String(value ?? '')} /></label>;
                  if (field.kind === 'select') {
                    const options = field.relation ? related[field.relation] ?? [] : [];
                    const relatedConfig = field.relation ? resourcesBySlug[field.relation] : undefined;
                    const selectedMissing = field.relation && value && !options.some((record) => String(record.id) === String(value));
                    return <label className={className} key={field.name}><span>{field.label}{field.required && <i aria-hidden="true"> *</i>}</span><select onChange={(event) => updateField(field.name, event.target.value)} required={field.required} value={String(value ?? '')}><option value="">{field.required ? 'Selecione…' : 'Sem vínculo'}</option>{field.options?.map((option) => <option key={option} value={option}>{option.replaceAll('_', ' ')}</option>)}{field.relation && options.map((record) => <option key={record.id} value={record.id}>{relatedConfig ? recordLabel(record, relatedConfig) : `#${record.id}`}</option>)}{selectedMissing && <option value={String(value)}>Registro #{String(value)} (fora da lista)</option>}</select></label>;
                  }
                  return <label className={className} key={field.name}><span>{field.label}{field.required && <i aria-hidden="true"> *</i>}</span><input list={field.options ? `${slug}-${field.name}-options` : undefined} min={field.min} onChange={(event) => updateField(field.name, event.target.value)} required={field.required} step={field.step} type={field.kind} value={String(value ?? '')} />{field.options && <datalist id={`${slug}-${field.name}-options`}>{field.options.map((option) => <option key={option} value={option} />)}</datalist>}</label>;
                })}
              </div>
              <footer className="modal-footer"><span className="form-hint"><i aria-hidden="true">*</i> Campos obrigatórios</span><div><button className="button button-secondary" disabled={saving} onClick={() => { setEditorOpen(false); setActiveRecord(null); }} type="button">Cancelar</button><button className="button button-primary" disabled={saving} type="submit">{saving ? <><span className="spinner spinner-light" /> Salvando…</> : editing ? 'Salvar alterações' : 'Cadastrar'}</button></div></footer>
            </form>
          </section>
        </div>
      )}
    </main>
  );
}
