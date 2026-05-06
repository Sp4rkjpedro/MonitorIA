import os
import threading
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

from flask import Flask, render_template, request, redirect, url_for, jsonify
from extensoes import banco
from modelos.entidades import Usuario, Pergunta, Resposta
from controles.rotas_perguntas import blueprint_perguntas
from servicos.servico_pergunta import ServicoPergunta
from repositorios.repositorio_pergunta import RepositorioPergunta
from servicos.servico_ia import ServicoIA
from repositorios.repositorio_resposta import RepositorioResposta
from controles.rotas_autenticacao import blueprint_auth

def criar_app() -> Flask:
    app = Flask(__name__)
    
    # Configurações do Banco de Dados
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///monitoria.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    # Inicialização
    banco.init_app(app)
    app.register_blueprint(blueprint_perguntas)
    app.register_blueprint(blueprint_auth)

    # Instanciando Repositórios e Serviços
    repo_pergunta = RepositorioPergunta()
    repo_resposta = RepositorioResposta()
    servico = ServicoPergunta(repo_pergunta)
    servico_ia = ServicoIA(repo_resposta)

    # --- ROTAS PRINCIPAIS ---

    @app.route('/')
    def base():
        """Página inicial com lista de perguntas."""
        return render_template('base.html', 
                               perguntas=servico.listar_todas(), 
                               disciplinas=servico.listar_disciplinas())

    @app.route('/perguntas/nova', methods=['GET', 'POST'])
    def fazer_pergunta():
        """Criação de nova pergunta com IA em segundo plano (Threading)."""
        disciplinas = servico.listar_disciplinas()
        
        if request.method == 'POST':
            dados = {
                'titulo': request.form.get('titulo', '').strip(),
                'corpo': request.form.get('corpo', '').strip(),
                'disciplina': request.form.get('disciplina', '').strip(),
                'usuario_id': 1  # Usuário padrão para testes
            }
            try:
                # 1. Salva a pergunta no banco
                pergunta = servico.criar_pergunta(dados)
                
                # 2. Dispara a IA em background para não travar o carregamento da página
                threading.Thread(
                    target=servico_ia.gerar_resposta_monitor, 
                    args=(pergunta,)
                ).start()
                
                return redirect(url_for('ver_pergunta', id=pergunta.id))
            except ValueError as error:
                return render_template('fazer_pergunta.html', 
                                       disciplinas=disciplinas, 
                                       erro=str(error), 
                                       form=dados)
        
        return render_template('fazer_pergunta.html', disciplinas=disciplinas)

    @app.route('/perguntas/<int:id>')
    def ver_pergunta(id):
        """Visualização de detalhes de uma pergunta específica."""
        try:
            return render_template('ver_pergunta.html', 
                                   pergunta=servico.buscar_detalhes(id), 
                                   disciplinas=servico.listar_disciplinas())
        except ValueError:
            return "Pergunta não encontrada", 404

    @app.route('/minhas-perguntas')
    def minhas_perguntas():
        """Lista as perguntas do usuário logado."""
        usuario_id_atual = 1
        todas = servico.listar_todas()
        minhas = [p for p in todas if p.usuario_id == usuario_id_atual]
        return render_template('minhas_perguntas.html', 
                               perguntas=minhas, 
                               disciplinas=servico.listar_disciplinas())

    # --- ROTAS DE API E FUNCIONALIDADES (Tarefas do João e Felipe) ---

    @app.route('/api/checar-duplicatas', methods=['POST'])
    def api_duplicatas():
        """Endpoint para busca de duplicatas via IA (Tarefa do João)."""
        dados = request.get_json()
        titulo = dados.get('titulo', '')
        todas_perguntas = servico.listar_todas()
        
        duplicatas = servico_ia.buscar_duplicatas(titulo, todas_perguntas)
        
        resultado = [{"id": p.id, "titulo": p.titulo} for p in duplicatas]
        return jsonify({"duplicatas": resultado})

    @app.route('/respostas/<int:id>/solucao', methods=['POST'])
    def marcar_solucao(id):
        """Marca uma resposta como a solução da dúvida (Tarefa do Felipe)."""
        # A lógica será implementada no repositório/serviço pelo Felipe
        return redirect(request.referrer or url_for('base'))

    # Contexto do App para Banco de Dados
    with app.app_context():
        banco.create_all()
        if not Usuario.query.first():
            banco.session.add(Usuario(nome='Admin', email='admin@monitoria.local', papel='aluno', senha_hash='admin123'))
            banco.session.commit()

    return app

if __name__ == '__main__':
    # Rodar o servidor Flask
    criar_app().run(debug=True, port=5000)