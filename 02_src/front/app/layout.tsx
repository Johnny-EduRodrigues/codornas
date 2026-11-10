import type { Metadata } from "next";
import { Suspense } from "react";
import type { ReactNode } from "react";
import "./globals.css";

import { AppNavigation } from './components/app-navigation';
import { Providers } from './providers';

export const metadata: Metadata = {
  title: "Quinta Verde | Gestão de Criação de Codornas",
  description: "Painel de gerenciamento da criação de codornas.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>
        <Providers>
          <div className="app-shell">
            <Suspense fallback={<aside aria-hidden="true" className="sidebar" />}>
              <AppNavigation />
            </Suspense>
            <div className="app-content">
              <header className="topbar"><span className="topbar-caption">Sistema de gerenciamento</span><span className="topbar-right"><span aria-hidden="true">⌁</span> Criação rural</span></header>
              {children}
            </div>
          </div>
        </Providers>
      </body>
    </html>
  );
}
