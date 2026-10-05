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