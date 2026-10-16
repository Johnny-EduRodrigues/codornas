# Descrição do minimundo

Reservas são criadas para prever o uso de artefatos coletivos. Um usuário é quem realiza uma reserva, para um determinado propósito. Reservas podem ser agrupadas, tornando-se pertencentes a um grupo como por exemplo "Bacharelado em Ciência da Computação", indicando que são reservas ligadas ao curso de Ciência da Computação, ou "Gabinete", indicando que é uma reserva vinculada/oriunda de uma demanda (ou de responsabilidade) do gabinete. 

Artefatos podem ser categorizados, por exemplo: Sala de Aula, Laboratório de Informática, etc. Um artefato pertence a uma ou mais categorias; por exemplo, a Sala C08 pertence às categorias "Sala de Aula" e "Sala de Aula do andar superior".

O sistema funciona com múltiplas organizações, ou seja, o sistema é multi-campi (ou multi-tenant). Um usuário pertence a no mínimo uma organização (escolhida quando ele se cadastra), e depois pode ser vinculado a outras organizações por um superadmin.

Qualquer usuário do sistema pode efetuar reservas, a não ser que o artefato seja restrito; nesse caso, apenas um usuário superadmin ou um usuário pertencente à lista de usuários administradores daquele artefato poderão efetuar reservas. O sistema permite visualizar os dados de todas as reservas de forma pública, sem a necessidade de realizar login, por considerar apenas artefatos não sigilosos. Qualquer usuário poderá se auto-cadastrar no sistema com um email e senha, ou via google (login via google), desde que seja aceito conforme especificação existente no conjunto de usuários permitidos (CUP). No CUP existem domínios (por exemplo, ifc.edu.br) ou emails permitidos (para poder incluir, por exemplo, emails de estagiários ou outras pessoas terceiras) que filtram os usuários que podem se cadastrar.

# Descrição das entidades

## Uma reserva possui: 

- um identificador único; 
- um usuário que fez a reserva ("autor" da reserva); 
- o artefato que foi reservado; 
- a data para a qual o artefato está reservado;
- a hora de início e hora de fim da reserva;
- o propósito da reserva (uma breve descrição); na verdade, será uma chave estrangeira para uma tabela de propósitos
- se a reserva está ativa ou não;
- um código de agrupamento de reservas (batch_id), que diz se aquela reserva é individual ou é uma reserva que foi feita "em lote"; 
- uma observação, para registrar qualquer informação extra;
- a data de criação da reserva;
- o usuário que cancelou a reserva, caso ela não esteja ativa;
- uma anotação sobre o motivo do cancelamento da reserva, caso ela não esteja ativa; esse campo é obrigatório (não pode ser vazio) para quando uma reserva for cancelada ou alterada
- o identificador da versão anterior da reserva, em caso de alteração de reserva; é um valor único no cadastro
- um grupo que agrupa reservas de alguma maneira; por exemplo, uma reserva de uma sala de aula para uma disciplina pode pertencer ao grupo "Ciência da Computação"; uma reserva para uma palestra sobre "Como empreender" pode pertencer ao grupo "Interesse geral". A reserva pode, entretanto, não pertencer a nenhum grupo
- RELACIONAMENTO: uma lista de usuários que efetivamente vão pegar o artefato reservado para usá-lo. Por padrão, é o próprio usuário que está fazendo a reserva; mas pode ser informado outro usuário no momento da criação, ou mais de um usuário; mas precisa existir pelo menos um usuário destinado a fazer o uso do artefato reservado. Não há restrição de que esses usuários pertençam também a outras organizações, mas para que sejam incluídos como participante do uso do artefato, é preciso que pertençam à organização do artefato
- RELACIONAMENTO: uma lista de observadores, que desejam receber notificação caso a reserva seja cancelada ou alterada

RN: duas reservas ativas não podem ser realizadas com interseções; ou seja, cada reserva ativa ocupa um dia e faixa de horário único e exclusivo, para um artefato (inserir esta regra no banco de dados)

RN: os intervalos de horários devem ser semiabertos incluindo o início e excluindo o fim; assim, uma reserva na segunda feira das 10hs às 11hs pode ser seguida por outra na mesma segunda feira das 11hs às 12hs, sem conflito.

RN: o horário inicial de uma reserva deve ser sempre menor que o horário final da reserva (inserir esta regra no banco de dados) => CHECK (start_time < end_time)

RN: uma reserva não "atravessa" a meia-noite

