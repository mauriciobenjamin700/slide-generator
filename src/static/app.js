const SLIDES_SAMPLE = `Aula 1: Fundamentos da Lógica Digital e Portas Lógicas
Introdução ao Pensamento Binário
A eletrônica digital baseia-se na ideia de que toda informação pode ser representada por apenas dois estados: Ligado (1) ou Desligado (0). No nível do hardware, esses estados são representados por níveis de tensão (geralmente 0V para o nível baixo e 5V ou 3.3V para o nível alto). Diferente da eletrônica analógica, onde a tensão varia continuamente, a digital ignora pequenas variações, o que torna os sistemas muito mais imunes a ruídos.

As Portas Lógicas Fundamentais
As portas lógicas são os "tijolos" de qualquer processador ou circuito digital. Elas recebem sinais de entrada, processam de acordo com uma regra lógica e entregam um resultado.

Porta NOT (Inversora): É a mais simples. Se entrar 0, sai 1. Se entrar 1, sai 0. Ela é essencial para criar sinais de controle complementares.

Porta AND (E): Imagine um circuito com dois interruptores em série. A lâmpada só acende se o primeiro E o segundo estiverem fechados. Na eletrônica, a saída só é nível alto se todas as entradas forem nível alto.

Porta OR (OU): Funciona como dois interruptores em paralelo. A lâmpada acende se o primeiro OU o segundo (ou ambos) estiverem fechados. Basta uma entrada ser 1 para a saída ser 1.

Conclusão da Unidade
Ao final destas três aulas, o aluno deve ser capaz de entender que um sensor capta uma informação, o conversor traduz essa informação para o "idioma" do computador, e as portas lógicas tomam decisões baseadas nesses dados.`;

const ANSWER_KEY_SAMPLE = `Título: Gabarito de Eletrônica Digital e Sensores
Subtítulo: Disciplina: Eletrônica Digital | 2º Ano Técnico

Parte 1: Portas Lógicas e Álgebra Booleana

1. Explique a diferença fundamental entre um sinal analógico e um sinal digital.
R: O sinal analógico é contínuo no tempo e pode assumir infinitos valores em uma faixa (ex: temperatura). O sinal digital é discreto, possuindo estados definidos (geralmente 0 e 1) e mudando em passos ou degraus.

2. Qual é a função da porta lógica NOT e como ela é representada em uma expressão booleana?
R: Sua função é a inversão lógica. Se a entrada é 1, a saída é 0; se a entrada é 0, a saída é 1. É representada por uma barra sobre a variável (Y = <span class="overline">A</span>).

3. Desenhe a tabela verdade para uma porta AND de duas entradas.
R: Tabela: 0 e 0 = 0; 0 e 1 = 0; 1 e 0 = 0; 1 e 1 = 1. A saída será 1 somente quando todas as entradas forem 1 simultaneamente.

Parte 2: Conversores (ADC e DAC)

4. O que significa a sigla ADC e qual a sua importância para sistemas baseados em microcontroladores?
R: ADC (Analog-to-Digital Converter) é o conversor analógico-digital. Ele permite que o microcontrolador "leia" grandezas do mundo real e as transforme em números binários processáveis.

5. Se um ADC de 10 bits possui referência de 5V, qual é o valor aproximado da sua resolução?
R: Resolução = 5V / (2^10) = 5V / 1024 ≈ 4,88 mV.`;

function setStatus(node, message, kind) {
    node.textContent = message;
    node.classList.remove("success", "error");
    if (kind) {
        node.classList.add(kind);
    }
}

function updateCharCount(input, label) {
    const length = input.value.length;
    label.textContent = `${length.toLocaleString("pt-BR")} caracteres`;
}

function createPreviewBinder(iframe) {
    let currentUrl = null;
    return function setHtml(html) {
        if (currentUrl) {
            URL.revokeObjectURL(currentUrl);
        }
        const blob = new Blob([html], { type: "text/html" });
        currentUrl = URL.createObjectURL(blob);
        iframe.src = currentUrl;
    };
}

function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

