# Relatorio de mutacao

## Ferramenta

O projeto configura `mutmut==3.6.0` em `pyproject.toml` para mutar o pacote `app/`
e selecionar os testes em `tests/`. A execucao local em Windows nativo deve ser feita
via WSL/Linux porque o mutmut 3 depende de suporte a `fork`.

Comando planejado:

```bash
python -m mutmut run
python -m mutmut browse
```

## Cenario escolhido

Mutacao: remover ou inverter o tratamento de `ExternalProviderError` no endpoint
`POST /notifications`, fazendo a API persistir uma notificacao mesmo quando o provedor
externo falha.

Bug real evitado: registrar uma notificacao como aceita sem que o servico externo tenha
recebido o envio. Isso criaria inconsistencia operacional: a API responderia sucesso ou
deixaria dado persistido, mas o email/SMS nunca teria sido encaminhado.

Teste que mata a mutacao: `test_falha_do_provedor_retorna_503_e_nao_persiste`.
Esse teste substitui o sender por um mock que levanta `ExternalProviderError`, espera
HTTP `503`, verifica que `/notifications` continua vazio e confirma o incremento de
`notifications_failed_total`. Se o codigo mutado removesse o rollback, ignorasse a
excecao ou persistisse antes/depois da falha, o teste falharia.

## Criterio de aceitacao

Nesta entrega, mutacao e informativa/manual. O quality gate obrigatorio continua sendo:
lint sem erros, todos os testes passando e cobertura minima de 70%.
