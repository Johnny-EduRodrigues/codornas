# Descrição do minimundo

Reservas são criadas para prever o uso de artefatos coletivos. Um usuário é quem realiza uma reserva, para um determinado propósito. Reservas podem ser agrupadas, tornando-se pertencentes a um grupo como por exemplo "Bacharelado em Ciência da Computação", indicando que são reservas ligadas ao curso de Ciência da Computação, ou "Gabinete", indicando que é uma reserva vinculada/oriunda de uma demanda (ou de responsabilidade) do gabinete. 

Artefatos podem ser categorizados, por exemplo: Sala de Aula, Laboratório de Informática, etc. Um artefato pertence a uma ou mais categorias; por exemplo, a Sala C08 pertence às categorias "Sala de Aula" e "Sala de Aula do andar superior".

O sistema funciona com múltiplas organizações, ou seja, o sistema é multi-campi (ou multi-tenant). 

Qualquer usuário do sistema pode efetuar reservas, a não ser que o artefato seja restrito; nesse caso, apenas um usuário "super" ou um usuário pertencente à lista de usuários administradores daquele artefato poderão efetuar reservas. O sistema permite visualizar todas as reservas de forma pública, sem a necessidade de realizar login, por considerar apenas artefatos não sigilosos. Qualquer usuário poderá se auto-cadastrar no sistema com um email e senha, ou via google (login via google), desde que seja aceito conforme especificação existente no grupo de usuários permitidos (GUP). No GUP existem domínios (por exemplo, ifc.edu.br) ou emails permitidos (para poder incluir, por exemplo, emails de estagiários ou outras pessoas terceiras) que filtram os usuários que podem se cadastrar.

# Descrição das entidades

Uma reserva possui: 
- um identificador único; 
- um usuário que fez a reserva; 
- o artefato que foi reservado; 
- a data para a qual o artefato está reservado;
- a hora de início e hora de fim da reserva;
- o propósito da reserva (uma breve descrição);
- se a reserva está ativa ou não;
- um código de agrupamento de reservas (batch_id), que diz se aquela reserva é individual ou é uma reserva que foi feita "em lote"; 
- uma observação, para registrar qualquer informação extra;
- a data de criação da reserva;
- o usuário que cancelou a reserva, caso ela não esteja ativa;
- uma anotação sobre o motivo do cancelamento da reserva, caso ela não esteja ativa;
- o identificador da versão anterior da reserva, em caso de alteração de reserva;
- um grupo que agrupa reservas de alguma maneira; por exemplo, uma reserva de uma sala de aula para uma disciplina pode pertencer ao grupo "Ciência da Computação"; uma reserva para uma palestra sobre "Como empreender" pode pertencer ao grupo "Interesse geral". A reserva pode, entretanto, não pertencer a nenhum grupo
- RELACIONAMENTO: uma lista de observadores, que desejam receber notificação caso a reserva seja cancelada ou alterada

RN: duas reservas ativas não podem ser realizadas com interseções; ou seja, cada reserva ativa ocupa um dia e faixa de horário único e exclusivo, para um artefato.

RN: o horário inicial de uma reserva deve ser sempre menor que o horário final da reserva

RN: uma reserva está concluída quando a data da reserva se torna "passada"; porém, não há diferença (restrições) na manipulação de reservas passadas, em execução ou futuras.

RN: como todos os dados da reserva são públicos, não é recomendado registrar dados sensíveis na reserva.

RN: reservas em lote são criadas simultaneamente e individualmente; são criadas com o mesmo horário desde a data inicial até uma *data final*, informada no momento da criação, a cada dia da semana marcado na reserva inicial;

RN: a alteração de uma reserva em lote é feita de forma individual, ou da reserva atual "para frente".

RN: se uma reserva em lote for alterada de forma individual, aquela reserva "deixa" de pertencer ao lote, tendo o seu batch_id apagado

RN: se a reserva em lote for alterada "daquela para frente", a reserva atual e as sequentes receberão um novo "batch_id", para diferenciar o novo "lote" do lote antigo

RN: a alteração de uma reserva pode ser feita pela pessoa que fez a reserva, por um administrador do artefato envolvido na reserva ou por um superadmin.

