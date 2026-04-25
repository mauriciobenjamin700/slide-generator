import pytest

from src.core import EmptyInputError
from src.schemas import SlideKind
from src.services import SlideParserService

SAMPLE_TEXT: str = """Aula 1: Fundamentos da Lógica Digital e Portas Lógicas
Introdução ao Pensamento Binário
A eletrônica digital baseia-se na ideia de que toda informação pode ser representada por apenas dois estados: Ligado (1) ou Desligado (0). No nível do hardware, esses estados são representados por níveis de tensão.

As Portas Lógicas Fundamentais
As portas lógicas são os "tijolos" de qualquer processador ou circuito digital.

Porta NOT (Inversora): É a mais simples. Se entrar 0, sai 1. Se entrar 1, sai 0.

Porta AND (E): A saída só é nível alto se todas as entradas forem nível alto na eletrônica.

Porta OR (OU): Basta uma entrada ser 1 para a saída ser 1 nesse circuito paralelo.

Shutterstock
Explorar

Aula 2: Conversores Analógico-Digitais
A Ponte entre dois Mundos
O mundo real é analógico, mas o computador só entende números binários discretos.

Conclusão da Unidade
Ao final destas aulas o aluno entende sensores, conversores e portas lógicas em conjunto.
"""


@pytest.fixture
def parser() -> SlideParserService:
    """Provide a fresh parser instance for each test.

    Returns:
        A new `SlideParserService` instance.
    """
    return SlideParserService()


async def test_parse_extracts_two_lessons(parser: SlideParserService) -> None:
    """The parser must produce a lesson title slide for each `Aula N:` header."""
    deck = await parser.parse(SAMPLE_TEXT)
    lesson_titles = [s for s in deck.slides if s.kind == SlideKind.LESSON_TITLE]
    assert len(lesson_titles) == 2
    assert lesson_titles[0].subtitle == "Aula 1"
    assert lesson_titles[1].subtitle == "Aula 2"


async def test_parse_groups_bullets(parser: SlideParserService) -> None:
    """Bullet lines under one section must end up in a single BULLETS slide."""
    deck = await parser.parse(SAMPLE_TEXT)
    bullet_slides = [s for s in deck.slides if s.kind == SlideKind.BULLETS]
    assert len(bullet_slides) == 1
    bullets = bullet_slides[0].bullets
    assert len(bullets) == 3
    terms = {bullet.term for bullet in bullets}
    assert terms == {"Porta NOT (Inversora)", "Porta AND (E)", "Porta OR (OU)"}


async def test_parse_filters_junk_lines(parser: SlideParserService) -> None:
    """Junk markers like 'Shutterstock' and 'Explorar' should never become slides."""
    deck = await parser.parse(SAMPLE_TEXT)
    titles = [s.title for s in deck.slides]
    assert "Shutterstock" not in titles
    assert "Explorar" not in titles


async def test_parse_marks_conclusion(parser: SlideParserService) -> None:
    """Sections whose title contains 'Conclus' must use the CONCLUSION variant."""
    deck = await parser.parse(SAMPLE_TEXT)
    conclusion_slides = [s for s in deck.slides if s.kind == SlideKind.CONCLUSION]
    assert len(conclusion_slides) == 1
    assert "Conclusão" in conclusion_slides[0].title


async def test_parse_assigns_sequential_numbers(parser: SlideParserService) -> None:
    """Each slide must receive a 1-based slide_number in deck order."""
    deck = await parser.parse(SAMPLE_TEXT)
    numbers = [s.slide_number for s in deck.slides]
    assert numbers == list(range(1, len(deck.slides) + 1))


async def test_parse_uses_first_lesson_as_default_title(parser: SlideParserService) -> None:
    """When no deck title is supplied, the first lesson's title is used."""
    deck = await parser.parse(SAMPLE_TEXT)
    assert deck.title.startswith("Fundamentos da Lógica Digital")


async def test_parse_respects_explicit_deck_title(parser: SlideParserService) -> None:
    """An explicit deck_title must override the default first-lesson title."""
    deck = await parser.parse(SAMPLE_TEXT, deck_title="Eletrônica Digital — 2º Ano")
    assert deck.title == "Eletrônica Digital — 2º Ano"


async def test_parse_rejects_empty_input(parser: SlideParserService) -> None:
    """Empty or whitespace-only input must raise EmptyInputError."""
    with pytest.raises(EmptyInputError):
        await parser.parse("   \n\n  ")


async def test_paragraph_with_inline_colon_is_not_a_bullet(parser: SlideParserService) -> None:
    """Paragraphs whose first colon appears far in must not be classified as bullets."""
    text = (
        "Aula 1: Teste\n"
        "Seção\n"
        "A eletrônica digital baseia-se na ideia de que toda informação pode ser representada "
        "por apenas dois estados: Ligado (1) ou Desligado (0).\n"
    )
    deck = await parser.parse(text)
    bullets = [s for s in deck.slides if s.kind == SlideKind.BULLETS]
    assert bullets == []


async def test_paragraph_with_copula_verb_is_not_a_bullet(parser: SlideParserService) -> None:
    """Sentences like 'O mundo real é analógico: ...' must stay paragraphs."""
    text = (
        "Aula 1: Teste\n"
        "Seção\n"
        "O mundo real é analógico: a temperatura não pula de 20°C para 21°C; "
        "ela passa por todos os valores intermediários.\n"
    )
    deck = await parser.parse(text)
    bullets = [s for s in deck.slides if s.kind == SlideKind.BULLETS]
    assert bullets == []
    content_slides = [s for s in deck.slides if s.kind == SlideKind.CONTENT]
    assert len(content_slides) == 1
    assert "mundo real" in content_slides[0].paragraphs[0]


async def test_unbalanced_parentheses_in_head_rejects_bullet(parser: SlideParserService) -> None:
    """Lines with an unclosed '(' before the colon must not be bullets."""
    text = (
        "Aula 1: Teste\n"
        "Seção\n"
        "O processo de transformar uma tensão (ex: vinda de um microfone) em "
        "um número binário envolve três etapas principais.\n"
    )
    deck = await parser.parse(text)
    bullets = [s for s in deck.slides if s.kind == SlideKind.BULLETS]
    assert bullets == []


async def test_section_heading_can_end_with_question_mark(parser: SlideParserService) -> None:
    """Headings phrased as questions ('O que são X?') must be recognized as sections."""
    text = (
        "Aula 1: Sensores\n"
        "O que são Sensores e Transdutores?\n"
        "Um sensor é um dispositivo que detecta uma mudança em uma grandeza física e "
        "responde com um sinal elétrico.\n"
    )
    deck = await parser.parse(text)
    content_slides = [s for s in deck.slides if s.kind == SlideKind.CONTENT]
    assert len(content_slides) == 1
    assert content_slides[0].title == "O que são Sensores e Transdutores?"
