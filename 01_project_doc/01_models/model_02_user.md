1) id
   
2) name
- nome completo do usuário
- exemplos de valores:
Hylson Vescovi Netto
Ricardo de la Rocha Ladeira

3) email
- email é usado para comunicação com o usuário, e usado para *identificar* um usuário no sistema de forma textual
- pode também ser usado para acessar o sistema, no caso de login via email

4) timestamp_email_verified
- timestamp sobre quando o email foi confirmado pelo usuário
- o usuário só pode iniciar a marcação de reservas após confirmar o email
- o valor padrão desse campo deve ser NULL
- se for realizado login via google, esse campo poderá ser preenchido com o momento da criação do usuário
- para login via email comum, esse campo só será preenchido na confirmação via email

5) created_at

6) password
- armazena a senha cifrada; é obrigatória no caso de ter sido feito login via email/local
- pode ter valor nulo caso tenha sido feito login via provedor externo (ex: login via google)

7) obs

8) tenants
- RELACIONAMENTO: uma lista de organizações (tenants) às quais o usuário pertence
- um usuário deve pertencer a pelo menos uma organização

9) super_admin
- informa se o usuário é um "super admin"
- "super admin" pode executar todas as ações no sistema, mas atuando apenas em entidades da(s) organização(ções) à(s)qual(is) pertence
- tipo Boolean

10) active

11) authentication_identities
- RELACIONAMENTO: lista de identidades de autenticacao que o usuário possui.
- uma identidade de autenticacao é um meio de acesso via provedor externo
- List[AuthenticationIdentity]

12) artifacts_admin
- lista reversa de artefatos os quais esse usuário é "admin", ou seja, pode criar, editar ou cancelar reservas
- um artefato pode possuir muitos admin, e um usuário pode ser admin de muitos artefatos
- List[Artifact]
  
13) reservations_observer
- lista reversa de reservas que o usuário está observando
- se um usuário observa uma reserva, em caso de alteração ou cancelamento, o usuário será notificado (por exemplo, via email)
- um usuário pode observar várias reservas, e uma reserva pode ser "observada" por vários usuários
- List[Reservation]