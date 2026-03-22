(function () {
    const campoBusca = document.getElementById("campo-busca");
    const container = document.getElementById("noticias-container");
    const tituloPagina = document.getElementById("titulo-pagina");
    const buscaForm = document.getElementById("busca-form");

    if (!campoBusca || !container || !buscaForm) return;

    let debounceTimer = null;

    function atualizarUrl(termo) {
        const url = new URL(window.location);
        if (termo) {
            url.searchParams.set("q", termo);
            url.searchParams.delete("pagina");
        } else {
            url.searchParams.delete("q");
            url.searchParams.delete("pagina");
        }
        window.history.replaceState({}, "", url);
    }

    function atualizarTitulo(termo) {
        if (!tituloPagina) return;
        if (termo) {
            tituloPagina.textContent = 'grep -ri "' + termo + '" /noticias/';
        } else {
            tituloPagina.textContent = "ls -lt /noticias/";
        }
    }

    async function buscar(termo) {
        try {
            const url = termo
                ? "/api/busca?q=" + encodeURIComponent(termo)
                : "/";
            const resposta = await fetch(url);
            if (!resposta.ok) return;

            if (termo) {
                const html = await resposta.text();
                container.innerHTML = html;
            } else {
                const html = await resposta.text();
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, "text/html");
                const novoContainer = doc.getElementById("noticias-container");
                if (novoContainer) {
                    container.innerHTML = novoContainer.innerHTML;
                }
            }

            atualizarUrl(termo);
            atualizarTitulo(termo);
        } catch (e) {
            console.error("Erro na busca:", e);
        }
    }

    campoBusca.addEventListener("input", function () {
        clearTimeout(debounceTimer);
        const termo = this.value.trim();
        debounceTimer = setTimeout(function () {
            buscar(termo);
        }, 300);
    });

    buscaForm.addEventListener("submit", function (e) {
        e.preventDefault();
        clearTimeout(debounceTimer);
        buscar(campoBusca.value.trim());
    });
})();
