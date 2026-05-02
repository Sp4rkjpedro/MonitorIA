from flask import Flask, render_template, request, redirect, url_for
from extensoes import banco
from modelos import entidades
from modelos.entidades import Usuario
from controles.rotas_perguntas import blueprint_perguntas

# Importações para a lógica das páginas
from servicos.servico_pergunta import ServicoPergunta
from repositorios.repositorio_pergunta import RepositorioPergunta

# [JOÃO PEDRO - AI ENGINEER] Serviços de IA Ativados
from servicos.servico_ia import ServicoIA
from repositorios.repositorio_resposta import RepositorioResposta

def criar_app() -> Flask:
    app = Flask(__name__)
    
    # 1. Configurações
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///monitoria.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 2. Inicialização do Banco
    banco.init_app(app)

    # 3. Registro de Blueprints (APIs JSON)
    app.register_blueprint(blueprint_perguntas)

    # 4. Instanciando serviços
    repositorio = RepositorioPergunta()
    servico = ServicoPergunta(repositorio)
    
    # [JOÃO PEDRO - AI ENGINEER] 
    # Instanciamos o repositório de respostas e o serviço de IA
    repo_res = RepositorioResposta()
    servico_ia = ServicoIA(repo_res)

    # 5. Rotas de Renderização de Páginas (Frontend)
    @app.route('/')
    def base():
        perguntas = servico.listar_todas()
        disciplinas = servico.listar_disciplinas()
        return render_template('base.html', perguntas=perguntas, disciplinas=disciplinas)

    @app.route('/perguntas/nova', methods=['GET', 'POST'])
    def fazer_pergunta():
        disciplinas = servico.listar_disciplinas()

        if request.method == 'POST':
            dados = {
                'titulo': request.form.get('titulo', '').strip(),
                'corpo': request.form.get('corpo', '').strip(),
                'disciplina': request.form.get('disciplina', '').strip(),
                'usuario_id': 1
            }

            try:
                # 1. Cria a pergunta no banco
                pergunta = servico.criar_pergunta(dados)
                
                # 2. [JOÃO PEDRO] A IA gera a resposta IMEDIATAMENTE
                # O Llama 3.1 8B é perfeito aqui pela velocidade.
                servico_ia.gerar_resposta_monitor(pergunta)
                
                return redirect(url_for('ver_pergunta', id=pergunta.id))
            except ValueError as error:
                return render_template('fazer_pergunta.html', disciplinas=disciplinas, erro=str(error), form=dados)

        return render_template('fazer_pergunta.html', disciplinas=disciplinas)

    @app.route('/perguntas/<int:id>', methods=['GET'])
    def ver_pergunta(id):
        try:
            pergunta = servico.buscar_detalhes(id)
            disciplinas = servico.listar_disciplinas()
            return render_template('ver_pergunta.html', pergunta=pergunta, disciplinas=disciplinas)
        except ValueError:
            return "Pergunta não encontrada", 404

    # 6. Criação das tabelas e Usuário Padrão
    with app.app_context():
        banco.create_all()
        if not Usuario.query.first():
            usuario_padrao = Usuario(
                nome='João Pedro (AI Engineer)',
                email='joao@monitoria.local',
                papel='aluno'
            )
            banco.session.add(usuario_padrao)
            banco.session.commit()

    return app

if __name__ == '__main__':
    aplicacao = criar_app()
    aplicacao.run(debug=True, port=5000)