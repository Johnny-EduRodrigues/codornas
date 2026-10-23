import { RecordsPage } from '../components/records-page';

export default function GroupsPage() {
  return (
    <RecordsPage
      config={{
        endpoint: '/groups',
        title: 'Grupos',
        description: 'Consulte os grupos e suas organizações.',
        fields: [
          { name: 'acronym', label: 'Sigla', kind: 'text', required: true },
          { name: 'name', label: 'Nome', kind: 'text', required: true },
          { name: 'tenant_id', label: 'Organização', kind: 'tenant', required: true },
          { name: 'active', label: 'Grupo ativo', kind: 'checkbox', defaultValue: true },
          { name: 'obs', label: 'Observações', kind: 'textarea' },
          { name: 'color', label: 'Cor', kind: 'text' },
        ],
        columns: [
          { key: 'id', label: 'ID' },
          { key: 'acronym', label: 'Sigla' },
          { key: 'name', label: 'Nome' },
          { key: 'tenant_id', label: 'Organização (ID)' },
          { key: 'active', label: 'Ativo' },
          { key: 'color', label: 'Cor' },
        ],
      }}
    />
  );
}
