from siraback.config import db
from siraback.models.tenant import Tenant

def create_tenant(data):
    """
    Cria um novo tenant no banco de dados.

    Args:
        data (dict): Um dicionário contendo os dados do tenant a ser criado.
                     Deve conter a chave 'name' com o nome do tenant.

    Returns:
        Tenant: O objeto Tenant criado.
    """
    # Cria uma instância do modelo Tenant com os dados fornecidos
    new_tenant = Tenant(name=data['name'])
    
    # Adiciona o novo tenant à sessão do banco de dados
    db.session.add(new_tenant)
    
    # Comita a transação para salvar o novo tenant no banco de dados
    db.session.commit()
    
    return new_tenant

def get_tenants():
    """
    Recupera todos os tenants do banco de dados.

    Returns:
        list: Uma lista de objetos Tenant.
    """
    return Tenant.query.all()