'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { apiList, formatCurrency, formatDate } from '../lib/api';
import { resourcesBySlug, type ResourceConfig } from '../lib/farm-config';

type RecordData = Record<string, unknown> & { id: number };

function sumField(records: RecordData[], field: string): number {
  return records.reduce((sum, record) => sum + (Number(record[field]) || 0), 0);
}

function fetchDashboardData() {
  return Promise.all([
    apiList<RecordData>('/codornas'),
    apiList<RecordData>('/lotes'),
    apiList<RecordData>('/producao-ovos'),
    apiList<RecordData>('/vendas'),
  ]).then(([birds, lots, eggs, sales]) => ({ birds, lots, eggs, sales }));
}

function MetricCard({ label, value, note, icon, tone }: { label: string; value: string; note: string; icon: string; tone: string }) {
  return <article className="metric-card"><div className={`metric-icon ${tone}`} aria-hidden="true">{icon}</div><div><p>{label}</p><strong>{value}</strong><span>{note}</span></div></article>;
}

export function DashboardPage() {
  const [data, setData] = useState<{ birds: RecordData[]; lots: RecordData[]; eggs: RecordData[]; sales: RecordData[] } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  async function loadDashboard() {
    setLoading(true);
    setError('');
    try {
      setData(await fetchDashboardData());
    } catch (loadError) {
      setData(null);
      setError(loadError instanceof Error ? loadError.message : 'Não foi possível carregar os indicadores.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    let active = true;
    fetchDashboardData()
      .then((result) => { if (active) setData(result); })
      .catch((loadError: unknown) => {
        if (!active) return;
        setData(null);
        setError(loadError instanceof Error ? loadError.message : 'Não foi possível carregar os indicadores.');
      })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  const quickLinks = [
    { slug: 'codornas', icon: '♧', note: 'Identificação e plantel' },
    { slug: 'producao-ovos', icon: '◉', note: 'Coleta e produção' },
    { slug: 'alimentacoes', icon: '◌', note: 'Rotina de nutrição' },
    { slug: 'despesas', icon: 'R$', note: 'Custos da criação' },
  ];

  return (
    <main className="page-main dashboard-main">
      <header className="dashboard-welcome">
        <div><p className="eyebrow">Visão geral da propriedade</p><h1>Sua criação, em foco <span aria-hidden="true">☀</span></h1><p className="page-description">Acompanhe os dados da sua criação de codornas em um só lugar.</p></div>
        <div className="today-label"><span className="today-dot" />Indicadores da propriedade</div>
      </header>

      {error && <div className="alert alert-error" role="alert"><span>{error}</span><button className="button button-secondary" onClick={() => void loadDashboard()} type="button">Tentar novamente</button></div>}

      <section aria-label="Indicadores da criação" className="metrics-grid">
        <MetricCard label="Codornas cadastradas" value={loading || !data ? '—' : new Intl.NumberFormat('pt-BR').format(data.birds.length)} note="Aves no cadastro" icon="♧" tone="metric-green" />
        <MetricCard label="Lotes ativos" value={loading || !data ? '—' : new Intl.NumberFormat('pt-BR').format(data.lots.filter((lot) => String(lot.status).toLowerCase() === 'ativo').length)} note="Status ativo no cadastro" icon="▦" tone="metric-brown" />
        <MetricCard label="Ovos registrados" value={loading || !data ? '—' : new Intl.NumberFormat('pt-BR').format(sumField(data.eggs, 'quantidade'))} note="Soma dos registros de produção" icon="◉" tone="metric-amber" />
        <MetricCard label="Total em vendas" value={loading || !data ? '—' : formatCurrency(sumField(data.sales, 'valor_total'))} note="Soma dos valores cadastrados" icon="R$" tone="metric-olive" />
      </section>

      <div className="dashboard-grid">
        <section className="panel overview-panel">
          <div className="section-heading"><div><p className="eyebrow">Acesso rápido</p><h2>Rotina da criação</h2></div><span className="section-mark" aria-hidden="true">✦</span></div>
          <div className="quick-links">
            {quickLinks.map((item) => {
              const resource = resourcesBySlug[item.slug];
              return <Link className="quick-link" href={`/${item.slug}`} key={item.slug}><span className="quick-icon" aria-hidden="true">{item.icon}</span><span><strong>{resource.title}</strong><small>{item.note}</small></span><span aria-hidden="true" className="quick-arrow">↗</span></Link>;
            })}
          </div>
        </section>

        <section className="panel recent-panel">
          <div className="section-heading"><div><p className="eyebrow">Acompanhe</p><h2>Produção recente</h2></div><Link className="text-link" href="/producao-ovos">Ver produção <span aria-hidden="true">→</span></Link></div>
          {loading ? <div className="loading-state"><span className="spinner" /> Carregando dados…</div> : data?.eggs.length ? (
            <div className="recent-list">{[...data.eggs].sort((a, b) => String(b.data_producao).localeCompare(String(a.data_producao))).slice(0, 5).map((egg) => <div className="recent-row" key={egg.id}><span className="recent-egg" aria-hidden="true">◉</span><div><strong>{new Intl.NumberFormat('pt-BR').format(Number(egg.quantidade) || 0)} ovos</strong><small>Registro #{egg.id}</small></div><time>{formatDate(egg.data_producao)}</time></div>)}</div>
          ) : <div className="empty-inline"><span aria-hidden="true">◉</span><p>{error ? 'Os dados de produção não estão disponíveis.' : 'Nenhum registro de produção encontrado.'}</p>{!error && <Link className="text-link" href="/producao-ovos">Registrar produção →</Link>}</div>}
        </section>
      </div>

      <section className="panel module-panel">
        <div className="section-heading"><div><p className="eyebrow">Gestão completa</p><h2>Módulos do sistema</h2></div><span className="muted-count">25 módulos</span></div>
        <div className="module-chips">
          {Object.values(resourcesBySlug).map((resource: ResourceConfig) => <Link className="module-chip" href={`/${resource.slug}`} key={resource.slug}>{resource.title}<span aria-hidden="true">↗</span></Link>)}
        </div>
      </section>
      <p className="data-note">Os indicadores são calculados exclusivamente a partir dos registros retornados pela API configurada.</p>
    </main>
  );
}
