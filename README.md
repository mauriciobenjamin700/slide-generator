# Slide Generator

Ferramenta web para transformar textos pedagógicos estruturados em **slides
HTML** ou **gabaritos** e exportá-los como PDF. Construída com FastAPI,
Pydantic v2, Jinja2 e WeasyPrint, seguindo arquitetura em camadas
(router → controller → service).

## Funcionalidades

### Slides

- Parser que reconhece automaticamente:
  - **Aula N: Título** → slide de capa com numeração da aula
  - **Cabeçalhos curtos** → títulos de seção dos slides
  - **Termo: descrição** → bullets agrupados em slides de lista
  - **Parágrafos** → slides de conteúdo (com quebra automática quando longos)
  - **Notas: ...** → notas do apresentador (anexadas ao parágrafo ou bullet imediatamente acima)
  - **Conclusão da Unidade** → slide com estilo destacado
  - Linhas de ruído (Shutterstock, Explorar etc.) são descartadas
- Pré-visualização HTML em iframe com tema claro/escuro
- **Múltiplos formatos de exportação** a partir do mesmo texto:
  - **PDF** (1280×720, uma página por slide)
  - **PPTX** (PowerPoint 16:9, com notas no painel do apresentador)
  - **DOCX handout** (1 slide por página com bloco "Notas do apresentador")
  - **Markdown reveal.js** (`---` entre slides, `Note:` para notas)
- API REST: `/api/slides/{generate,preview,pdf,pptx,docx,markdown}`

### Gabaritos

- Parser que reconhece:
  - **Título:** e **Subtítulo:** para o cabeçalho do documento
  - **Parte N: ...**, **Seção ...**, **Capítulo ...** ou qualquer linha que se
    pareça com um cabeçalho → cria uma nova seção
  - **`1.`** ou **`1)`** no início da linha → nova questão
  - **`R:`** ou **`Resposta:`** → resposta da questão anterior
  - Continuações em múltiplas linhas são juntadas automaticamente
- HTML inline com CSS dedicado, suporta inline HTML (ex.:
  `<span class="overline">A</span>` para barra de inversão booleana)
- **Múltiplos formatos de exportação**:
  - **PDF** A4 com codificação UTF-8 correta
  - **DOCX** editável (com inline HTML automaticamente convertido para texto plano)
  - **Markdown** com cabeçalhos e blockquotes
- API REST: `/api/answer-keys/{generate,preview,pdf,docx,markdown}`

### Interface

Frontend single-page com **abas** que alternam entre os dois geradores. Cada
aba traz seu próprio campo de texto, controles e pré-visualização em iframe.

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

### POST `/api/slides/pptx`

Mesmo payload, retorna `application/vnd.openxmlformats-officedocument.presentationml.presentation` com download de `slides.pptx` (16:9 widescreen, notas do apresentador no painel correspondente).

### POST `/api/slides/docx`

Mesmo payload, retorna `application/vnd.openxmlformats-officedocument.wordprocessingml.document` com download de `slides_handout.docx`. Layout em handout: um slide por página, bloco "Notas do apresentador" preenchido com as `Notas:` do texto ou linhas em branco para anotação manual.

### POST `/api/slides/markdown`

Mesmo payload, retorna `text/markdown; charset=utf-8` com download de `slides.md` no formato reveal.js (`---` entre slides, `Note:` para notas do apresentador).

### POST `/api/answer-keys/generate`

Gera o JSON estruturado e o HTML completo do gabarito.

```json
{
  "text": "Título: ...\nSubtítulo: ...\n\nParte 1: ...\n\n1. Pergunta?\nR: Resposta.",
  "title": null,
  "subtitle": null,
  "theme": "default"
}
```

### POST `/api/answer-keys/preview`

Mesmo payload, retorna apenas `text/html` para uso direto em iframe.

### POST `/api/answer-keys/pdf`

Mesmo payload, retorna `application/pdf` com `Content-Disposition: attachment`
(`gabarito.pdf`).

### POST `/api/answer-keys/docx`

Mesmo payload, retorna o gabarito como Word (`gabarito.docx`). Inline HTML
(ex.: `<span class="overline">A</span>`) é convertido para texto plano.

### POST `/api/answer-keys/markdown`

Mesmo payload, retorna `text/markdown; charset=utf-8` com download de
`gabarito.md` (cabeçalhos `##` por seção, perguntas em **negrito**, respostas
em blockquote `>`).

## Testes

```bash
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Formato de entrada esperado

### Entrada de slides

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
- Linhas começando com `Notas:` (ou `Note:`/`Nota:`) anexam notas do apresentador ao parágrafo ou bullet imediatamente acima — visíveis no PPTX, no DOCX handout e no Markdown reveal.js, ocultas no PDF e na pré-visualização HTML
- Demais linhas são tratadas como parágrafos

### Entrada de gabarito

```text
Título: Gabarito de Eletrônica Digital e Sensores
Subtítulo: Disciplina: Eletrônica Digital | 2º Ano Técnico

