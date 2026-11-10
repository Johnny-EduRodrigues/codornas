'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { resourceGroups, resourcesBySlug } from '../lib/farm-config';

export function AppNavigation() {
  const pathname = usePathname();

  return (
    <aside className="sidebar">
      <Link aria-label="Ir ao painel inicial" className="brand" href="/">
        <span aria-hidden="true" className="brand-mark">C</span>
        <span><strong>Quinta Verde</strong><small>Gestão de codornas</small></span>
      </Link>
      <nav aria-label="Navegação principal" className="sidebar-menu">
        <Link aria-current={pathname === '/' ? 'page' : undefined} className={`nav-home${pathname === '/' ? ' active' : ''}`} href="/">
          <span aria-hidden="true">⌂</span> Painel geral
        </Link>
        {resourceGroups.map((group) => (
          <section aria-label={group.title} className="nav-group" key={group.title}>
            <div className="nav-group-heading"><span>{group.title}</span><small>{group.description}</small></div>
            <div className="nav-group-links">
              {group.slugs.map((slug) => {
                const resource = resourcesBySlug[slug];
                const active = pathname === `/${slug}`;
                return <Link aria-current={active ? 'page' : undefined} className={`nav-link${active ? ' active' : ''}`} href={`/${slug}`} key={slug}><span aria-hidden="true" className="nav-leaf">·</span>{resource.title}</Link>;
              })}
            </div>
          </section>
        ))}
      </nav>
      <div className="sidebar-footer"><span aria-hidden="true" className="footer-sprout">✳</span><span><strong>Produção consciente</strong><small>Cuidado em cada etapa</small></span></div>
    </aside>
  );
}
