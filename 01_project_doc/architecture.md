# Arquitetura do sistema

## Diretrizes de código:
1) O código deve ser legível
- isso leva a um melhor entendimento/compreensão
- deve ser um código legível
2) frameworks usados atualmente no mercado; por exemplo, Vue é mais fácil do que React; mas React é bem mais usado no mercado do que Vue no ano de 2025;
 
## Frontend
- tecnologia: React com Next
  - o servidor Next permite o uso de recursos modernos:
    - hidratação de páginas (atualização com base em atualização de dados)
    - carregamento do front-end no cliente de uma só vez
    - utilizar tailwind na construção dos estilos

1) Backend
- 3 camadas de código
  - models: classes usando ORM (object relational mapping)
  - services
  - routes
- tecnologia: python com flask
  - usar desde o começo: sqlalchemy, JWT, migration
  - considerar uso de bibliotecas que facilitam a integração: flask-login, flask-smorest

Observações sobre as regras de negócio:
a) implementar a verificação de conflito de reservas também no banco, para não permitir dados inconsistentes
b) uma reserva cancelada deve possuir informações de cancelamento
c) quando uma reserva é editada, cancela-se a reserva anterior e cria-se uma nova, com as informações novas
d) a operação em lote é atômica: ou todas as reservas são criadas/alteradas, ou nenhuma delas é

Observações de implementação:
a) a lista reversa de Observadores de uma reserva vai ser armazenada em uma tabela que contém o usuário e a reserva
b) O sistema deve permitir a exportação de dados (reservas) conforme o ano, para manter apenas dados do ano corrente (mover dados histórios para outro banco)