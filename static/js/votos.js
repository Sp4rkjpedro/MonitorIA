document.addEventListener('DOMContentLoaded', () => {

    // --- VOTOS ---
    document.querySelectorAll('.btn-votar').forEach(botao => {
        botao.addEventListener('click', () => {
            const respostaId = botao.dataset.id;
            const valor      = botao.dataset.valor;

            fetch(`/respostas/${respostaId}/votar/${valor}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.sucesso) {
                    document.getElementById(`likes-${respostaId}`).textContent    = data.total_likes;
                    document.getElementById(`dislikes-${respostaId}`).textContent = data.total_dislikes;
                } else {
                    alert(data.mensagem || 'Erro ao votar!');
                }
            })
            .catch(error => {
                console.error('Erro:', error);
            });
        });
    });

    // --- EFEITO DIGITAÇÃO (IA) ---
    const blocoIA = document.querySelector('.texto-formatado');
    if (blocoIA) {
        const textoOriginal = blocoIA.textContent.trim();
        const perguntaId = blocoIA.dataset.perguntaId;
        const chave = 'ia_' + perguntaId;

        if (localStorage.getItem(chave)) {
            // já foi digitado antes, mostra direto sem atraso
            blocoIA.textContent = textoOriginal;
        } else {
            // primeira vez, digita
            blocoIA.textContent = '';
            let i = 0;
            const timer = setInterval(() => {
                blocoIA.textContent += textoOriginal.charAt(i);
                i++;
                if (i >= textoOriginal.length) {
                    clearInterval(timer);
                    localStorage.setItem(chave, '1');
                }
            }, 8);
        }
    }

});