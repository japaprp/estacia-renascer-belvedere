# Estacia Renascer Belvedere

Site institucional para apresentacao do espaco, experiencias e contato comercial.

## Objetivo

Dar presenca digital ao negocio, melhorar a comunicacao da proposta e facilitar contato, reserva e locacao.

## Funcionalidades

- Pagina institucional com proposta de valor
- Galeria de imagens
- Blocos de servicos e experiencias
- CTA para contato e reserva
- Fallback local com ultima disponibilidade sincronizada
- Estrutura preparada para sincronizacao de calendario

## Tecnologias

- HTML
- CSS
- JavaScript

---

# Roadmap de qualidade comercial

Este projeto e propositalmente mais simples que os produtos SaaS, mas tambem deve ser uma **entrega real e confiavel**, sem vender como pronto o que ainda nao existe.

## 1. Conversao e contato

- [ ] CTA principal claramente orientado para locacao
- [ ] WhatsApp com mensagem contextual
- [ ] Formulario de contato/reserva validado
- [ ] Tratamento de erros de envio
- [ ] Confirmacao de envio
- [ ] Anti-spam
- [ ] Medicao basica de conversao

## 2. Calendario e disponibilidade

- [ ] Definir fonte oficial de disponibilidade
- [ ] Integracao real com calendario quando aplicavel
- [ ] Fallback confiavel quando a sincronizacao falhar
- [ ] Identificar ultima atualizacao da disponibilidade
- [ ] Evitar prometer disponibilidade desatualizada
- [ ] Testar conflitos de reserva

## 3. Seguranca

- [ ] Validacao de todos os dados enviados
- [ ] Protecao anti-spam/abuso
- [ ] Segredos fora do repositorio
- [ ] Revisar integracoes externas
- [ ] Evitar exposicao de dados pessoais
- [ ] HTTPS no deploy

## 4. Performance

- [ ] Otimizar imagens
- [ ] Lazy loading quando aplicavel
- [ ] Minificar assets no build de producao
- [ ] Testar Core Web Vitals
- [ ] Garantir bom funcionamento em celular

## 5. SEO e confiabilidade

- [ ] Title e meta description finais
- [ ] Open Graph
- [ ] Sitemap
- [ ] Robots
- [ ] Dados estruturados quando fizer sentido
- [ ] Favicon e manifest
- [ ] Links e imagens sem erros
- [ ] Pagina 404 quando aplicavel

## 6. Acessibilidade e UX

- [ ] Contraste adequado
- [ ] Navegacao por teclado
- [ ] Alt text das imagens
- [ ] Hierarquia semantica
- [ ] Botoes e links claramente identificaveis
- [ ] Estados de erro/sucesso
- [ ] Teste em celular real

## 7. Operacao

- [ ] Dominio e HTTPS
- [ ] Monitoramento de disponibilidade
- [ ] Backup do conteudo/configuracao
- [ ] Procedimento para atualizar fotos e informacoes
- [ ] Documentar contato e fluxo de reserva

## Criterio de pronto

O site deve funcionar como ferramenta comercial real: carregar rapidamente, apresentar informacoes corretas, encaminhar reservas/contatos sem ambiguidade e nao afirmar disponibilidade que nao possa ser confirmada.

## Como executar localmente

Rode um servidor local na pasta do projeto:

```powershell
python -m http.server 8080
```

Depois acesse:

```text
http://localhost:8080
```

Abrir `index.html` diretamente via `file://` nao garante sincronizacao ao vivo do calendario.

## Regra de continuidade

Antes de adicionar efeitos ou novas telas, priorizar **confiabilidade, conversao, disponibilidade, performance e seguranca**.
