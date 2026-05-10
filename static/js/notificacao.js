document.addEventListener('DOMContentLoaded', () => {
    const notificacoes = document.querySelectorAll('.notificacao');

    notificacoes.forEach(notificacao => {
        setTimeout(() => {
            notificacao.classList.remove('visivel');
        }, 3000);
    });
});