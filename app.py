import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

from flask import Flask
from extensoes import banco
from controles.rotas_perguntas import blueprint_perguntas
from controles.rotas_autenticacao import blueprint_auth
from controles.rotas_respostas import blueprint_respostas

def criar_app() -> Flask:
    app = Flask(__name__)
    
    # Configurações do Banco de Dados e Segurança
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///monitoria.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    # Inicialização das extensões
    banco.init_app(app)

    # Registro das Rotas (Blueprints)
    app.register_blueprint(blueprint_perguntas)
    app.register_blueprint(blueprint_respostas)
    app.register_blueprint(blueprint_auth)

    # Contexto do App para criar tabelas e dados iniciais
    with app.app_context():
        from modelos.entidades import Usuario, Pergunta, Resposta
        from werkzeug.security import generate_password_hash
        
        banco.create_all()
        
        if not Usuario.query.first():
            admin = Usuario(
                nome='Admin', 
                email='admin@monitoria.local', 
                senha_hash=generate_password_hash('admin123'),
                papel='monitor'
            )
            banco.session.add(admin)
            banco.session.commit()

    return app

if __name__ == '__main__':
    criar_app().run(debug=True, port=5000)