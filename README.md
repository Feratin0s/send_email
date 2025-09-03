# send\_email



COMO USAR (passo a passo rápido)

=================================

1\) Abra o arquivo config.json e edite:

&nbsp;  - username: seu e-mail (ex.: Gmail)

&nbsp;  - password: sua SENHA DE APP (não é a senha normal). No Gmail, gere em

&nbsp;    Segurança > Verificação em duas etapas > Senhas de app.

&nbsp;  - from\_name e subject: opcional



2\) Abra recipients.json e cadastre os destinos:

&nbsp;  - Organize por grupos (ex.: "clientes", "interno", "log").

&nbsp;  - Cada item pode ser uma string "email@dominio.com" ou um objeto

&nbsp;    {"email": "...", "name": "Nome"} para personalizar {{name}}.



3\) Edite email\_template.html se quiser mudar o layout/texto do e-mail.

&nbsp;  - Você pode usar {{name}} no HTML para personalizar por destinatário.



4\) Para enviar:

&nbsp;  - Windows: dê 2 cliques em send\_html\_email.py (com Python instalado).

&nbsp;  - Ou abra um terminal e rode:  python send\_html\_email.py

&nbsp;  - Escolha o grupo pelo menu (ou "todos" para todos).



Observações:

\- Este script usa TLS (porta 587). Se usar outro provedor, ajuste smtp\_server/port.

\- Se der erro de autenticação, confira se sua conta exige senha de app

&nbsp; e se 2FA está habilitado.