async function postJson(path, payload) {
    const response = await fetch(path, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
    if (!response.ok) {
        let detail = `HTTP ${response.status}`;
        try {
            const error = await response.json();
            if (error && error.detail) {
                detail = error.detail;
            }
        } catch (_) {
            // ignore JSON parse errors and keep the default detail
        }
        throw new Error(detail);
    }
    return response;
}

function setupSlides() {
    const els = {
        input: document.getElementById("slides-input"),
        deckTitle: document.getElementById("deck-title"),
        theme: document.getElementById("slides-theme"),
        btnPreview: document.getElementById("slides-btn-preview"),
        btnPdf: document.getElementById("slides-btn-pdf"),
        btnSample: document.getElementById("slides-btn-sample"),
        iframe: document.getElementById("slides-iframe"),
        empty: document.getElementById("slides-empty"),
        status: document.getElementById("slides-status"),
        charCount: document.getElementById("slides-char-count"),
        slideCount: document.getElementById("slides-count"),
    };
    const setHtml = createPreviewBinder(els.iframe);

    function buildPayload() {
        return {
            text: els.input.value,
            deck_title: els.deckTitle.value.trim() || null,
            theme: els.theme.value,
        };
    }

    async function generate() {
        if (!els.input.value.trim()) {
            setStatus(els.status, "Cole algum texto antes de gerar.", "error");
            return;
        }
        setStatus(els.status, "Gerando pré-visualização...");
        els.btnPreview.disabled = true;
        try {
            const response = await postJson("/api/slides/generate", buildPayload());
            const data = await response.json();
            setHtml(data.html);
            els.empty.classList.add("hidden");
            els.btnPdf.disabled = false;
            els.slideCount.textContent = `${data.deck.slides.length} slides`;
            setStatus(els.status, `Deck "${data.deck.title}" gerado com sucesso.`, "success");
        } catch (error) {
            setStatus(els.status, error.message || String(error), "error");
        } finally {
            els.btnPreview.disabled = false;
        }
    }

    async function downloadPdf() {
        if (!els.input.value.trim()) {
            setStatus(els.status, "Cole algum texto antes de gerar.", "error");
            return;
        }
        setStatus(els.status, "Gerando PDF...");
        els.btnPdf.disabled = true;
        try {
            const response = await postJson("/api/slides/pdf", buildPayload());
            const blob = await response.blob();
            downloadBlob(blob, "slides.pdf");
            setStatus(els.status, "PDF gerado e baixado.", "success");
        } catch (error) {
            setStatus(els.status, error.message || String(error), "error");
        } finally {
            els.btnPdf.disabled = false;
        }
    }

    els.btnPreview.addEventListener("click", generate);
    els.btnPdf.addEventListener("click", downloadPdf);
    els.btnSample.addEventListener("click", () => {
        els.input.value = SLIDES_SAMPLE;
        updateCharCount(els.input, els.charCount);
        setStatus(els.status, 'Exemplo carregado. Clique em "Gerar pré-visualização".');
    });
    els.input.addEventListener("input", () => updateCharCount(els.input, els.charCount));
    els.theme.addEventListener("change", () => {
        if (!els.btnPdf.disabled) {
            generate();
        }
    });
    updateCharCount(els.input, els.charCount);
}

function setupAnswerKey() {
    const els = {
        input: document.getElementById("ak-input"),
        title: document.getElementById("ak-title"),
        subtitle: document.getElementById("ak-subtitle"),
        theme: document.getElementById("ak-theme"),
        btnPreview: document.getElementById("ak-btn-preview"),
        btnPdf: document.getElementById("ak-btn-pdf"),
        btnSample: document.getElementById("ak-btn-sample"),
        iframe: document.getElementById("ak-iframe"),
        empty: document.getElementById("ak-empty"),
        status: document.getElementById("ak-status"),
        charCount: document.getElementById("ak-char-count"),
        itemCount: document.getElementById("ak-count"),
    };
    const setHtml = createPreviewBinder(els.iframe);

    function buildPayload() {
        return {
            text: els.input.value,
            title: els.title.value.trim() || null,
            subtitle: els.subtitle.value.trim() || null,
            theme: els.theme.value,
        };
    }

    function totalItems(answerKey) {
        return answerKey.sections.reduce((acc, s) => acc + s.items.length, 0);
    }

    async function generate() {
        if (!els.input.value.trim()) {
            setStatus(els.status, "Cole algum texto antes de gerar.", "error");
            return;
        }
        setStatus(els.status, "Gerando pré-visualização...");
        els.btnPreview.disabled = true;
        try {
            const response = await postJson("/api/answer-keys/generate", buildPayload());
            const data = await response.json();
            setHtml(data.html);
            els.empty.classList.add("hidden");
            els.btnPdf.disabled = false;
            const total = totalItems(data.answer_key);
            const sections = data.answer_key.sections.length;
            els.itemCount.textContent = `${total} questões em ${sections} seção(ões)`;
            setStatus(els.status, `Gabarito "${data.answer_key.title}" gerado com sucesso.`, "success");
        } catch (error) {
            setStatus(els.status, error.message || String(error), "error");
        } finally {
            els.btnPreview.disabled = false;
        }
    }

    async function downloadPdf() {
        if (!els.input.value.trim()) {
            setStatus(els.status, "Cole algum texto antes de gerar.", "error");
            return;
        }
        setStatus(els.status, "Gerando PDF...");
        els.btnPdf.disabled = true;
        try {
            const response = await postJson("/api/answer-keys/pdf", buildPayload());
            const blob = await response.blob();
            downloadBlob(blob, "gabarito.pdf");
            setStatus(els.status, "PDF gerado e baixado.", "success");
        } catch (error) {
            setStatus(els.status, error.message || String(error), "error");
        } finally {
            els.btnPdf.disabled = false;
        }
    }

    els.btnPreview.addEventListener("click", generate);
    els.btnPdf.addEventListener("click", downloadPdf);
    els.btnSample.addEventListener("click", () => {
        els.input.value = ANSWER_KEY_SAMPLE;
        updateCharCount(els.input, els.charCount);
        setStatus(els.status, 'Exemplo carregado. Clique em "Gerar pré-visualização".');
    });
    els.input.addEventListener("input", () => updateCharCount(els.input, els.charCount));
    els.theme.addEventListener("change", () => {
        if (!els.btnPdf.disabled) {
            generate();
        }
    });
    updateCharCount(els.input, els.charCount);
}

function setupTabs() {
    const tabs = [
        {
            button: document.getElementById("tab-slides"),
            view: document.getElementById("view-slides"),
        },
        {
            button: document.getElementById("tab-answer-key"),
            view: document.getElementById("view-answer-key"),
        },
    ];

    function activate(target) {
        tabs.forEach(({ button, view }) => {
            const isActive = button === target;
            button.classList.toggle("tab--active", isActive);
            button.setAttribute("aria-selected", isActive ? "true" : "false");
            view.classList.toggle("view--active", isActive);
        });
    }

    tabs.forEach(({ button }) => {
        button.addEventListener("click", () => activate(button));
    });
}

setupTabs();
setupSlides();
setupAnswerKey();
