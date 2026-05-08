import threading
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session, flash
from servicos.servico_pergunta import ServicoPergunta
from repositorios.repositorio_pergunta import RepositorioPergunta
from servicos.servico_ia import ServicoIA
from repositorios.repositorio_resposta import RepositorioResposta

# Criação do Blueprint
blueprint_perguntas = Blueprint('perguntas', __name__)

# Instanciando os serviços que esta controladora vai usar
servico = ServicoPergunta(RepositorioPergunta())
servico_ia = ServicoIA(RepositorioResposta())

@blueprint_perguntas.route('/')
def base():
    """Página inicial com lista de perguntas."""
    lista_de_perguntas = servico.listar_todas()
    return render_template('home.html', 
                           perguntas=lista_de_perguntas, 
                           disciplinas=servico.listar_disciplinas())

@blueprint_perguntas.route('/perguntas/nova', methods=['GET', 'POST'])
def fazer_pergunta():
    """Criação de nova pergunta com IA em segundo plano."""
    if 'usuario_id' not in session:
        flash("Você precisa estar logado para fazer uma pergunta.", "alerta")
        return redirect(url_for('auth.login'))

    disciplinas = servico.listar_disciplinas()
    
    if request.method == 'POST':
        dados = {
            'titulo': request.form.get('titulo', '').strip(),
            'corpo': request.form.get('corpo', '').strip(),
            'disciplina': request.form.get('disciplina', '').strip(),
            'usuario_id': session.get('usuario_id') # Usando o usuário real da sessão
        }
        try:
            pergunta = servico.criar_pergunta(dados)
            
            # IA em background
            threading.Thread(target=servico_ia.gerar_resposta_monitor, args=(pergunta,)).start()
            
            return redirect(url_for('perguntas.ver_pergunta', id=pergunta.id))
        except ValueError as error:
            return render_template('fazer_pergunta.html', disciplinas=disciplinas, erro=str(error), form=dados)
    
    return render_template('fazer_pergunta.html', disciplinas=disciplinas)

@blueprint_perguntas.route('/perguntas/<int:id>')
def ver_pergunta(id):
    """Visualização de detalhes de uma pergunta específica."""
    try:
        return render_template('ver_pergunta.html', 
                               pergunta=servico.buscar_detalhes(id), 
                               disciplinas=servico.listar_disciplinas())
    except ValueError:
        return "Pergunta não encontrada", 404

@blueprint_perguntas.route('/minhas-perguntas')
def minhas_perguntas():
    """Lista as perguntas do usuário logado."""
    if 'usuario_id' not in session:
        flash("Faça login para ver suas perguntas.", "alerta")
        return redirect(url_for('auth.login'))

    usuario_id_atual = session.get('usuario_id')
    todas = servico.listar_todas()
    minhas = [p for p in todas if p.usuario_id == usuario_id_atual]
    
    return render_template('minhas_perguntas.html', perguntas=minhas, disciplinas=servico.listar_disciplinas())

@blueprint_perguntas.route('/api/checar-duplicatas', methods=['POST'])
def api_duplicatas():
    """Endpoint para busca de duplicatas via IA"""
    dados = request.get_json()
    titulo = dados.get('titulo', '')
    todas_perguntas = servico.listar_todas()
    
    duplicatas = servico_ia.buscar_duplicatas(titulo, todas_perguntas)
    resultado = [{"id": p.id, "titulo": p.titulo} for p in duplicatas]
    return jsonify({"duplicatas": resultado})

@blueprint_perguntas.route('/respostas/<int:id>/solucao', methods=['POST'])
def marcar_solucao(id):
    """Marca uma resposta como a solução da dúvida"""
    if session.get('usuario_papel') != 'monitor':
        flash("Apenas monitores podem marcar a melhor resposta.", "erro")
        return redirect(request.referrer)

    from modelos.entidades import Resposta
    from extensoes import banco
    
    resposta = Resposta.query.get_or_404(id)
    Resposta.query.filter_by(pergunta_id=resposta.pergunta_id).update({"solucao": False})
    
    resposta.solucao = True
    banco.session.commit()

    flash("Resposta validada como Solução Correta!", "sucesso")
    return redirect(url_for('perguntas.ver_pergunta', id=resposta.pergunta_id))