Arquitetura do sistema:

* Frontend: páginas HTML criadas com React e Javascript
- Será usado Rect com Next; o servidor Next permite o uso de recursos modernos:
-- hidratação de páginas (atualização com base em atualização de dados)
-- carregamento do front-end no cliente de uma só vez
- Será usado javascript simples, e não typescript
-- Isso facilita mudanças no sistema; por exemplo, caso seja necessário alterar um tipo de dado, menos mudanças serão necessárias no sistema (o dado com o novo tipo "trafega" no sistema mais livremente)

* Backend: 3 camadas de código
- modelo: classes usando ORM (object relational mapping)
- servico
- rotas
usar node.js com prisma para manter um conjunto único de tecnologias

possível arquitetura:
Node.js
+ JavaScript
+ Express
+ Prisma
+ PostgreSQL
+ JWT
+ Google OAuth