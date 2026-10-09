1) id
- identificador único da reserva
- pode ser autoincremento, UID, ULID, UUID v7, etc

2) user_id
- chave estrangeira do usuário que fez a reserva
- referente ao id da classe User
- tipo inteiro

3) user
- objeto da classe User, montado a partir de user_id

4) artifact_id
- chave estrangeira do artefato que foi reservado
- referente ao atributo id da classe Artifact
- pode ser uma sala, um veículo, um laboratório de informática
- tipo inteiro

5) artifact
- objeto da classe Artifact, montado a partir de artifact_id

6) date
- Data para a qual foi feita a reserva
- tipo Date
- Se uma reserva for feita para 2 ou mais dias, deverão ser feitas 2 ou mais reservas
- cada reserva se refere a apenas uma data

7) start_time
- Hora/min/seg de início da reserva (a partir da qual a reserva é válida)
- tipo Time

8) end_time
- hora/min/seg de término da reserva
- tipo Time

9) purpose_id
- chave estrangeira do propósito da reserva
- referente ao atributo id da classe Purpose
- finalidade da reserva: para quê o artefato foi reservado?

10) purpose
- objeto da classe Purpose, montado a partir de purpose_id

11) active
- a reserva está ativa ou não?
- tipo boolean
- reservas ativas são válidas, reservas não ativas foram canceladas
- quando uma reserva é alterada, a antiga é cancelada e uma nova é criada

12) batch_id
- código que identifica reserva como "em lote"
- Quando uma reserva é feita "em massa", por exemplo, de uma data até outra, são criadas várias reservas que possuem o mesmo "batch_id"
- se uma reserva for alterada ou cancelada e possuir valor em batch_id, todas as outras que possuem esse valor de batch_id poderão ser alteradas ou canceladas "em lote" (de uma só vez), isso será perguntado ao usuário (se ele deseja fazer a operação "em lote" ou individual)
- se apenas essa reserva for alterada, o batch_id dela será "zerado" (valor ficará NULL), pois ela não pertencerá mais ao lote
- se a reserva não foi feita "em massa"/"em lote", esse campo não será preenchido (valerá NULL)
- tipo UUID ou algo assim

13)  obs
- una observação qualquer sobre a reserva
- tipo Text

14)  created_at
- data de criação da reserva
- tipo: data/hora (timestamp)
- obtida automaticamente do sistema

15)  canceled_by_user_id
- chave estrangeira do usuário que cancelou a reserva
- referente ao id da classe User
- quando houver valor neste campo (diferente de NULL), essa reserva deve estar com o campo active igual a false, pois foi cancelada. 

16)  canceled_by_user
- objeto da classe User, montado a partir de canceler_user_id
- usuário que cancelou a reserva

17)  cancellation_reason
- observação/justificativa sobre o porquê da reserva ter sido cancelado
- tipo Text
- campo de prenchimento obrigatório

18)  previous_reservation_id
- quando uma reserva for alterada, esse campo armazena o ID da reserva que foi desativada e que possuía os valores anteriores à reserva atual ativa
- esse campo pode ter valor também para reservas canceladas, pois pode ter havido versões anteriores da reserva
- o valor é praticamente uma chave estrangeira para a própria tabela
- é um valor único no sistema (UNIQUE), pois não é desejável haver ramificações
- pode possuir um valor nulo, o que significa que a reserva não possui histórico de alterações

19) previous_reservation
- objeto da reserva anterior, montado sobre previous_reservation_id

20)  groupid
- grupo ao qual a reserva pertence; por exemplo, uma reserva de uma disciplina pode pertencer ao grupo "Ciência da Computação"

21)  group
  objeto Grupo montado a partir de group_id

22) takers
- lista de usuários que vão fazer uso do artefato reservado (vão efetivamente "pegar" o artefato para usar).
Por padrão, na criação da reserva é o usuário que está criando a reserva, mas podem ser especificados outros usuários. Quem está fazendo a reserva pode não incluir a si mesmo e incluir outro usuário, ou outros usuários.

23) observers
- lista reversa de usuários que estão interessados caso essa reserva fique inativa (seja ALTERADA ou CANCELADA)
- a alteração de uma reserva implica no cancelamento da reserva e na criação de uma nova reserva alterada