RN: quando uma reserva é alterada, o identificador da versão anterior da reserva fica registrado em um campo específico na reserva nova. Isso é importante para manter o histórico de alterações da reserva.

Um usuário possui:
- um identificador único
- um nome
- um email
- uma data de criação/inserção no sistema
- uma senha, para o caso de usuário que não faz login via google
- uma observação, para registros textuais quaisquer
- a organização à qual o usuário pertence
- o indicador (flag: verdadeiro ou falso) de super-admin
- RELACIONAMENTO: uma lista reversa de artefatos os quais o usuário pode administrar
- RELACIONAMENTO: uma lista reversa de reservas que o usuário está observando, para ser notificado em caso de cancelamento ou alteração

RN: o email é um atributo de valor único no sistema

RN: normalmente, um usuário de uma organização não pode reservar artefatos de outra organização. Entretanto, um usuário pode ser alterado para outra organização, para ter acesso aos recursos. Essa alteração é feita por um superadministrador.

RN: o superadministrador tem acesso ao sistema de forma completa (como um root), à todas as organizações.

Um artefato possui:
- um identificador único
- um nome
- pertence a uma ou mais categorias (exemplo: Sala de Aula, Sala de aula do piso superior, Laboratório de Informática)
- uma data de registro no sistema
- a organização à qual pertence o artefato
- um indicador (flag: verdadeiro ou falso) que diz se o artefato é restrito ou não
- RELACIONAMENTO: uma lista reversa dos usuários específicos que podem administrar esse artefato

RN: um artefato restrito somente pode ser reservado por um administrador daquele artefato, ou por um superadmin.

Um propósito possui:
- um identificador único
- uma descrição (exemplo: "Aula de Matemática 102 info / Alexandre", "Prática de Esportes: futsal, vôlei, tênis de mesa", "II Workshop das Mulheres na Ciência")
- uma data de registro no sistema
- a organização à qual pertence o propósito
- RN (regra de negócio): o propósito foi separado para reduzir a repetição de descrições similares, no caso de alocação de um laboratório para aula, por exemplo. Para o caso de um propósito específico, esse propósito específico será criado como um novo propósito, e será cadastrado. O campo observação da reserva sempre poderá ser usado para informações complementares.

Uma organização possui:
- um identificador único
- um nome (exemplos: "IFC Campus Blumenau", "IFC Reitoria")
- RELACIONAMENTO: uma lista reversa das categorias, que correspondem aos conjuntos de artefatos que os usuários daquela organização podem reservar

Um grupo possui:
- um identificador único
- um acrônimo, usado para localização rápida; exemplos: BCC, EMI Info
- um nome; por exemplo: Curso Superior de Bacharelado em Ciência da Computação
- se o grupo está ativo ou não; grupos inativos não "aparecem" no sistema
- uma observação, para registros textuais quaisquer
- uma data de registro no sistema
- uma cor, para auxiliar a apresentação de reservas do grupo
- a organização à qual pertence esse grupo

Uma categoria possui:
- um identificador único
- um nome; exemplos: Sala de Aula, Sala de Aula do piso superior, Laboratório de Informática
- a organização à qual pertence essa categoria
- DERIVADO: uma lista reversa de artefatos relacionados ao artefato

Um grupo de usuários permitido (GUP) possui:
- um identificador único
- uma descrição; exemplo: "Servidores do IFC"
- um filtro; por exemplos: "ifc.edu.br", "hvescovi@gmail.com"
- a organização à qual pertence esse grupo de usuários

RN: o auto-cadastramento é permitido apenas para usuários que estejam cadastrado no GUP.

RN: quem cadastra usuários no GUP é o superadmin

RN: filtro de domínio são tratados com exatidão; subdomínios não são considerados. Por exemplo, se o filtro é "ifc.edu.br", aceita-se "jorge@ifc.edu.br", mas não "joao@blumenau.ifc.edu.br" ou "maria@sisae.ifc.edu.br"

RN: ao se cadastrar, o novo usuário escolhe a organização à qual pertence, caso mais de uma organização aceite o usuário. Caso erre a escolha, será necessário um superadmin para fazer a alteração de vínculo de organização.

RN: todo usuário pertence a uma organização.