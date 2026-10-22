from siraback.extensions import db
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
    
    # Cria instância do modelo e salva no banco
    new = Tenant(name=data['name'])
    db.session.add(new)
    db.session.commit()
    
    return new

def get_tenants():
    """
    Recupera todos os tenants do banco de dados.

    Returns:
        list: Uma lista de objetos Tenant.
    """
    return Tenant.query.all()