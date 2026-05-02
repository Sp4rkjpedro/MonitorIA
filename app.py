import os
from dotenv import load_dotenv
load_dotenv() # ESSA LINHA É OBRIGATÓRIA

from flask import Flask, render_template, request, redirect, url_for
from extensoes import banco
from modelos.entidades import Usuario
from controles.rotas_perguntas import blueprint_perguntas
from servicos.servico_pergunta import ServicoPergunta
from repositorios.repositorio_pergunta import RepositorioPergunta
from servicos.servico_ia import ServicoIA
from repositorios.repositorio_resposta import RepositorioResposta

def criar_app() -> Flask:
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///monitoria.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    banco.init_app(app)
    app.register_blueprint(blueprint_perguntas)

    servico = ServicoPergunta(RepositorioPergunta())
    servico_ia = ServicoIA(RepositorioResposta())

    @app.route('/')
    def base():
        return render_template('base.html', perguntas=servico.listar_todas(), disciplinas=servico.listar_disciplinas())

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
                pergunta = servico.criar_pergunta(dados)
                servico_ia.gerar_resposta_monitor(pergunta)
                return redirect(url_for('ver_pergunta', id=pergunta.id))
            except ValueError as error:
                return render_template('fazer_pergunta.html', disciplinas=disciplinas, erro=str(error), form=dados)
        return render_template('fazer_pergunta.html', disciplinas=disciplinas)

    @app.route('/perguntas/<int:id>')
    def ver_pergunta(id):
        try:
            return render_template('ver_pergunta.html', pergunta=servico.buscar_detalhes(id), disciplinas=servico.listar_disciplinas())
        except ValueError:
            return "Não encontrado", 404

    with app.app_context():
        banco.create_all()
        if not Usuario.query.first():
            banco.session.add(Usuario(nome='Admin', email='admin@monitoria.local', papel='aluno'))
            banco.session.commit()

    return app

if __name__ == '__main__':
    criar_app().run(debug=True, port=5000)