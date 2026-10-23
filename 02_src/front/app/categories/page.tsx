import { RecordsPage } from '../components/records-page';

export default function CategoriesPage() {
  return (
    <RecordsPage
      config={{
        endpoint: '/categories',
        title: 'Categorias',
        description: 'Consulte as categorias disponíveis e seus registros.',
        fields: [
          { name: 'name', label: 'Nome', kind: 'text', required: true },
          { name: 'tenant_id', label: 'Organização', kind: 'tenant', required: true },
        ],
        columns: [
          { key: 'id', label: 'ID' },
          { key: 'name', label: 'Nome' },
          { key: 'tenant_id', label: 'Organização (ID)' },
          { key: 'created_at', label: 'Criada em' },
        ],
      }}
    />
  );
}
