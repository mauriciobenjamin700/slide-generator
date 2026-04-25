from weasyprint import HTML

# Content for the PDF based on the previous conversation
content = {
    "Parte 1: Portas Lógicas e Álgebra Booleana": [
        ("1. Explique a diferença fundamental entre um sinal analógico e um sinal digital.",
         "O sinal analógico é contínuo no tempo e pode assumir infinitos valores em uma faixa (ex: temperatura). O sinal digital é discreto, possuindo estados definidos (geralmente 0 e 1) e mudando em passos ou degraus."),
        ("2. Qual é a função da porta lógica NOT e como ela é representada em uma expressão booleana?",
         "Sua função é a inversão lógica. Se a entrada é 1, a saída é 0; se a entrada é 0, a saída é 1. É representada por uma barra sobre a variável (Y = <span class=\"overline\">A</span>)."),
        ("3. Desenhe a tabela verdade para uma porta AND de duas entradas (A e B). Em qual única condição a saída será 1?",
         "Tabela: 0 e 0 = 0; 0 e 1 = 0; 1 e 0 = 0; 1 e 1 = 1. A saída será 1 somente quando todas as entradas forem 1 simultaneamente."),
        ("4. Considere uma porta OR com três entradas. Se as entradas forem A=0, B=1 e C=0, qual será o nível lógico da saída?",
         "A saída será 1. Na lógica OR, basta que uma das entradas seja nível alto para que a saída também seja."),
        ("5. Por que as portas NAND e NOR são frequentemente chamadas de 'portas universais'?",
         "Elas recebem esse nome porque qualquer outra porta lógica (AND, OR, NOT, etc.) ou circuito digital complexo pode ser construído utilizando-se exclusivamente combinações de portas NAND ou apenas portas NOR."),
        ("6. O que diferencia a porta lógica XOR (OU Exclusivo) de uma porta OR convencional?",
         "Na porta OR, a saída é 1 se ao menos uma entrada for 1 (incluindo o caso de ambas serem 1). Na XOR, a saída é 1 se as entradas forem diferentes; se ambas forem 1, a saída será 0."),
        ("7. Dada a expressão booleana Y = A · <span class=\"overline\">B</span> + C, determine o valor de Y quando A=1, B=1 e C=0.",
         "Y = 1 · <span class=\"overline\">1</span> + 0 → Y = 1 · 0 + 0 → Y = 0.")
    ],
    "Parte 2: Conversores (ADC e DAC)": [
        ("8. O que significa a sigla ADC e qual a sua importância para sistemas baseados em microcontroladores?",
         "ADC (Analog-to-Digital Converter) é o conversor analógico-digital. Ele permite que o microcontrolador 'leia' grandezas do mundo real e as transforme em números binários processáveis."),
        ("9. Defina o processo de 'Amostragem' em um conversor analógico-digital.",
         "É o processo de medir o valor do sinal analógico em intervalos de tempo periódicos, registrando a voltagem em pontos específicos para posterior processamento."),
        ("10. Um conversor ADC de 8 bits possui quantas combinações ou níveis digitais possíveis?",
         "O número de níveis é 2^n. Para 8 bits: 2^8 = 256 níveis (representando valores de 0 a 255)."),
        ("11. Se um ADC de 10 bits possui referência de 5V, qual é o valor aproximado da sua resolução?",
         "Resolução = 5V / (2^10) = 5V / 1024 ≈ 4,88 mV."),
        ("12. Explique o que acontece na etapa de 'Quantização' de um sinal.",
         "O valor amostrado é arredondado para o nível digital mais próximo disponível na escala do conversor, podendo gerar pequenos erros de precisão."),
        ("13. Qual é a função de um conversor DAC em um sistema de som digital?",
         "Converte dados binários da música em tensão elétrica variável para que um amplificador e alto-falante possam recriar ondas sonoras."),
        ("14. O que ocorre com a fidelidade de um sinal se aumentarmos a taxa de bits?",
         "Aumentamos a fidelidade, pois os degraus entre os valores digitais tornam-se menores, aproximando o sinal digitalizado do original analógico.")
    ],
    "Parte 3: Sensores e Transdutores": [
        ("15. Diferencie 'Sensor' de 'Transdutor' de acordo com as definições técnicas.",
         "O sensor detecta a mudança física. O transdutor é o dispositivo que converte uma forma de energia (calor, luz) em outra (sinal elétrico)."),
        ("16. Cite dois exemplos de sensores com saída puramente digital (ON/OFF).",
         "Sensor PIR (presença) usado em alarmes e Chave Fim de Curso usada para indicar o limite de movimento de um portão."),
        ("17. O sensor LDR varia qual grandeza física em resposta à luz? Ele é analógico ou digital?",
         "Varia sua Resistência Elétrica. É um sensor Analógico, pois a mudança ocorre de forma contínua."),
        ("18. Como funciona o sensor ultrassônico (HC-SR04) para medir distâncias?",
         "Emite um pulso de som e mede o tempo de retorno (eco). A distância é calculada baseada na velocidade do som no ar."),
        ("19. Para detectar garrafas plásticas, qual sensor é mais indicado: indutivo ou capacitivo?",
         "Capacitivo. Sensores indutivos detectam apenas metais, enquanto capacitivos detectam materiais diversos como plásticos e líquidos."),
        ("20. Defina o termo 'Sensibilidade' no contexto de sensores eletrônicos.",
         "É a razão entre a variação do sinal de saída e a variação da grandeza física de entrada, indicando a precisão da resposta do componente.")
    ]
}

