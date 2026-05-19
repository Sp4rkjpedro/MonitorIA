// --- PERSISTÊNCIA DOS CAMPOS ---
const campos = ['titulo', 'corpo'];
const selects = ['disciplina'];

// Restaura campos de texto
campos.forEach(id => {
    const el = document.getElementById(id);
    const salvo = localStorage.getItem('form_' + id);
    if (el && salvo) el.value = salvo;
});

// Restaura select
selects.forEach(id => {
    const el = document.getElementById(id);
    const salvo = localStorage.getItem('form_' + id);
    if (el && salvo) el.value = salvo;
});

// Salva campos de texto
campos.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
        el.addEventListener('input', () => {
            localStorage.setItem('form_' + id, el.value);
        });
    }
});

// Salva select
selects.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
        el.addEventListener('change', () => {
            localStorage.setItem('form_' + id, el.value);
        });
    }
});

// Limpa ao enviar
document.querySelector('.form-pergunta').addEventListener('submit', () => {
    [...campos, ...selects].forEach(id => localStorage.removeItem('form_' + id));
});