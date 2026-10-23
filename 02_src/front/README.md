# Configuração

Crie um arquivo .env.development com este conteúdo:

```
NEXT_PUBLIC_API_URL=http://localhost:5000
NEXT_PUBLIC_GOOGLE_CLIENT_ID=XXX
```

O ID do cliente Google deverá ser obtido a partir do [Google Cloud](https://console.cloud.google.com).

# Instalação

Além da instalação comum das bibliotecas (npm install), instale o módulo de autenticação do google: 

```
npm install @react-oauth/google
```

# Execução

Para rodar o front-end, execute:

```
npm run dev
```