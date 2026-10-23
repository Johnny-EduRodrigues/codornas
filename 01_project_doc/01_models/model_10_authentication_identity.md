1) id

2) user_id
- chave estrangeira

3) user
- objeto User

4) login_provider_id
- chave estrangeira

5) login_provider
- objeto LoginProvider

6) identificator_login
- exemplo: email da google; CPF (para login via .gov)

7) identificator_external
- exemplo: o valor do claim sub no ID token validado pelo Google; para uma conta GOV, seria um claim sub do ID Token validado pelo gov.br. 
- pode ser usado para reencontrar a mesma identidade nas próximas autenticações (em vez de localizar email)