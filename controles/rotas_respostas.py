from flask import Blueprint, request, redirect, url_for, session, flash
from modelos.entidades import Resposta
from extensoes import banco

blueprint_respostas = Blueprint('respostas', __name__)

@blueprint_respostas.route('/perguntas/<int:pergunta_id>/responder', methods=['POST'])
def criar(pergunta_id):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    nova_resposta = Resposta(
        corpo=request.form.get('corpo', '').strip(),
        pergunta_id=pergunta_id,
        usuario_id=session.get('usuario_id'),
        eh_ia=False,
        solucao=False
    )
    
    banco.session.add(nova_resposta)
    banco.session.commit()
    return redirect(url_for('perguntas.ver_pergunta', id=pergunta_id))

@blueprint_respostas.route('/respostas/<int:id>/solucao', methods=['POST'])
def definir_solucao(id):
    if session.get('papel') != 'monitor':
        return redirect(request.referrer)

    resposta = Resposta.query.get_or_404(id)
    Resposta.query.filter_by(pergunta_id=resposta.pergunta_id).update({"solucao": False})
    resposta.solucao = True
    banco.session.commit()
    return redirect(url_for('perguntas.ver_pergunta', id=resposta.pergunta_id))