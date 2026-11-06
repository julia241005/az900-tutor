# 11 · Segurança e ética

> **Objetivo:** proteger o tutor quando ele sair do computador local e usar IA de forma responsável.
> **Arquivos no código:** [`seguranca.py`](../seguranca.py), [`api.py`](../api.py), [`.env.example`](../.env.example)

## Segurança

| Risco | Proteção |
|---|---|
| Alguém usar o tutor sem permissão | **Senha opcional** (`TUTOR_SENHA` no `.env`): o navegador pede usuário e senha (HTTP Basic). A comparação é feita em tempo constante (`secrets.compare_digest`) |
| Abuso / gasto descontrolado | **Limite de mensagens por minuto por IP** (`LIMITE_MENSAGENS_POR_MINUTO`, padrão 20). Acima disso: erro 429 "espere um minuto" |
| Vazamento de chaves | Chaves e senhas só no `.env`, que está no `.gitignore`. O repositório traz apenas o `.env.example` sem valores |
| Exposição na rede | Por padrão o Uvicorn escuta só em `127.0.0.1`: apenas o próprio computador acessa |
| Gabarito visível no navegador | A API do simulado nunca envia a resposta correta antes da correção (há teste para isso) |
| Entrada gigante | Mensagens limitadas a 500 caracteres (validação com Pydantic) |
| Prompt injection ("ignore as regras...") | O prompt de sistema restringe ao AZ-900 e às fontes. Modelos pequenos podem ceder: por isso o tutor não tem ferramentas perigosas (só leitura de documentação e banco local) |

> **HTTP Basic** só é seguro com **HTTPS**. Em uma publicação real, o tutor deve ficar atrás de HTTPS (os planos gratuitos de hospedagem já oferecem).

`/saude` continua aberto mesmo com senha, para ferramentas de monitoramento (como o Zabbix) verificarem se o serviço está no ar.

## Privacidade

- O log guarda só os **primeiros 200 caracteres** de cada pergunta e fica em `data/`, fora do Git.
- O histórico do chat fica no SQLite local. O botão **Nova conversa** apaga o histórico (o progresso do simulado continua).
- Com o modelo local, **nenhuma pergunta sai do computador**: não há envio para APIs de terceiros.

## Ética e uso responsável

- **Respostas com fonte:** o tutor responde só com base em trechos oficiais e cita a fonte. Sem trecho relevante, diz que não encontrou em vez de inventar (guardrail medido na avaliação, doc 09).
- **Revisão humana:** perguntas de simulado geradas por IA só entram após aprovação humana. Na prática, 0 de 11 geradas pelo modelo pequeno foram aprovadas, então o simulado usa um banco curado com fonte oficial.
- **Direitos do conteúdo:** o texto da Microsoft Learn não é publicado no repositório. O tutor sempre cita e linka a página original.
- **Transparência:** a interface mostra modelo, tokens e tempo de cada resposta. O projeto não tem vínculo com a Microsoft.
- **Limitações declaradas:** um modelo de 3B parâmetros erra mais que modelos grandes. O tutor é material de apoio e não substitui a documentação oficial nem os simulados oficiais.
