class Reservation

id: identificador único da reserva
pode ser autoincremento, UID, etc

user: Usuário que fez a reserva. 
É bom que seja uma chave estrageira para a classe User

artifact: Artefato que será reservado. 
Pode ser uma sala, um veículo, um laboratório de informática. 
Exemplos de valores:
Sala C16
Doblô Placa ABC 123 Branco
Auditório
Laboratório A04

date: Data para a qual foi feita a reserva.
Se uma reserva for feita para 2 ou mais dias, deverão ser feitas 2 ou mais reservas; cada reserva se refere a apenas uma data

start_time: hora/min/seg de início da reserva (a partir da qual a reserva é válida)

end_time: hora/min/seg de término da reserva

purpose: finalidade da reserva.
Para quê o artefato foi reservado? Neste momento pode ser uma STRING para facilitar o desenvolvimento, no futuro será chave estrangeira. 
Exemplos de valores:
Aula de matemática 102 info (sala)
Aula de algoritmos BCC (labinfo)
Viagem Blumenau x Floripa evento SBRC (veículo)
Formatura Info 201 2026 (auditório)

category: categoria da reserva; é um campo que "agrupa" reservas. Neste momento pode ser uma STRING para facilitar o desenvolvimento, no futuro será chave estrangeira. Esse campo será usado para filtros durante a criação de uma reserva, ou para visualizar apenas reservas de um determinado “tipo”. 
Exemplos de valores:
Veículo do campus
Sala de aula
Laboratório de Informática

color_category: cor ou padrão de preenchimento ou imagem de fundo a ser utilizado na representação visual das reservas que pertençam à categoria. Pode ser string neste momento.
10
active
reserva ativa ou não? reservas ativas são válidas, reservas não ativas foram canceladas/excluídas. Quando uma reserva é alterada, a antiga é cancelada e uma nova é criada. Isso não precisa ser implementado agora (deixar para uma sprint 3)
11
batch_id
ID de operação em lote. Quando uma reserva é feita “em massa”, por exemplo, de uma data até outra, são criadas várias reservas que possuem o mesmo “batch_id”. Isso serve para, quando alterarmos uma reserva, o sistema perguntar se deseja alterar só aquela reserva ou todas as reservas com o mesmo “batch_id”. Se a reserva não foi feita “em massa”, esse campo não será preenchido (valerá NULL). Possivelmente será um valor do tipo UID ou HASH.
12
obs
qualquer tipo de observação adicional sobre a reserva (campo STRING)
13
created_at
data e hora (timestamp) de criação da reserva, obtida automaticamente do sistema.
14
canceler_user
Usuário que cancelou a reserva. Quando houver valor neste campo (diferente de NULL), essa reserva deve estar com o campo active igual a false. Nesse momento pode ser STRING, futuramente será chave estrangeira.
15
observers
lista de usuários que têm interesse em serem notificados, caso essa reserva fique inativa (alterada ou excluída). Nesse momento, pode ser uma STRING com uma lista de IDs separados por vírgula, futuramente será uma lista reversa.


