document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.btn-votar').forEach(botao => {
        botao.addEventListener('click', () => {
            const respostaId = botao.dataset.id;
            const valor      = botao.dataset.valor;

            // URL corrigida para bater com a rota do Flask
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
});