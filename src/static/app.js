const SAMPLE_TEXT = `Aula 1: Fundamentos da Lógica Digital e Portas Lógicas
Introdução ao Pensamento Binário
A eletrônica digital baseia-se na ideia de que toda informação pode ser representada por apenas dois estados: Ligado (1) ou Desligado (0). No nível do hardware, esses estados são representados por níveis de tensão (geralmente 0V para o nível baixo e 5V ou 3.3V para o nível alto). Diferente da eletrônica analógica, onde a tensão varia continuamente, a digital ignora pequenas variações, o que torna os sistemas muito mais imunes a ruídos.

As Portas Lógicas Fundamentais
As portas lógicas são os "tijolos" de qualquer processador ou circuito digital. Elas recebem sinais de entrada, processam de acordo com uma regra lógica e entregam um resultado.

Porta NOT (Inversora): É a mais simples. Se entrar 0, sai 1. Se entrar 1, sai 0. Ela é essencial para criar sinais de controle complementares.

Porta AND (E): Imagine um circuito com dois interruptores em série. A lâmpada só acende se o primeiro E o segundo estiverem fechados. Na eletrônica, a saída só é nível alto se todas as entradas forem nível alto.

Porta OR (OU): Funciona como dois interruptores em paralelo. A lâmpada acende se o primeiro OU o segundo (ou ambos) estiverem fechados. Basta uma entrada ser 1 para a saída ser 1.

Portas Derivadas e Lógica Combinacional
A partir das básicas, criamos portas como a NAND (o inverso da AND) e a NOR (o inverso da OR). Uma porta muito importante para o curso é a XOR (OU Exclusivo), que é usada em circuitos de soma aritmética: a saída é 1 apenas se as entradas forem diferentes entre si. Se ambas forem iguais (0 e 0 ou 1 e 1), a saída será 0.

Aula 2: Conversores Analógico-Digitais (ADC) e Digital-Analógicos (DAC)
A Ponte entre dois Mundos
O mundo real é analógico: a temperatura não pula de 20°C para 21°C; ela passa por todos os valores intermediários. Porém, o computador só entende números binários. Os conversores são os tradutores dessa comunicação.

Conversor Analógico-Digital (ADC)
O processo de transformar uma tensão (ex: vinda de um microfone) em um número binário envolve três etapas principais descritas para os alunos:

Amostragem: O circuito tira "fotos" da tensão em intervalos de tempo muito curtos.

Quantização: O valor da tensão é arredondado para o nível digital mais próximo disponível.

Codificação: Esse nível é transformado em um código binário (ex: 1010).

Conclusão da Unidade
Ao final destas três aulas, o aluno deve ser capaz de entender que um sensor capta uma informação, o conversor traduz essa informação para o "idioma" do computador, e as portas lógicas tomam decisões baseadas nesses dados.`;

const elements = {
    textInput: document.getElementById("text-input"),
    deckTitle: document.getElementById("deck-title"),
    themeSelect: document.getElementById("theme-select"),
    btnPreview: document.getElementById("btn-preview"),
    btnPdf: document.getElementById("btn-pdf"),
    btnSample: document.getElementById("btn-load-sample"),
    iframe: document.getElementById("preview-iframe"),
    previewEmpty: document.getElementById("preview-empty"),
    status: document.getElementById("status"),
    charCount: document.getElementById("char-count"),
    slideCount: document.getElementById("slide-count"),
};

function setStatus(message, kind) {
    elements.status.textContent = message;
    elements.status.classList.remove("success", "error");
    if (kind) {
        elements.status.classList.add(kind);
    }
}

function updateCharCount() {
    const length = elements.textInput.value.length;
    elements.charCount.textContent = `${length.toLocaleString("pt-BR")} caracteres`;
}

function buildPayload() {
    return {
        text: elements.textInput.value,
        deck_title: elements.deckTitle.value.trim() || null,
        theme: elements.themeSelect.value,
    };
}

async function generatePreview() {
    const text = elements.textInput.value.trim();
    if (!text) {
        setStatus("Cole algum texto antes de gerar.", "error");
        return;
    }
    setStatus("Gerando pré-visualização...");
    elements.btnPreview.disabled = true;
    try {
        const response = await fetch("/api/slides/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(buildPayload()),
        });
        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: "Falha desconhecida." }));
            throw new Error(error.detail || `HTTP ${response.status}`);
        }
        const data = await response.json();
        elements.iframe.srcdoc = data.html;
        elements.previewEmpty.classList.add("hidden");
        elements.btnPdf.disabled = false;
        elements.slideCount.textContent = `${data.deck.slides.length} slides`;
        setStatus(`Deck "${data.deck.title}" gerado com sucesso.`, "success");
    } catch (error) {
        setStatus(error.message || String(error), "error");
    } finally {
        elements.btnPreview.disabled = false;
    }
}

async function downloadPdf() {
    const text = elements.textInput.value.trim();
    if (!text) {
        setStatus("Cole algum texto antes de gerar.", "error");
        return;
    }
    setStatus("Gerando PDF...");
    elements.btnPdf.disabled = true;
    try {
        const response = await fetch("/api/slides/pdf", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(buildPayload()),
        });
        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: "Falha desconhecida." }));
            throw new Error(error.detail || `HTTP ${response.status}`);
        }
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "slides.pdf";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        setStatus("PDF gerado e baixado.", "success");
    } catch (error) {
        setStatus(error.message || String(error), "error");
    } finally {
        elements.btnPdf.disabled = false;
    }
}

function loadSample() {
    elements.textInput.value = SAMPLE_TEXT;
    updateCharCount();
    setStatus("Exemplo carregado. Clique em \"Gerar pré-visualização\".");
}

elements.btnPreview.addEventListener("click", generatePreview);
elements.btnPdf.addEventListener("click", downloadPdf);
elements.btnSample.addEventListener("click", loadSample);
elements.textInput.addEventListener("input", updateCharCount);
elements.themeSelect.addEventListener("change", () => {
    if (!elements.btnPdf.disabled) {
        generatePreview();
    }
});

updateCharCount();
