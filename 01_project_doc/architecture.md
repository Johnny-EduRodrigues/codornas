Arquitetura do sistema
----------------------

1) Frontend
- tecnologia: Rect com Next
  - o servidor Next permite o uso de recursos modernos:
    - hidratação de páginas (atualização com base em atualização de dados)
    - carregamento do front-end no cliente de uma só vez

2) Backend
- 3 camadas de código
  - models: classes usando ORM (object relational mapping)
  - services
  - routes
- tecnologia: python com flask
  - usar desde o começo: sqlalchemy, JWT, migration

Observações sobre as regras de negócio:
a) implementar a verificação de conflito de reservas também no banco, para não permitir dados inconsistentes
b) a organização à qual pertence uma reserva pode ser obtida buscando-se à qual organização o artefato reservado pertence
c) uma reserva cancelada deve possuir informações de cancelamento
d) quando uma reserva é editada, cancela-se a reserva anterior e cria-se uma nova, com as informações novas
e) a operação em lote é atômica: ou todas as reservas são criadas/alteradas, ou nenhuma delas é

Observações de implementação:
a) a lista reversa de Observadores de uma reserva vai ser armazenada em uma tabela que contém o usuário e a reserva
b) É possível observar o histório de uma reserva que foi cancelada? COMO?
