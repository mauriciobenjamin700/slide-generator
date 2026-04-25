import pytest

from src.core import EmptyInputError
from src.services import AnswerKeyParserService

SAMPLE_TEXT: str = (
    "Título: Gabarito de Eletrônica Digital e Sensores\n"
    "Subtítulo: Disciplina: Eletrônica Digital | 2º Ano Técnico\n"
    "\n"
    "Parte 1: Portas Lógicas e Álgebra Booleana\n"
    "\n"
    "1. Explique a diferença entre sinal analógico e digital.\n"
    "R: O sinal analógico é contínuo no tempo. O sinal digital é "
    "discreto.\n"
    "\n"
    "2. Qual é a função da porta lógica NOT?\n"
    "R: Sua função é a inversão lógica. Se a entrada é 1, a saída é 0.\n"
    "\n"
    "Parte 2: Conversores (ADC e DAC)\n"
    "\n"
    "8. O que significa a sigla ADC?\n"
    "R: ADC é o conversor analógico-digital.\n"
)


@pytest.mark.asyncio
async def test_parse_extracts_title_and_subtitle() -> None:
    """The parser should populate the title and subtitle metadata."""
    parser: AnswerKeyParserService = AnswerKeyParserService()
    result = await parser.parse(SAMPLE_TEXT)
    assert result.title == "Gabarito de Eletrônica Digital e Sensores"
    assert result.subtitle == (
        "Disciplina: Eletrônica Digital | 2º Ano Técnico"
    )


@pytest.mark.asyncio
async def test_parse_groups_items_by_section() -> None:
    """Each section heading should accumulate the questions that follow."""
    parser: AnswerKeyParserService = AnswerKeyParserService()
    result = await parser.parse(SAMPLE_TEXT)
    assert len(result.sections) == 2
    first, second = result.sections
    assert first.title == "Parte 1: Portas Lógicas e Álgebra Booleana"
    assert second.title == "Parte 2: Conversores (ADC e DAC)"
    assert len(first.items) == 2
    assert len(second.items) == 1


@pytest.mark.asyncio
async def test_parse_keeps_question_numbering_in_text() -> None:
    """The numbered prefix should remain part of the question text."""
    parser: AnswerKeyParserService = AnswerKeyParserService()
    result = await parser.parse(SAMPLE_TEXT)
    first_question: str = result.sections[0].items[0].question
    assert first_question.startswith("1. ")


@pytest.mark.asyncio
async def test_parse_joins_multiline_answers_with_spaces() -> None:
    """Continuation lines after R: should be joined into one answer string."""
    text: str = (
        "Parte 1: X\n"
        "\n"
        "1. Pergunta?\n"
        "R: Linha um.\n"
        "Linha dois continua aqui.\n"
    )
    parser: AnswerKeyParserService = AnswerKeyParserService()
    result = await parser.parse(text)
    answer: str = result.sections[0].items[0].answer
    assert answer == "Linha um. Linha dois continua aqui."


@pytest.mark.asyncio
async def test_parse_overrides_title_via_argument() -> None:
    """An explicit `title` argument should win over the inline metadata."""
    parser: AnswerKeyParserService = AnswerKeyParserService()
    result = await parser.parse(SAMPLE_TEXT, title="Override")
    assert result.title == "Override"


@pytest.mark.asyncio
async def test_parse_overrides_subtitle_via_argument() -> None:
    """An explicit `subtitle` argument should win over the inline metadata."""
    parser: AnswerKeyParserService = AnswerKeyParserService()
    result = await parser.parse(SAMPLE_TEXT, subtitle="Override sub")
    assert result.subtitle == "Override sub"


@pytest.mark.asyncio
async def test_parse_raises_on_empty_text() -> None:
    """Empty input should be rejected with EmptyInputError."""
    parser: AnswerKeyParserService = AnswerKeyParserService()
    with pytest.raises(EmptyInputError):
        await parser.parse("   \n\n  \t")


@pytest.mark.asyncio
async def test_parse_creates_default_section_when_none_given() -> None:
    """Q/A pairs without a heading should land in a default section."""
    text: str = "1. Pergunta?\nR: Resposta.\n"
    parser: AnswerKeyParserService = AnswerKeyParserService()
    result = await parser.parse(text)
    assert len(result.sections) == 1
    assert result.sections[0].items[0].answer == "Resposta."


@pytest.mark.asyncio
async def test_parse_accepts_resposta_alias() -> None:
    """'Resposta:' should work as an alternative to 'R:' for answers."""
    text: str = (
        "Parte 1: Teste\n"
        "\n"
        "1. Pergunta?\n"
        "Resposta: Texto da resposta longa.\n"
    )
    parser: AnswerKeyParserService = AnswerKeyParserService()
    result = await parser.parse(text)
    assert result.sections[0].items[0].answer == "Texto da resposta longa."


@pytest.mark.asyncio
async def test_total_items_property() -> None:
    """The schema property should sum items across every section."""
    parser: AnswerKeyParserService = AnswerKeyParserService()
    result = await parser.parse(SAMPLE_TEXT)
    assert result.total_items == 3
