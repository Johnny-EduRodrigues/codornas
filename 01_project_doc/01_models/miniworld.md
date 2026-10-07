# Descrição do minimundo

Reservas são criadas para prever o uso de artefatos coletivos. Um usuário é quem realiza uma reserva, para um determinado propósito. Reservas podem ser agrupadas, tornando-se pertencentes a um grupo como por exemplo "Bacharelado em Ciência da Computação", indicando que são reservas ligadas ao curso de Ciência da Computação, ou "Gabinete", indicando que é uma reserva vinculada/oriunda de uma demanda (ou de responsabilidade) do gabinete. 

Artefatos podem ser categorizados, por exemplo: Sala de Aula, Laboratório de Informática, etc. Um artefato pertence a uma ou mais categorias; por exemplo, a Sala C08 pertence às categorias "Sala de Aula" e "Sala de Aula do andar superior".

O sistema funciona com múltiplas organizações, ou seja, o sistema é multi-campi (ou multi-tenant). 

Qualquer usuário do sistema pode efetuar reservas, a não ser que o artefato seja restrito; nesse caso, apenas um usuário "super" ou um usuário pertencente à lista de usuários administradores daquele artefato poderão efetuar reservas. O sistema permite visualizar todas as reservas de forma pública, sem reservas, por considerar apenas artefatos não sigilosos. Qualquer usuário poderá se cadastrar no sistema com um email e senha, ou via google (login via google). É possível especificar uma lista de usuários permitidos de se cadastrar no sistema, restringindo domínios (por exemplo, ifc.edu.br) ou listando diretamente os emails permitidos (para poder incluir, por exemplo, emails de estagiários ou outras pessoas terceiras).

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
- uma data final, que indica que aquela é uma reserva "em lote";
- uma observação, para registrar qualquer informação extra;
- a data de criação da reserva;
- o usuário que cancelou a reserva, caso ela não esteja ativa;
- uma anotação sobre o motivo do cancelamento da reserva, caso ela não esteja ativa;
- um grupo ao qual a reserva pertence (por exemplo, a reserva é relativa a uma aula do curso de "Ciência da Computação" <== esse seria o grupo: "Ciência da Computação")
- DERIVADO: uma lista de observadores, que desejam receber notificação caso a reserva seja cancelada ou alterada

Um usuário possui:
- um identificador único
- um nome
- um email
- uma data de criação/inserção no sistema
- uma senha, para o caso de usuário que não faz login via google
- uma observação, para registros textuais quaisquer
- a organização à qual o usuário pertence
- o indicador (flag: verdadeiro ou falso) de super-admin
- DERIVADO: uma lista reversa de artefatos os quais o usuário pode administrar
- DERIVADO: uma lista reversa de reservas que o usuário está observando, para ser notificado em caso de cancelamento ou alteração

Um artefato possui:
- um identificador único
- um nome
- pertence a uma ou mais categorias (exemplo: Sala de Aula, Sala de aula do piso superior, Laboratório de Informática)
- uma data de registro no sistema
- a organização à qual pertence o artefato
- o indicador (flag: verdadeiro ou falso) que diz se o artefato é restrito ou não
- DERIVADO: uma lista reversa com os usuários que podem administrar esse artefato

Um propósito possui:
- um identificador único
- uma descrição (exemplo: "Aula de Matemática 102 info / Alexandre", "Prática de Esportes: futsal, vôlei, tênis de mesa", "II Workshop das Mulheres na Ciência")
- uma data de registro no sistema
- a organização à qual pertence o propósito

Uma organização possui:
- um identificador único
- um nome (exemplos: "IFC Campus Blumenau", "IFC Reitoria")
- DERIVADO: uma lista reversa das categorias, que correspondem aos conjuntos de artefatos que os usuários daquela organização podem reservar

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
- a organização à qual pertence esse grupo
- DERIVADO: uma lista reversa de artefatos relacionados ao artefato

Um grupo de usuários permitido possui:
- um identificador único
- uma descrição; exemplo: "Servidores do IFC"
- um filtro; por exemplos: "ifc.edu.br", "hvescovi@gmail.com"