Parte 1: Portas Lógicas e Álgebra Booleana

1. Explique a diferença entre sinal analógico e digital.
R: O sinal analógico é contínuo no tempo e pode assumir infinitos valores. O digital é discreto.

2. Qual é a função da porta lógica NOT?
R: Inverte a entrada. Representada por uma barra: Y = <span class="overline">A</span>.

Parte 2: Conversores (ADC e DAC)

8. O que significa a sigla ADC?
R: Analog-to-Digital Converter. Resolução ≈ 4,88 mV em 10 bits / 5V.
```

Heurísticas usadas:

- `Título:` e `Subtítulo:` (sem distinção entre maiúsculas/minúsculas) populam o cabeçalho do documento
- Linhas iniciadas por `<número>.` ou `<número>)` viram novas questões; o número é mantido como parte do texto
- `R:`, `Resposta:`, `A:` ou `Answer:` (case-insensitive) iniciam a resposta da última questão
- Linhas que não casam com nenhum padrão acima e parecem cabeçalhos curtos abrem uma nova seção
- Linhas em continuação (sem prefixo) são juntadas com espaço à pergunta ou resposta corrente
- HTML inline (ex.: `<span class="overline">A</span>`, `<strong>`) é renderizado direto — útil para notação booleana e ênfase

## Prompts para gerar conteúdo com IA

Cole o prompt apropriado em qualquer assistente (ChatGPT, Claude, Gemini,
Copilot…) substituindo os placeholders entre colchetes pelo conteúdo
desejado. A saída poderá ser colada diretamente na ferramenta sem ajustes.

### Prompt para slides

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

7. (Opcional) Para anexar notas do apresentador a um parágrafo ou bullet,
   use uma linha imediatamente após o conteúdo no formato:
   Notas: texto da nota em uma única linha.
   As notas aparecem no painel do PowerPoint, no DOCX handout e no Markdown
   reveal.js, mas não na pré-visualização HTML nem no PDF.

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

### Prompt para gabarito

````text
Você é um assistente que produz gabaritos de exercícios em texto puro. Sua
saída será processada por um parser automático que segue regras estritas —
siga-as com precisão. Não use Markdown (asteriscos, hífens de bullet,
crases, blocos de código), nem emojis. Devolva APENAS o texto bruto no
formato abaixo.

REGRAS DE FORMATAÇÃO

1. As duas primeiras linhas devem ser, nesta ordem:
   Título: [Título do gabarito]
   Subtítulo: [Disciplina, ano, turma — informações curtas separadas por |]

2. Agrupe as questões em seções. Cada seção começa com uma linha de
   cabeçalho do tipo:
   Parte N: Título da Parte
   (também aceitos: "Seção N:", "Capítulo N:", "Módulo N:"). Deixe uma linha
   em branco antes e depois do cabeçalho.

3. Cada questão é um par de duas linhas separado por uma linha em branco
   das próximas:
   N. Texto da pergunta terminando em ponto final ou interrogação.
   R: Texto da resposta terminando em ponto final.

   Onde N é a numeração contínua (1, 2, 3, ...) ao longo de todo o
   documento, NÃO reiniciando a cada seção.

4. Para notação booleana com barra de inversão sobre uma variável, use
   exatamente: <span class="overline">A</span>
   (substitua "A" pela variável correspondente). NÃO use combinações de
   caracteres Unicode como A̅, pois não renderizam bem em PDF.

5. Não use Markdown nem outros tags HTML além de <span class="overline">.
   Símbolos matemáticos comuns como ·, ≈, →, ², ³ podem ser usados
   diretamente.

6. Cada resposta deve ser objetiva: 1 a 4 frases, sem listas internas.

EXEMPLO DE SAÍDA VÁLIDA

Título: Gabarito de Eletrônica Digital e Sensores
Subtítulo: Disciplina: Eletrônica Digital | 2º Ano Técnico

Parte 1: Portas Lógicas e Álgebra Booleana

1. Explique a diferença fundamental entre um sinal analógico e um sinal digital.
R: O sinal analógico é contínuo no tempo e pode assumir infinitos valores em uma faixa. O digital é discreto, possuindo estados definidos (0 e 1).

2. Qual é a função da porta lógica NOT e como ela é representada?
R: Sua função é a inversão lógica. É representada por uma barra sobre a variável: Y = <span class="overline">A</span>.

Parte 2: Conversores (ADC e DAC)

3. O que significa a sigla ADC?
R: Analog-to-Digital Converter. Converte uma grandeza analógica em um número binário processável pelo microcontrolador.

TAREFA

Gere agora um gabarito sobre: [TEMA]
Quantidade total de questões: [N]
Quantidade de seções/partes: [M]
Público-alvo: [DESCRIÇÃO DO PÚBLICO]

Retorne apenas o texto formatado conforme as regras acima. Nada mais.
````
