from flask import Blueprint, request, redirect, url_for, session, flash, jsonify
from modelos.entidades import Resposta, Voto
from extensoes import banco

# 🚨 NOVOS IMPORTS: Adicionando o serviço de IA para o Guardrail funcionar aqui
from servicos.servico_ia import ServicoIA
from repositorios.repositorio_resposta import RepositorioResposta

blueprint_respostas = Blueprint('respostas', __name__)

# Instanciando o repositório e o serviço de IA na inicialização da rota
repo_resposta = RepositorioResposta()
servico_ia = ServicoIA(repo_resposta)

@blueprint_respostas.route('/perguntas/<int:pergunta_id>/responder', methods=['POST'])
def criar(pergunta_id):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # 1. Pegamos o texto limpo digitado pelo usuário
    corpo_texto = request.form.get('corpo', '').strip()

    # 2. Verificação básica se o campo não foi enviado vazio
    if not corpo_texto:
        flash("A resposta não pode estar vazia.", "aviso")
        return redirect(url_for('perguntas.ver_pergunta', id=pergunta_id))

    # 3. 🛡️ GUARDRAIL DA IA: Analisa se a resposta humana contém grosserias/xingamentos
    if not servico_ia.verificar_conteudo_adequado(corpo_texto):
        flash("Sua resposta contém termos inadequados para o ambiente acadêmico.", "perigo")
        return redirect(url_for('perguntas.ver_pergunta', id=pergunta_id))

    # 4. Se passou pela IA sem problemas, o banco cria e salva o registro normalmente
    nova_resposta = Resposta(
        corpo=corpo_texto,
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
    papel_logado = session.get('usuario_papel') 

    if resposta.eh_ia:
        flash("Sugestões da IA não podem ser marcadas como solução.", "erro")
        return redirect(request.referrer)

    eh_monitor = (papel_logado == 'monitor')
    eh_autor = (pergunta.usuario_id == usuario_logado_id)

    if not (eh_monitor or eh_autor):
        flash("Apenas o autor da pergunta ou um monitor podem validar a resposta.", "erro")
        return redirect(request.referrer)

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

    if eh_ajax:
        return jsonify({
            'sucesso'       : True,
            'total_likes'   : total_likes,
            'total_dislikes': total_dislikes
        })

    return redirect(request.referrer)