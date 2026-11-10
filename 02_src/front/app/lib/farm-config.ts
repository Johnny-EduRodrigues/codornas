export type FieldKind = 'text' | 'textarea' | 'number' | 'date' | 'datetime-local' | 'select' | 'boolean';

export interface FieldConfig {
  name: string;
  label: string;
  kind: FieldKind;
  required?: boolean;
  relation?: string;
  options?: string[];
  defaultValue?: string | boolean;
  step?: string;
  min?: number;
  omitWhenEmpty?: boolean;
  omitWhenZero?: boolean;
}

export interface ResourceConfig {
  slug: string;
  endpoint: string;
  title: string;
  singular: string;
  description: string;
  group: string;
  labelField: string;
  fields: FieldConfig[];
  columns: string[];
}

const field = (
  name: string,
  label: string,
  kind: FieldKind = 'text',
  options: Omit<FieldConfig, 'name' | 'label' | 'kind'> = {},
): FieldConfig => ({ name, label, kind, ...options });

export const resourceGroups = [
  { title: 'Plantel', description: 'Aves e estrutura', slugs: ['codornas', 'racas', 'lotes', 'galpoes', 'gaiolas'] },
  { title: 'Manejo', description: 'Nutrição e saúde', slugs: ['alimentos', 'estoque-alimentos', 'alimentacoes', 'veterinarios', 'consultas-veterinarias', 'vacinas', 'vacinacoes', 'pesagens', 'mortalidades'] },
  { title: 'Produção', description: 'Reprodução e ovos', slugs: ['reproducoes', 'incubacoes', 'producao-ovos', 'ecloses'] },
  { title: 'Comercial', description: 'Clientes e movimentações', slugs: ['clientes', 'vendas', 'itens-venda', 'fornecedores', 'compras', 'itens-compra'] },
  { title: 'Financeiro', description: 'Despesas da criação', slugs: ['despesas'] },
];

