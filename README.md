# Slide Generator

Ferramenta web para transformar textos pedagógicos estruturados em slides HTML
e exportá-los como PDF. Construída com FastAPI, Pydantic v2, Jinja2 e WeasyPrint,
seguindo arquitetura em camadas (router → controller → service).

## Funcionalidades

- Parser que reconhece automaticamente:
  - **Aula N: Título** → slide de capa com numeração da aula
  - **Cabeçalhos curtos** → títulos de seção dos slides
  - **Termo: descrição** → bullets agrupados em slides de lista
  - **Parágrafos** → slides de conteúdo (com quebra automática quando longos)
  - **Conclusão da Unidade** → slide com estilo destacado
  - Linhas de ruído (Shutterstock, Explorar etc.) são descartadas
- Pré-visualização HTML em iframe com tema claro/escuro
- Exportação para PDF (1280×720, uma página por slide)
- API REST com três endpoints: `/api/slides/generate`, `/api/slides/preview`, `/api/slides/pdf`

## Estrutura

```text
src/
├── core/              # config (pydantic-settings) e exceções
├── schemas/           # DTOs Pydantic v2
├── services/          # parser, renderer HTML, renderer PDF
├── controllers/       # orquestração
├── api/
│   ├── app.py         # factory FastAPI
│   ├── dependencies.py
│   └── routers/       # rotas /api/slides/*
├── templates/         # slides.html + slide_styles.css (Jinja2)
├── static/            # frontend single-page (HTML+CSS+JS)
└── server.py          # entrypoint uvicorn
tests/                 # pytest do parser
```

## Instalação

WeasyPrint depende de bibliotecas C nativas (Cairo, Pango, GDK-PixBuf).
No Ubuntu/Debian/WSL:

```bash
sudo apt-get update
sudo apt-get install -y libpango-1.0-0 libpangoft2-1.0-0 libcairo2 libgdk-pixbuf-2.0-0
```

Depois, dentro do projeto:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

(Ou `pip install -e ".[dev]"` para incluir as dependências de teste.)

## Execução

```bash
source .venv/bin/activate
python -m src.server
```

A interface web fica em `http://localhost:8000` e a documentação OpenAPI em
`http://localhost:8000/docs`.

## Uso da API

### POST `/api/slides/generate`

Gera o JSON estruturado e o HTML completo do deck.

```json
{
  "text": "Aula 1: ...",
  "deck_title": null,
  "theme": "default"
}
```

### POST `/api/slides/preview`

Mesmo payload, retorna apenas `text/html` para uso direto em iframe.

### POST `/api/slides/pdf`

Mesmo payload, retorna `application/pdf` com `Content-Disposition: attachment`.

## Testes

```bash
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Formato de entrada esperado

```text
Aula 1: Título da Aula
Título da Seção
Parágrafo introdutório com explicação textual.

Outra Seção
Termo: descrição razoavelmente longa do conceito.
Outro Termo: descrição do segundo conceito.

Aula 2: Próxima Aula
...

Conclusão da Unidade
Texto de fechamento da apresentação.
```

Heurísticas usadas:

- Linhas que casam `Aula \d+:` viram slides de capa
- Linhas curtas (≤ 90 caracteres), começando com maiúscula e sem terminação `.!,;:` viram títulos de seção (aceitam `?` para perguntas)
- Linhas no formato `Termo: descrição` viram bullets se o termo tiver até 8 palavras, parênteses balanceados e nenhum verbo de ligação (é, são, foi…)
- Demais linhas são tratadas como parágrafos

## Prompt para gerar conteúdo com IA

Cole o prompt abaixo em qualquer assistente (ChatGPT, Claude, Gemini, Copilot…)
substituindo `[TEMA]` pelo assunto desejado. A saída poderá ser colada
diretamente na ferramenta sem nenhum ajuste.

````text
Você é um assistente que produz roteiros de slides em texto puro. Sua saída
será processada por um parser automático que segue regras estritas — siga-as
com precisão. Não use Markdown, HTML, asteriscos, hífens de bullet, emojis,
crases ou blocos de código. Devolva APENAS o texto bruto no formato abaixo.

REGRAS DE FORMATAÇÃO

1. Cada aula começa com uma linha exatamente no formato:
   Aula N: Título da Aula
   Onde N é um número inteiro começando em 1 e incrementando.

2. Logo após uma linha de aula (ou de outra seção) pode vir um título de seção.
   Um título de seção é uma linha curta (até 90 caracteres), começa com letra
   maiúscula, é multipalavra e NÃO termina em ponto final, vírgula, ponto e
   vírgula ou dois-pontos. Pode terminar em "?" para perguntas.

3. Após um título de seção, escreva um ou mais parágrafos explicativos. Cada
   parágrafo deve ser uma frase ou um pequeno conjunto de frases em uma única
   linha, terminando com ponto final. Separe parágrafos com uma linha em branco.

4. Para listas de itens use o padrão "Termo: descrição" em uma única linha,
   sempre separados por uma linha em branco entre si. Restrições do termo:
   - Começa com letra maiúscula.
   - Tem no máximo 8 palavras e 80 caracteres.
   - Não contém ponto, vírgula, ponto-de-exclamação, interrogação ou
     ponto-e-vírgula.
   - Parênteses, se houver, devem estar balanceados.
   - NÃO contém verbos de ligação ("é", "são", "foi", "está", "tem", etc.).
   A descrição vem após os dois-pontos, com pelo menos 20 caracteres.

5. A última seção da última aula deve ser intitulada "Conclusão da Unidade"
   (ou começar com "Conclus") para receber estilo destacado.

6. Não inclua numeração nas seções (nada de "1. Introdução"), nem cabeçalhos
   redundantes como "Tópico 1", "Resumo", "Sumário". Não inclua linhas de
   ruído como "Compartilhar", "Explorar", "Ver mais".

ESTRUTURA RECOMENDADA POR AULA

- 1 linha de título da aula
- 2 a 4 seções
- Cada seção tem 1 parágrafo explicativo (40 a 120 palavras) e/ou uma lista
  de bullets (3 a 6 itens)

EXEMPLO DE SAÍDA VÁLIDA

Aula 1: Fundamentos da Lógica Digital
Introdução ao Pensamento Binário
A eletrônica digital trabalha apenas com dois estados, ligado e desligado, representados por níveis de tensão bem definidos. Essa abordagem torna os sistemas mais imunes a ruídos do que circuitos analógicos.

Portas Lógicas Fundamentais
As portas lógicas são os blocos de construção de qualquer circuito digital. Cada uma aplica uma regra específica entre suas entradas para produzir uma saída.

Porta NOT (Inversora): inverte o sinal de entrada, transformando 0 em 1 e 1 em 0.

Porta AND (E): produz 1 apenas quando todas as entradas estão em nível alto simultaneamente.

Porta OR (OU): produz 1 sempre que pelo menos uma das entradas está em nível alto.

Conclusão da Unidade
O aluno deve ser capaz de identificar estados binários, descrever as portas básicas e relacioná-las a circuitos do cotidiano.

TAREFA

Gere agora um roteiro de slides sobre: [TEMA]
Quantidade de aulas: [N]
Público-alvo: [DESCRIÇÃO DO PÚBLICO]

Retorne apenas o texto formatado conforme as regras acima. Nada mais.
````
