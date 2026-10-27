1) id
- tipo Inteiro
  
2) name
- tipo String(250)
- exemplos de valores:
Veículo
Sala de aula
Laboratório de Informática
Utensílio elétrico
Mobília

3) tenant_id

4) tenant

5) created_at

6) artifacts
- lista de Artifact
- contém os artefatos que estão associados a esta categoria
- um artefato está vinculado a uma ou mais categorias
- List[Artifact]