export const resources: ResourceConfig[] = [
  { slug: 'codornas', endpoint: '/codornas', title: 'Codornas', singular: 'codorna', description: 'Identifique e acompanhe cada ave do plantel.', group: 'Plantel', labelField: 'codigo', fields: [
    field('codigo', 'Código', 'text', { required: true }), field('sexo', 'Sexo', 'text', { options: ['femea', 'macho'] }), field('data_nascimento', 'Data de nascimento', 'date'), field('peso_atual', 'Peso atual (g)', 'number', { step: '0.01', min: 0.01 }), field('status', 'Status', 'text', { required: true, options: ['ativa', 'vendida', 'morta'], defaultValue: 'ativa' }), field('raca_id', 'Raça', 'select', { relation: 'racas' }), field('lote_id', 'Lote', 'select', { relation: 'lotes' }), field('gaiola_id', 'Gaiola', 'select', { relation: 'gaiolas' }),
  ], columns: ['codigo', 'sexo', 'data_nascimento', 'peso_atual', 'status', 'raca_id'] },
  { slug: 'racas', endpoint: '/racas', title: 'Raças', singular: 'raça', description: 'Mantenha as raças e características do plantel organizadas.', group: 'Plantel', labelField: 'nome', fields: [
    field('nome', 'Nome', 'text', { required: true }), field('descricao', 'Descrição', 'textarea'), field('origem', 'Origem'), field('peso_medio', 'Peso médio (g)', 'number', { step: '0.01', min: 0.01 }),
  ], columns: ['nome', 'origem', 'peso_medio', 'descricao'] },
  { slug: 'lotes', endpoint: '/lotes', title: 'Lotes', singular: 'lote', description: 'Organize o plantel por lotes, data de criação e localização.', group: 'Plantel', labelField: 'codigo', fields: [
    field('codigo', 'Código', 'text', { required: true }), field('data_criacao', 'Data de criação', 'date', { required: true }), field('quantidade_inicial', 'Quantidade inicial', 'number', { required: true, min: 1, step: '1' }), field('status', 'Status', 'text', { required: true, options: ['ativo', 'encerrado'], defaultValue: 'ativo' }), field('raca_id', 'Raça', 'select', { relation: 'racas' }), field('galpao_id', 'Galpão', 'select', { relation: 'galpoes' }),
  ], columns: ['codigo', 'data_criacao', 'quantidade_inicial', 'status', 'galpao_id'] },
  { slug: 'galpoes', endpoint: '/galpoes', title: 'Galpões', singular: 'galpão', description: 'Cadastre os espaços de criação e suas capacidades.', group: 'Plantel', labelField: 'nome', fields: [
    field('nome', 'Nome', 'text', { required: true }), field('localizacao', 'Localização'), field('capacidade', 'Capacidade (aves)', 'number', { step: '1', min: 1 }),
  ], columns: ['nome', 'localizacao', 'capacidade'] },
  { slug: 'gaiolas', endpoint: '/gaiolas', title: 'Gaiolas', singular: 'gaiola', description: 'Controle a capacidade e o galpão de cada gaiola.', group: 'Plantel', labelField: 'codigo', fields: [
    field('codigo', 'Código', 'text', { required: true }), field('capacidade', 'Capacidade (aves)', 'number', { required: true, min: 1, step: '1' }), field('galpao_id', 'Galpão', 'select', { relation: 'galpoes', required: true }), field('lote_id', 'Lote', 'select', { relation: 'lotes' }),
  ], columns: ['codigo', 'capacidade', 'galpao_id', 'lote_id'] },
  { slug: 'alimentos', endpoint: '/alimentos', title: 'Alimentos', singular: 'alimento', description: 'Cadastre os alimentos utilizados na criação.', group: 'Manejo', labelField: 'nome', fields: [
    field('nome', 'Nome', 'text', { required: true }), field('tipo', 'Tipo'), field('unidade', 'Unidade', 'text', { required: true, defaultValue: 'kg' }), field('proteina_percentual', 'Proteína (%)', 'number', { step: '0.01', min: 0.01 }), field('ativo', 'Ativo', 'boolean', { defaultValue: true }),
  ], columns: ['nome', 'tipo', 'unidade', 'proteina_percentual', 'ativo'] },
  { slug: 'estoque-alimentos', endpoint: '/estoque-alimentos', title: 'Estoque de alimentos', singular: 'estoque', description: 'Acompanhe quantidades disponíveis e níveis mínimos.', group: 'Manejo', labelField: 'alimento_id', fields: [
    field('alimento_id', 'Alimento', 'select', { relation: 'alimentos', required: true }), field('quantidade', 'Quantidade', 'number', { required: true, step: '0.001', min: 0.001 }), field('quantidade_minima', 'Quantidade mínima', 'number', { required: true, step: '0.001', min: 0 }),
  ], columns: ['alimento_id', 'quantidade', 'quantidade_minima', 'atualizado_em'] },
  { slug: 'alimentacoes', endpoint: '/alimentacoes', title: 'Alimentações', singular: 'alimentação', description: 'Registre a distribuição de alimento para as aves e lotes.', group: 'Manejo', labelField: 'alimento_id', fields: [
    field('data_hora', 'Data e hora', 'datetime-local', { required: true }), field('quantidade', 'Quantidade', 'number', { required: true, step: '0.001', min: 0.001 }), field('unidade', 'Unidade', 'text', { required: true, defaultValue: 'kg' }), field('alimento_id', 'Alimento', 'select', { relation: 'alimentos', required: true }), field('codorna_id', 'Codorna', 'select', { relation: 'codornas' }), field('lote_id', 'Lote', 'select', { relation: 'lotes' }),
  ], columns: ['data_hora', 'alimento_id', 'quantidade', 'unidade', 'codorna_id', 'lote_id'] },
  { slug: 'fornecedores', endpoint: '/fornecedores', title: 'Fornecedores', singular: 'fornecedor', description: 'Gerencie os contatos de fornecedores da propriedade.', group: 'Comercial', labelField: 'nome', fields: [
    field('nome', 'Nome', 'text', { required: true }), field('documento', 'CPF/CNPJ'), field('email', 'E-mail'), field('telefone', 'Telefone'), field('endereco', 'Endereço'),
  ], columns: ['nome', 'documento', 'telefone', 'email'] },
  { slug: 'veterinarios', endpoint: '/veterinarios', title: 'Veterinários', singular: 'veterinário', description: 'Mantenha os profissionais responsáveis pela saúde do plantel.', group: 'Manejo', labelField: 'nome', fields: [
    field('nome', 'Nome', 'text', { required: true }), field('registro_profissional', 'Registro profissional'), field('telefone', 'Telefone'), field('email', 'E-mail'),
  ], columns: ['nome', 'registro_profissional', 'telefone', 'email'] },
  { slug: 'consultas-veterinarias', endpoint: '/consultas-veterinarias', title: 'Consultas veterinárias', singular: 'consulta veterinária', description: 'Registre atendimentos, diagnósticos e tratamentos.', group: 'Manejo', labelField: 'data_consulta', fields: [
    field('data_consulta', 'Data da consulta', 'date', { required: true }), field('diagnostico', 'Diagnóstico', 'textarea'), field('tratamento', 'Tratamento', 'textarea'), field('custo', 'Custo (R$)', 'number', { step: '0.01', min: 0.01 }), field('codorna_id', 'Codorna', 'select', { relation: 'codornas', required: true }), field('veterinario_id', 'Veterinário', 'select', { relation: 'veterinarios' }),
  ], columns: ['data_consulta', 'codorna_id', 'veterinario_id', 'diagnostico', 'custo'] },
  { slug: 'vacinas', endpoint: '/vacinas', title: 'Vacinas', singular: 'vacina', description: 'Cadastre vacinas e orientações de aplicação.', group: 'Manejo', labelField: 'nome', fields: [
    field('nome', 'Nome', 'text', { required: true }), field('descricao', 'Descrição', 'textarea'), field('dose', 'Dose'), field('intervalo_dias', 'Intervalo (dias)', 'number', { step: '1', min: 0 }),
  ], columns: ['nome', 'dose', 'intervalo_dias', 'descricao'] },
  { slug: 'vacinacoes', endpoint: '/vacinacoes', title: 'Vacinações', singular: 'vacinação', description: 'Acompanhe aplicações realizadas e próximas doses.', group: 'Manejo', labelField: 'data_aplicacao', fields: [
    field('data_aplicacao', 'Data da aplicação', 'date', { required: true }), field('proxima_aplicacao', 'Próxima aplicação', 'date'), field('codorna_id', 'Codorna', 'select', { relation: 'codornas', required: true }), field('vacina_id', 'Vacina', 'select', { relation: 'vacinas', required: true }), field('veterinario_id', 'Veterinário', 'select', { relation: 'veterinarios' }),
  ], columns: ['data_aplicacao', 'codorna_id', 'vacina_id', 'veterinario_id', 'proxima_aplicacao'] },
  { slug: 'reproducoes', endpoint: '/reproducoes', title: 'Reproduções', singular: 'reprodução', description: 'Acompanhe os acasalamentos e o andamento reprodutivo.', group: 'Produção', labelField: 'data_acasalamento', fields: [
    field('data_acasalamento', 'Data do acasalamento', 'date', { required: true }), field('status', 'Status', 'text', { required: true, options: ['planejada', 'em_andamento', 'concluida', 'cancelada'], defaultValue: 'planejada' }), field('observacoes', 'Observações', 'textarea'), field('macho_id', 'Macho', 'select', { relation: 'codornas' }), field('femea_id', 'Fêmea', 'select', { relation: 'codornas' }),
  ], columns: ['data_acasalamento', 'status', 'macho_id', 'femea_id', 'observacoes'] },
  { slug: 'incubacoes', endpoint: '/incubacoes', title: 'Incubações', singular: 'incubação', description: 'Controle os ciclos, parâmetros e previsões de eclosão.', group: 'Produção', labelField: 'data_inicio', fields: [
    field('data_inicio', 'Data de início', 'date', { required: true }), field('data_prevista_eclosao', 'Eclosão prevista', 'date'), field('quantidade_ovos', 'Quantidade de ovos', 'number', { required: true, min: 1, step: '1' }), field('temperatura', 'Temperatura (°C)', 'number', { step: '0.01' }), field('umidade', 'Umidade (%)', 'number', { step: '0.01' }), field('status', 'Status', 'text', { required: true, options: ['em_andamento', 'concluida', 'cancelada'], defaultValue: 'em_andamento' }), field('reproducao_id', 'Reprodução', 'select', { relation: 'reproducoes' }),
  ], columns: ['data_inicio', 'data_prevista_eclosao', 'quantidade_ovos', 'temperatura', 'umidade', 'status'] },
  { slug: 'producao-ovos', endpoint: '/producao-ovos', title: 'Produção de ovos', singular: 'registro de produção', description: 'Registre a coleta diária e perdas de ovos.', group: 'Produção', labelField: 'data_producao', fields: [
    field('data_producao', 'Data da produção', 'date', { required: true }), field('quantidade', 'Ovos coletados', 'number', { required: true, min: 1, step: '1' }), field('quantidade_quebrados', 'Ovos quebrados', 'number', { required: true, min: 0, step: '1', defaultValue: '0' }), field('lote_id', 'Lote', 'select', { relation: 'lotes' }), field('gaiola_id', 'Gaiola', 'select', { relation: 'gaiolas' }),
  ], columns: ['data_producao', 'quantidade', 'quantidade_quebrados', 'lote_id', 'gaiola_id'] },
  { slug: 'vendas', endpoint: '/vendas', title: 'Vendas', singular: 'venda', description: 'Acompanhe as vendas e os respectivos clientes.', group: 'Comercial', labelField: 'data_venda', fields: [
    field('data_venda', 'Data da venda', 'date', { required: true }), field('valor_total', 'Valor total (R$)', 'number', { required: true, step: '0.01', min: 0, defaultValue: '0', omitWhenZero: true }), field('status', 'Status', 'text', { required: true, options: ['aberta', 'concluida', 'cancelada'], defaultValue: 'aberta' }), field('cliente_id', 'Cliente', 'select', { relation: 'clientes' }),
  ], columns: ['data_venda', 'cliente_id', 'valor_total', 'status'] },
  { slug: 'itens-venda', endpoint: '/itens-venda', title: 'Itens de venda', singular: 'item de venda', description: 'Detalhe os produtos, quantidades e valores das vendas.', group: 'Comercial', labelField: 'descricao', fields: [
    field('venda_id', 'Venda', 'select', { relation: 'vendas', required: true }), field('descricao', 'Descrição', 'text', { required: true }), field('quantidade', 'Quantidade', 'number', { required: true, min: 0.001, step: '0.001' }), field('valor_unitario', 'Valor unitário (R$)', 'number', { required: true, min: 0.01, step: '0.01' }), field('codorna_id', 'Codorna', 'select', { relation: 'codornas' }),
  ], columns: ['venda_id', 'descricao', 'quantidade', 'valor_unitario', 'codorna_id'] },
  { slug: 'clientes', endpoint: '/clientes', title: 'Clientes', singular: 'cliente', description: 'Organize os dados de contato dos clientes.', group: 'Comercial', labelField: 'nome', fields: [
    field('nome', 'Nome', 'text', { required: true }), field('documento', 'CPF/CNPJ'), field('email', 'E-mail'), field('telefone', 'Telefone'), field('endereco', 'Endereço'),
  ], columns: ['nome', 'documento', 'telefone', 'email'] },
  { slug: 'despesas', endpoint: '/despesas', title: 'Despesas', singular: 'despesa', description: 'Registre custos e despesas relacionados à criação.', group: 'Financeiro', labelField: 'descricao', fields: [
    field('data_despesa', 'Data da despesa', 'date', { required: true }), field('descricao', 'Descrição', 'text', { required: true }), field('categoria', 'Categoria'), field('valor', 'Valor (R$)', 'number', { required: true, min: 0.01, step: '0.01' }), field('fornecedor_id', 'Fornecedor', 'select', { relation: 'fornecedores' }),
  ], columns: ['data_despesa', 'descricao', 'categoria', 'fornecedor_id', 'valor'] },
  { slug: 'compras', endpoint: '/compras', title: 'Compras', singular: 'compra', description: 'Acompanhe as compras realizadas com fornecedores.', group: 'Comercial', labelField: 'data_compra', fields: [
    field('data_compra', 'Data da compra', 'date', { required: true }), field('valor_total', 'Valor total (R$)', 'number', { required: true, step: '0.01', min: 0, defaultValue: '0', omitWhenZero: true }), field('status', 'Status', 'text', { required: true, options: ['recebida', 'pendente', 'cancelada'], defaultValue: 'recebida' }), field('fornecedor_id', 'Fornecedor', 'select', { relation: 'fornecedores' }),
  ], columns: ['data_compra', 'fornecedor_id', 'valor_total', 'status'] },
  { slug: 'itens-compra', endpoint: '/itens-compra', title: 'Itens de compra', singular: 'item de compra', description: 'Detalhe os itens e custos vinculados a cada compra.', group: 'Comercial', labelField: 'descricao', fields: [
    field('compra_id', 'Compra', 'select', { relation: 'compras', required: true }), field('descricao', 'Descrição', 'text', { required: true }), field('quantidade', 'Quantidade', 'number', { required: true, min: 0.001, step: '0.001' }), field('custo_unitario', 'Custo unitário (R$)', 'number', { required: true, min: 0.01, step: '0.01' }), field('alimento_id', 'Alimento', 'select', { relation: 'alimentos' }),
  ], columns: ['compra_id', 'descricao', 'quantidade', 'custo_unitario', 'alimento_id'] },
  { slug: 'mortalidades', endpoint: '/mortalidades', title: 'Mortalidades', singular: 'mortalidade', description: 'Registre perdas e causas para acompanhar a saúde do plantel.', group: 'Manejo', labelField: 'data_morte', fields: [
    field('data_morte', 'Data da ocorrência', 'date', { required: true }), field('quantidade', 'Quantidade', 'number', { required: true, min: 1, step: '1', defaultValue: '1' }), field('causa', 'Causa'), field('codorna_id', 'Codorna', 'select', { relation: 'codornas' }), field('lote_id', 'Lote', 'select', { relation: 'lotes' }),
  ], columns: ['data_morte', 'quantidade', 'causa', 'codorna_id', 'lote_id'] },
  { slug: 'pesagens', endpoint: '/pesagens', title: 'Pesagens', singular: 'pesagem', description: 'Monitore a evolução de peso das codornas.', group: 'Manejo', labelField: 'data_pesagem', fields: [
    field('data_pesagem', 'Data da pesagem', 'date', { required: true }), field('peso', 'Peso (g)', 'number', { required: true, min: 0.01, step: '0.01' }), field('observacoes', 'Observações', 'textarea'), field('codorna_id', 'Codorna', 'select', { relation: 'codornas', required: true }),
  ], columns: ['data_pesagem', 'codorna_id', 'peso', 'observacoes'] },
  { slug: 'ecloses', endpoint: '/ecloses', title: 'Eclosões', singular: 'eclosão', description: 'Registre os resultados dos ciclos de incubação.', group: 'Produção', labelField: 'data_eclosao', fields: [
    field('data_eclosao', 'Data da eclosão', 'date', { required: true }), field('quantidade_nascidos', 'Nascidos', 'number', { required: true, min: 1, step: '1' }), field('quantidade_nao_eclodidos', 'Não eclodidos', 'number', { required: true, min: 0, step: '1', defaultValue: '0' }), field('incubacao_id', 'Incubação', 'select', { relation: 'incubacoes', required: true }),
  ], columns: ['data_eclosao', 'incubacao_id', 'quantidade_nascidos', 'quantidade_nao_eclodidos'] },
];

export const resourcesBySlug = Object.fromEntries(resources.map((resource) => [resource.slug, resource])) as Record<string, ResourceConfig>;

export function recordLabel(record: Record<string, unknown>, resource: ResourceConfig): string {
  const value = record[resource.labelField];
  if (value !== null && value !== undefined && String(value).trim()) return String(value);
  return `Registro #${String(record.id ?? '')}`;
}