html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Gabarito: Eletrônica Digital e Sensores</title>
    <style>
        @page {
            size: A4;
            margin: 20mm;
            background-color: #ffffff;
        }
        body {
            font-family: 'DejaVu Sans', 'Liberation Sans', 'Helvetica', 'Arial', sans-serif;
            color: #333;
            line-height: 1.5;
        }
        .header {
            text-align: center;
            border-bottom: 3px solid #2c3e50;
            margin-bottom: 30px;
            padding-bottom: 10px;
        }
        h1 {
            color: #2c3e50;
            font-size: 22pt;
            margin: 0;
        }
        h2 {
            color: #2980b9;
            font-size: 16pt;
            border-left: 5px solid #2980b9;
            padding-left: 10px;
            margin-top: 30px;
        }
        .item {
            margin-bottom: 20px;
            page-break-inside: avoid;
        }
        .question {
            font-weight: bold;
            color: #2c3e50;
            display: block;
            margin-bottom: 5px;
        }
        .answer {
            display: block;
            background-color: #f9f9f9;
            padding: 10px;
            border-radius: 5px;
            border-left: 3px solid #7f8c8d;
            font-style: italic;
        }
        .overline {
            text-decoration: overline;
        }
        .footer {
            margin-top: 50px;
            text-align: center;
            font-size: 9pt;
            color: #95a5a6;
            border-top: 1px solid #eee;
            padding-top: 10px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Gabarito: Eletrônica Digital e Sensores</h1>
        <p>Disciplina: Eletrônica Digital | 2º Ano Técnico</p>
    </div>
"""

for section, items in content.items():
    html_content += f"<h2>{section}</h2>"
    for q, a in items:
        html_content += f"""
        <div class="item">
            <span class="question">{q}</span>
            <span class="answer"><strong>Resposta:</strong> {a}</span>
        </div>
        """

html_content += """
    <div class="footer">
        Documento gerado para apoio pedagógico.
    </div>
</body>
</html>
"""

with open("gabarito.html", "w", encoding="utf-8") as f:
    f.write(html_content)

HTML(string=html_content, encoding="utf-8").write_pdf("Gabarito_Eletronica_Digital_Sensores.pdf")
