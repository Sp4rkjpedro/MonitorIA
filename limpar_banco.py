# Este script é utilizado APENAS para limpar os dados do banco de dados sem deletar as tabelas.
from app import criar_app
from extensoes import banco
from modelos.entidades import Usuario, Pergunta, Resposta, Voto

app = criar_app()

with app.app_context():
    # 1. Apaga os dados respeitando a hierarquia das chaves estrangeiras
    Voto.query.delete()
    Resposta.query.delete()
    Pergunta.query.delete()
    Usuario.query.delete()
    
    # 2. Salva as alterações
    banco.session.commit()
    print("Todos os dados foram apagados sem deletar as tabelas!")