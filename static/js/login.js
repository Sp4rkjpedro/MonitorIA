// Fora do DOMContentLoaded para ficar acessível ao onclick do HTML
function alternarSenhaLogin(botao) {
    const campo = document.getElementById('senha');
    const visivel = campo.type === 'password';

    campo.type = visivel ? 'text' : 'password';

    const olhoAberto = `
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
            <circle cx="12" cy="12" r="3"/>
        </svg>`;

    const olhoFechado = `
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>
            <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
            <line x1="1" y1="1" x2="23" y2="23"/>
        </svg>`;

    botao.innerHTML = visivel ? olhoFechado : olhoAberto;
}

document.addEventListener('DOMContentLoaded', () => {
    const campoEmail = document.getElementById('email');

    // Restaura o email salvo
    const emailSalvo = localStorage.getItem('login_email');
    if (emailSalvo) {
        campoEmail.value = emailSalvo;
    }

    // Salva o email enquanto digita
    campoEmail.addEventListener('input', () => {
        localStorage.setItem('login_email', campoEmail.value);
    });
});