from flask import Flask
from extensoes import banco
from modelos import entidades  # Importado para o SQLAlchemy reconhecer as tabelas
from controles.rotas_perguntas import blueprint_perguntas

def criar_app() -> Flask:
    app = Flask(__name__)
    
    # Configuração do banco de dados (SQLite local)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///monitoria.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializando as extensões
    banco.init_app(app)

    # Registrando as rotas (Blueprints)
    app.register_blueprint(blueprint_perguntas)

    # Criação automática das tabelas (ideal para o ambiente de desenvolvimento)
    with app.app_context():
        banco.create_all()

    return app

if __name__ == '__main__':
    aplicacao = criar_app()
    aplicacao.run(debug=True, port=5000)