from flask import Blueprint, request, jsonify
from servicos.servico_pergunta import ServicoPergunta
from repositorios.repositorio_pergunta import RepositorioPergunta

blueprint_perguntas = Blueprint('perguntas', __name__)

# Instanciando as dependências (Em um projeto maior, usaríamos um container de DI)
repositorio_pergunta = RepositorioPergunta()
servico_pergunta = ServicoPergunta(repositorio_pergunta)

@blueprint_perguntas.route('/api/perguntas', methods=['POST'])
def criar_pergunta():
    try:
        dados = request.get_json()
        pergunta = servico_pergunta.criar_pergunta(dados)
        
        return jsonify({
            "mensagem": "Pergunta cadastrada com sucesso!",
            "id": pergunta.id
        }), 201
        
    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 400
    except Exception as erro:
        return jsonify({"erro": "Erro interno do servidor."}), 500

@blueprint_perguntas.route('/api/perguntas', methods=['GET'])
def listar_perguntas():
    try:
        perguntas = servico_pergunta.listar_todas()
        resultado = [
            {
                "id": p.id,
                "titulo": p.titulo,
                "disciplina": p.disciplina,
                "data_criacao": p.data_criacao.isoformat()
            } for p in perguntas
        ]
        return jsonify(resultado), 200
    except Exception as erro:
        return jsonify({"erro": "Erro interno do servidor."}), 500