RN: uma reserva está concluída quando a data da reserva se torna "passada", ou concluída; porém, não há diferença (restrições) na manipulação de reservas passadas, em execução ou futuras.

RN: como todos os dados da reserva são públicos, não é recomendado registrar dados sensíveis na reserva.

RN: ao exibir uma reserva, são exibidos apenas os dados da reserva, e não todos os dados das entidades relacionadas (ex: não é exibido o hash da senha o usuário que fez a reserva, ou o ID da categoria do artefato reservado)

RN: reservas em lote são criadas simultaneamente e individualmente; são criadas com o mesmo horário desde a data inicial até uma *data final*, informada no momento da criação, a cada dia da semana marcado na reserva inicial;

RN: após a criação das 'reservas em lote, será possível identificar a data final por meio de busca pela reserva (ativa ou não) que possui aquele batch_id e que tem a data de reserva mais avançada

RN: quando uma reserva é alterada, na verdade ela a reserva é cancelada e é criada uma nova reserva com os novos dados alterados

RN: os campos que informam o usuário que cancelou a reserva e o motivo do cancelamento só podem possuir valores (strings não vazias) se o campo "ativo" estiver falso (pode ser inserido um CHECK no banco de dados); se a reserva estiver ativa, esses dois campos devem ser nulos

RN: a alteração de uma reserva é feita de forma transacional: a reserva antiga não pode ficar desativada se a criação da nova reserva falhar.

RN: a alteração de uma reserva em lote é feita de forma individual, ou da reserva atual "para frente".

RN: se uma reserva em lote for alterada de forma individual, aquela reserva "deixa" de pertencer ao lote, tendo o seu batch_id apagado

RN: se a reserva em lote for alterada "daquela para frente", a reserva atual e as seguintes do mesmo lote (ativas) receberão um novo "batch_id", para diferenciar o novo "lote" do lote antigo

RN: a criação e alteração de uma reserva em lote deve ser feita de forma transacional: ou todas são criadas, ou caso haja conflito de horário em alguma das reservas, nenhuma será criada

RN: em uma alteração de reservas em lote, todos os campos da reserva podem ser alterados

RN: a alteração ou cancelamento de uma reserva pode ser feita pela pessoa que fez a reserva, por um dos usuários que farão uso da reserva, por um administrador do artefato envolvido na reserva ou por um superadmin.

RN: um usuário, mesmo sendo superadmin, também precisa pertencer à organização do artefato que se encontra na reserva a ser alterada; ou seja, o usuário é superadmin nas organizações em que está vinculado

RN: o usuário que alterou a reserva passa a ser o novo "autor" da reserva.

RN: quando uma reserva é alterada, o identificador da versão anterior da reserva fica registrado em um campo específico na reserva nova. Isso é importante para manter o histórico de alterações da reserva.

RN: ao alterar uma reserva, os observadores da reserva antiga são "copiados" também para a nova reserva, assim como os usuários que farão usufruto da nova reserva. O usuário que está fazendo a nova reserva pode entrar ou não na lista de usuários que vai usufruir do artefato reservado (isso pode ser escolhido na alteração da reserva, caso o usuário que altera seja diferente do usuário da reserva anterior)

RN: dentro de uma reserva: o propósito, o grupo, os observadores e os usuários que vão usar o artefato da reserva devem estar vinculados à organização do artefato reservado.

# Um usuário possui:
- um identificador único
- um nome
- um email
- uma data de criação/inserção no sistema
- uma senha, para o caso de usuário que não faz login via google
- uma observação, para registros textuais quaisquer
- uma LISTA de organizações às quais o usuário pertence
- o indicador (flag: verdadeiro ou falso) de super-admin
- um indicador (flag) que diz se o usuário está ativo ou não
- RELACIONAMENTO: uma lista reversa de artefatos os quais o usuário pode administrar
- RELACIONAMENTO: uma lista reversa de reservas que o usuário está observando, para ser notificado em caso de cancelamento ou alteração

RN: o email é um atributo de valor único no sistema

RN: usuários inativos não podem criar reservas

RN: um usuário só pode reservar artefatos de uma das organizações às quais pertence.

RN: o superadministrador tem acesso ao sistema de forma completa (como um root), a todas as organizações.

RN: um usuário só pode ser removido de uma organização se não houver entidades da organização a ser removida associadas a ele

