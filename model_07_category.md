Descrição da classe Category

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

3) color
- cor associada à categoria
- é um código de cor  
- armazenado em hexadecimal
- essa cor será representada em uma página HTML

4) artifacts
- lista reversa de Artifact
- contém os artefatos que estão associados a esta categoria
- um artefato está vinculado a uma ou mais categorias
- List[Artifact]

5) tenant_id