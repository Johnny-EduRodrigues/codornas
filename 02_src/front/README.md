# Sistema de Gerenciamento de Criação de Codornas

Frontend Next.js para administrar o plantel, manejo, produção, vendas, compras e despesas. A interface em português usa as respostas reais da API e oferece busca e operações de consulta, criação, edição e exclusão para os 25 recursos.

## Configuração

Na pasta `02_src/front`, copie `.env.example` para `.env.local` e ajuste a URL da API:

```env
NEXT_PUBLIC_API_URL=http://localhost:5000
```

O valor deve ser a URL base do backend, sem uma rota de recurso. O frontend acrescenta os caminhos como `/codornas`, `/racas` e `/producao-ovos`. Reinicie o servidor Next.js depois de alterar variáveis `NEXT_PUBLIC_*`.

Para a página legada de login Google, informe também `NEXT_PUBLIC_GOOGLE_CLIENT_ID`.

## Instalação e execução

```bash
npm ci
npm run dev
```

Acesse `http://localhost:3000`. Os endpoints precisam estar disponíveis no navegador e aceitar requisições CORS da origem do frontend.

## Verificações

```bash
npm run lint
npx tsc --noEmit
npm run build
```
