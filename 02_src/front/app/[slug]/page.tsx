import { Suspense } from 'react';
import { ResourcePage } from '../components/resource-page';

export default function ResourceRoute({ params }: { params: Promise<{ slug: string }> }) {
  return (
    <Suspense fallback={<main className="page-main"><div className="loading-state"><span className="spinner" /> Carregando módulo…</div></main>}>
      {params.then(({ slug }) => <ResourcePage key={slug} slug={slug} />)}
    </Suspense>
  );
}
