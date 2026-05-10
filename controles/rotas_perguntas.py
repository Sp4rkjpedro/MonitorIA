from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from servicos.servico_pergunta import ServicoPergunta
from repositorios.repositorio_pergunta import RepositorioPergunta
from servicos.servico_ia import ServicoIA
from repositorios.repositorio_resposta import RepositorioResposta

# Inicialização do Blueprint e dos Serviços
blueprint_perguntas = Blueprint('perguntas', __name__)

repo_pergunta = RepositorioPergunta()
repo_resposta = RepositorioResposta()

servico = ServicoPergunta(repo_pergunta)
servico_ia = ServicoIA(repo_resposta)

@blueprint_perguntas.route('/')
def base():
    """Lista todas as perguntas na home."""
    return render_template('home.html', 
                           perguntas=servico.listar_todas(), 
                           disciplinas=servico.listar_disciplinas())

@blueprint_perguntas.route('/perguntas/nova', methods=['GET', 'POST'])
def fazer_pergunta():
    """Cria nova pergunta com validação de duplicatas via IA."""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        
        # DEBUG NO TERMINAL PARA A APRESENTAÇÃO
        print("\n" + "="*40)
        print(f"SISTEMA IA: ANALISANDO DUPLICATA")
        print(f"TITULO ENVIADO: {titulo}")
        
        todas = servico.listar_todas()
        duplicatas = servico_ia.buscar_duplicatas(titulo, todas)
        
        print(f"RESULTADO DA IA: {duplicatas}")
        print("="*40 + "\n")

        if duplicatas:
            flash(f"Pergunta similar encontrada no ID {duplicatas[0].id}", "perigo")
            return render_template('fazer_pergunta.html', 
                                 erro="Duplicata", 
                                 duplicata=duplicatas[0], 
                                 disciplinas=servico.listar_disciplinas())

        dados = {
            'titulo': titulo,
            'corpo': request.form.get('corpo', '').strip(),
            'disciplina': request.form.get('disciplina', '').strip(),
            'usuario_id': session.get('usuario_id')
        }
        pergunta = servico.criar_pergunta(dados)
        return redirect(url_for('perguntas.ver_pergunta', id=pergunta.id))
    
    return render_template('fazer_pergunta.html', disciplinas=servico.listar_disciplinas())

@blueprint_perguntas.route('/perguntas/<int:id>')
def ver_pergunta(id):
    """Exibe os detalhes de uma pergunta e suas respostas."""
    return render_template('ver_pergunta.html', 
                           pergunta=servico.buscar_detalhes(id), 
                           disciplinas=servico.listar_disciplinas())

@blueprint_perguntas.route('/minhas-perguntas')
def minhas_perguntas():
    """Filtra perguntas apenas do usuário logado."""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    usuario_id_atual = session.get('usuario_id')
    todas = servico.listar_todas()
    minhas = [p for p in todas if p.usuario_id == usuario_id_atual]
    
    return render_template('minhas_perguntas.html', 
                           perguntas=minhas, 
                           disciplinas=servico.listar_disciplinas())

@blueprint_perguntas.route('/debug/analisar/<int:id>')
def debug_ia_respostas(id):
    p = servico.buscar_detalhes(id)
    # Chama a sua lógica de juíza
    melhor_id = servico_ia.analisar_melhor_resposta(p, p.respostas)
    
    if melhor_id:
        return f"A IA analisou {len(p.respostas)} respostas e indica que a melhor é o ID: {melhor_id}"
    return "A IA não encontrou uma resposta satisfatória ou não há respostas."