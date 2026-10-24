import unittest
from unittest.mock import Mock, patch

from siraback.services.tenant import create_tenant, get_first_tenant, get_tenants


class TenantServiceTests(unittest.TestCase):

    # informando o caminho completo dos itens a serem usados
    @patch("siraback.services.tenant.db.session.commit")
    @patch("siraback.services.tenant.db.session.add")
    @patch("siraback.services.tenant.Tenant")
    def test_create_tenant_adds_and_commits_tenant(
        self,
        tenant_model: Mock,
        add: Mock,
        commit: Mock,
    ) -> None:
        # definindo os dados
        data = {"name": "IFC Campus Blumenau"}
        # definindo o retorno
        tenant = tenant_model.return_value
        # executando a ação a ser testada
        result = create_tenant(data)

        # fazendo as verificações
        tenant_model.assert_called_once_with(name="IFC Campus Blumenau")
        add.assert_called_once_with(tenant)
        commit.assert_called_once_with()
        self.assertIs(result, tenant)

    @patch("siraback.services.tenant.db.session.commit")
    @patch("siraback.services.tenant.db.session.add")
    @patch("siraback.services.tenant.Tenant")
    def test_create_tenant_rejects_empty_name(
        self,
        tenant_model: Mock,
        add: Mock,
        commit: Mock,
    ) -> None:
        with self.assertRaisesRegex(ValueError, "non-empty string"):
            create_tenant({"name": ""})

        tenant_model.assert_not_called()
        add.assert_not_called()
        commit.assert_not_called()


    @patch("siraback.services.tenant.Tenant")
    def test_get_tenants_returns_all_tenants(self, tenant_model: Mock) -> None:
        
        tenants = [Mock(), Mock()]
        tenant_model.query.all.return_value = tenants

        # executando a ação a ser testada
        result = get_tenants()

        tenant_model.query.all.assert_called_once_with()
        self.assertIs(result, tenants)

    @patch("siraback.services.tenant.Tenant")
    def test_get_first_tenant_returns_lowest_id_tenant(
        self,
        tenant_model: Mock,
    ) -> None:
        tenant = Mock()
        tenant_model.query.order_by.return_value.first.return_value = tenant

        result = get_first_tenant()

        tenant_model.query.order_by.assert_called_once_with(tenant_model.id)
        self.assertIs(result, tenant)


if __name__ == "__main__":
    unittest.main()
