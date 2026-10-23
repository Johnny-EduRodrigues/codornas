import { RecordsPage } from '../components/records-page';

export default function ArtifactsPage() {
  return (
    <RecordsPage
      config={{
        endpoint: '/artifacts',
        title: 'Artefatos',
        description: 'Consulte os artefatos cadastrados.',
        fields: [
          { name: 'name', label: 'Nome', kind: 'text', required: true },
          { name: 'tenant_id', label: 'Organização', kind: 'tenant', required: true },
          { name: 'restrict', label: 'Acesso restrito', kind: 'checkbox', defaultValue: false },
          { name: 'active', label: 'Artefato ativo', kind: 'checkbox', defaultValue: true },
        ],
        columns: [
          { key: 'id', label: 'ID' },
          { key: 'name', label: 'Nome' },
          { key: 'tenant_id', label: 'Organização (ID)' },
          { key: 'restrict', label: 'Acesso restrito' },
          { key: 'active', label: 'Ativo' },
          { key: 'created_at', label: 'Criado em' },
        ],
      }}
    />
  );
}
