const apiBaseUrl = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000').replace(/\/+$/, '');

export class ApiError extends Error {
  status: number;

  constructor(message: string, status = 0) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

export async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl}${path}`, {
      ...init,
      cache: 'no-store',
      headers: {
        ...(init?.body ? { 'Content-Type': 'application/json' } : {}),
        ...init?.headers,
      },
    });
  } catch {
    throw new ApiError(`Não foi possível conectar à API em ${apiBaseUrl}. Verifique se o servidor está disponível.`);
  }

  let body: unknown;
  try {
    body = await response.json();
  } catch {
    throw new ApiError('A API retornou uma resposta inválida.', response.status);
  }

  if (!response.ok) {
    const details =
      typeof body === 'object' && body !== null && 'detalhes' in body
        ? body.detalhes
        : null;
    throw new ApiError(
      typeof details === 'string' ? details : `A solicitação não foi concluída (HTTP ${response.status}).`,
      response.status,
    );
  }

  if (typeof body !== 'object' || body === null || !('resultado' in body) || !('detalhes' in body)) {
    throw new ApiError('A API retornou dados em formato inesperado.', response.status);
  }
  if (body.resultado !== 'ok') {
    throw new ApiError(typeof body.detalhes === 'string' ? body.detalhes : 'A solicitação não foi concluída.', response.status);
  }
  return body.detalhes as T;
}

export function apiList<T>(endpoint: string): Promise<T[]> {
  const loadPages = async () => {
    const records: T[] = [];
    let offset = 0;
    while (true) {
      const page = await apiRequest<T[]>(`${endpoint}?limit=200&offset=${offset}`);
      records.push(...page);
      if (page.length < 200) return records;
      offset += page.length;
    }
  };
  return loadPages();
}

export function formatDate(value: unknown): string {
  if (typeof value !== 'string' || !value) return '—';
  const date = new Date(value.length === 10 ? `${value}T12:00:00` : value);
  return Number.isNaN(date.getTime()) ? value : new Intl.DateTimeFormat('pt-BR').format(date);
}

export function formatDateTime(value: unknown): string {
  if (typeof value !== 'string' || !value) return '—';
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? value
    : new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeStyle: 'short' }).format(date);
}

export function formatCurrency(value: unknown): string {
  const amount = typeof value === 'number' ? value : Number(value);
  if (!Number.isFinite(amount)) return '—';
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(amount);
}
