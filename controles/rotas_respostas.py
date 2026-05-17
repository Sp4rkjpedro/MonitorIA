from flask import Blueprint, request, redirect, url_for, session, flash, jsonify
from modelos.entidades import Resposta, Voto
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
    return redirect(url_for('perguntas.ver_pergunta', id=pergunta_id) + f'#resposta-{nova_resposta.id}')

@blueprint_respostas.route('/respostas/<int:id>/solucao', methods=['POST'])
def definir_solucao(id):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    resposta = Resposta.query.get_or_404(id)
    pergunta = resposta.pergunta
    
    usuario_logado_id = session.get('usuario_id')
    # Nota: Ajuste 'usuario_papel' se no seu login você salva apenas como 'papel'
    papel_logado = session.get('usuario_papel') 

    # Regra 1: A IA não pode ser a solução oficial
    if resposta.eh_ia:
        flash("Sugestões da IA não podem ser marcadas como solução.", "erro")
        return redirect(request.referrer)

    # Regra 2: Apenas o monitor ou o autor da pergunta podem definir a solução
    eh_monitor = (papel_logado == 'monitor')
    eh_autor = (pergunta.usuario_id == usuario_logado_id)

    if not (eh_monitor or eh_autor):
        flash("Apenas o autor da pergunta ou um monitor podem validar a resposta.", "erro")
        return redirect(request.referrer)

    # Regra 3: Desmarca anterior e marca a nova
    Resposta.query.filter_by(pergunta_id=resposta.pergunta_id).update({"solucao": False})
    resposta.solucao = True
    banco.session.commit()
    
    flash("Solução validada com sucesso!", "sucesso")
    return redirect(url_for('perguntas.ver_pergunta', id=resposta.pergunta_id) + f'#resposta-{resposta.id}')

@blueprint_respostas.route('/respostas/<int:id>/votar/<int:valor>', methods=['POST'])
def votar_resposta(id, valor):
    eh_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    print(f">>> ROTA CHAMADA | id={id} valor={valor} | AJAX={eh_ajax}")

    if 'usuario_id' not in session:
        if eh_ajax:
            return jsonify({'sucesso': False, 'mensagem': 'Faça login para votar.'})
        flash("Faça login para votar.", "erro")
        return redirect(url_for('auth.login'))

    valor_voto = 1 if valor == 1 else -1
    usuario_id = session.get('usuario_id')
    resposta   = Resposta.query.get_or_404(id)

    if resposta.eh_ia:
        if eh_ajax:
            return jsonify({'sucesso': False, 'mensagem': 'Sugestões da IA não recebem votos.'})
        flash("Sugestões da IA não recebem votos.", "erro")
        return redirect(request.referrer)

    voto_existente = Voto.query.filter_by(usuario_id=usuario_id, resposta_id=id).first()

    if voto_existente:
        if voto_existente.valor == valor_voto:
            banco.session.delete(voto_existente)
        else:
            voto_existente.valor = valor_voto
    else:
        novo_voto = Voto(usuario_id=usuario_id, resposta_id=id, valor=valor_voto)
        banco.session.add(novo_voto)

    banco.session.commit()

    total_likes    = Voto.query.filter_by(resposta_id=id, valor=1).count()
    total_dislikes = Voto.query.filter_by(resposta_id=id, valor=-1).count()

    # Retorna JSON para AJAX, redirect para requisição normal
    if eh_ajax:
        return jsonify({
            'sucesso'       : True,
            'total_likes'   : total_likes,
            'total_dislikes': total_dislikes
        })

    return redirect(request.referrer)