# Um artefato possui:
- um identificador único
- um nome
- pertence a uma ou mais categorias (exemplo: Sala de Aula, Sala de aula do piso superior, Laboratório de Informática)
- uma data de registro no sistema
- a organização à qual pertence o artefato
- um indicador (flag: verdadeiro ou falso) que diz se o artefato é restrito ou não
- um indicador (flag) que diz se o artefato está ativo ou não (pode estar temporariamente inapto a receber novas reservas)
- RELACIONAMENTO: uma lista reversa dos usuários específicos que podem administrar esse artefato

RN: um artefato restrito somente pode ser reservado por um administrador daquele artefato, ou por um superadmin. 

RN: as informações de uma reserva que envolve um artefato restrito são visíveis da mesma forma que reservas de artefatos não restritos.

RN: a desativação de um artefato não remove automaticamente as reservas daquele artefato, apenas impede a criação de novas reservas com aquele artefato desativado

RN: um artefato pode ser reservado apenas por usuários pertencentes à mesma organização do artefato

# Um propósito possui:
- um identificador único
- uma descrição (exemplo: "Aula de Matemática 102 info / Alexandre", "Prática de Esportes: futsal, vôlei, tênis de mesa", "II Workshop das Mulheres na Ciência")
- uma data de registro no sistema
- a organização à qual pertence o propósito
- RN (regra de negócio): o propósito foi separado para reduzir a repetição de descrições similares, no caso de alocação de um laboratório para aula, por exemplo. Para o caso de um propósito específico, esse propósito específico será criado como um novo propósito, e será cadastrado. O campo observação da reserva sempre poderá ser usado para informações complementares.

# Uma organização (tenant) possui:
- um identificador único
- um nome (exemplos: "IFC Campus Blumenau", "IFC Reitoria")
- RELACIONAMENTO: uma lista reversa das categorias que os usuários daquela organização podem visualizar, a fim de filtrar artefatos quando forem selecionar artefatos; 

RN: todas as entidades que possuem relação com a tabela de organizações terão relacionamento com garantia de integridade referencial.

# Um grupo possui:
- um identificador único
- um acrônimo, usado para localização rápida ou exibição resumida; exemplos: BCC, EMI Info
- um nome; por exemplo: Curso Superior de Bacharelado em Ciência da Computação
- se o grupo está ativo ou não; grupos inativos não "aparecem" na criação de reservas
- uma observação, para registros textuais quaisquer
- uma data de registro no sistema
- uma cor, para auxiliar a apresentação de reservas do grupo
- a organização à qual pertence esse grupo

RN: ao desativar um grupo, as reservas associadas permanecem inalteradas

# Uma categoria possui:
- um identificador único
- um nome; exemplos: Sala de Aula, Sala de Aula do piso superior, Laboratório de Informática
- a organização à qual pertence essa categoria; esse vínculo é apenas para filtrar dados entre organizações, na listagem de categorias, e não para controlar acesso de artefatos
- RELACIONAMENTO: uma lista reversa de artefatos relacionados ao artefato

RN: uma categoria deve pertencer à mesma organização dos artefatos os quais reúne (artefatos que pertencem àquela categoria).

# Um conjunto de usuários permitidos (CUP) possui:
- um identificador único
- uma descrição; exemplo: "Servidores do IFC"
- um filtro; exemplos: "ifc.edu.br", "hvescovi@gmail.com"
- um tipo, para explicitar se o filtro é domínio ou email específico
- a organização à qual pertence esse conjunto de usuários

RN: o auto-cadastramento é permitido apenas para usuários que estejam cadastrados no CUP.

RN: quem cadastra usuários no CUP é o superadmin

RN: filtro de domínio são tratados com exatidão; subdomínios não são considerados. Por exemplo, se o filtro é "ifc.edu.br", aceita-se "jorge@ifc.edu.br", mas não "joao@blumenau.ifc.edu.br" ou "maria@sisae.ifc.edu.br"

RN: o usuário deverá confirmar seu email via verificação enviada por email, antes de poder acessar o sistema

RN: ao se cadastrar, o novo usuário escolhe a organização à qual pertence, caso mais de uma organização aceite o usuário. Para alterar seu vínculo ou adicionar vínculo com outras organizações, é preciso a ação de um superadmin.

RN: todo usuário pertence a pelo menos uma organização.

RN: um filtro não pode ser cadastrado duas ou mais vezes na mesma organização

Exemplos de dados:
ifc.edu.br => Servidores do IFC (domínio)
hvescovi@gmail.com => email particular do professor Hylson (email específico)
helder.martins@gmail.com => email particular do Helder, discente do projeto fabtec 2026 (email específico)

