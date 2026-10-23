import { RecordsPage } from '../components/records-page';

export default function TenantsPage() {
  return (
    <RecordsPage
      config={{
        endpoint: '/tenants',
        title: 'Organizações',
        description: 'Consulte as organizações cadastradas no sistema.',
        fields: [
          { name: 'name', label: 'Nome da organização', kind: 'text', required: true },
        ],
        columns: [
          { key: 'id', label: 'ID' },
          { key: 'name', label: 'Nome' },
        ],
      }}
    />
  );
}
