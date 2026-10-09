1) id
   
2) name
- nome do artefato
- exemplos de valores:
Sala C16
Doblô Placa ABC 123 Branco
Auditório
Laboratório A04

3) categories
- lista reversa de categorias às quais pertencem o artefato
- List[Category]

4) created_at

5) tenant_id

6) tenant

7) restrict
- artefatos restritos não podem ser reservados por usuários comuns, apenas admins
- tipo: Boolean
- valor padrão: Falso

8) active

8) admins
- lista reversa de usuários que podem administrar reservas deste artefato
- List[User]



