# Auditoria de Producao — Setembro/2026

## Bloqueadores encontrados

### E1 — Chave de API do Google Calendar exposta no frontend/public repository
- Arquivos: `availability.js` e `scripts/update_availability.py`
- O script gera `availability.js` contendo configuracao publica de calendario, incluindo a chave de API.
- A chave deve ser tratada como credencial exposta e rotacionada/restrita conforme o provedor.
- Correcao: nunca publicar segredo no bundle; se a chave de browser for realmente necessaria, usar uma chave dedicada com restricoes de HTTP referrer/API e quotas, ou preferir proxy/backend para operacoes sensiveis.

### E2 — Snapshot publico expõe detalhes dos eventos do calendario
- Arquivos: `availability.js`/`availability.json` e `update_availability.py`
- O script copia `event.summary` para o artefato publico.
- Resumos de calendario podem conter nomes, horarios, contatos ou outros dados que nao deveriam estar na vitrine publica.
- Correcao: publicar apenas disponibilidade agregada (bloqueado/livre), nunca o resumo bruto do evento.

### E3 — Disponibilidade publica pode ficar desatualizada
- O site usa snapshot gerado por automacao.
- Se a sincronizacao falhar, o visitante pode receber informacao antiga.
- Correcao: mostrar timestamp claramente, definir politica de stale data e nunca afirmar disponibilidade confirmada sem fonte atual.

## Pontos positivos

- Existe automacao para sincronizar calendario.
- Existe timezone explicito.
- O projeto e estatico e possui baixa superficie de ataque fora da integracao de calendario.

## Acao imediata

1. Rotacionar/restringir a chave atualmente exposta
2. Remover a chave de `availability.js` versionado
3. Sanitizar `event.summary` e publicar apenas estado de disponibilidade
4. Revisar historico do Git caso a chave tenha sido exposta em commits anteriores
5. Definir comportamento para snapshot antigo
