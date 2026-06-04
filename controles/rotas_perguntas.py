from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from servicos.servico_pergunta import ServicoPergunta
from repositorios.repositorio_pergunta import RepositorioPergunta
from servicos.servico_ia import ServicoIA
from repositorios.repositorio_resposta import RepositorioResposta
from modelos.entidades import Resposta
from extensoes import banco

blueprint_perguntas = Blueprint('perguntas', __name__)

repo_pergunta = RepositorioPergunta()
repo_resposta = RepositorioResposta()

servico = ServicoPergunta(repo_pergunta)
servico_ia = ServicoIA(repo_resposta)

@blueprint_perguntas.route('/')
def base():
    """Home do sistema."""
    disciplina_filtro = request.args.get('disciplina', '').strip()
    
    todas = servico.listar_todas()
    
    if disciplina_filtro:
        perguntas = [p for p in todas if p.disciplina == disciplina_filtro]
    else:
        perguntas = todas

    return render_template('home.html', 
                           perguntas=perguntas,
                           disciplina_ativa=disciplina_filtro,
                           disciplinas=servico.listar_disciplinas())

@blueprint_perguntas.route('/perguntas/checar-duplicatas', methods=['POST'])
def checar_duplicatas():
    """IA-001: Rota AJAX chamada pelo frontend enquanto o aluno digita."""
    dados = request.get_json()
    titulo_parcial = dados.get('titulo', '').strip()
    corpo_parcial = dados.get('corpo', '').strip() # 💡 Captura se já houver algo digitado no corpo
    disciplina_parcial = dados.get('disciplina', '').strip() # 💡 Captura a disciplina selecionada
    
    if len(titulo_parcial) < 8:
        return jsonify([])

    todas = servico.listar_todas()
    
    # 🚀 ATUALIZADO: Passando os novos parâmetros para a checagem dinâmica em tempo real
    duplicatas = servico_ia.buscar_duplicatas(titulo_parcial, corpo_parcial, disciplina_parcial, todas)
    
    resultado = [{"id": p.id, "titulo": p.titulo} for p in duplicatas]
    return jsonify(resultado)

@blueprint_perguntas.route('/perguntas/nova', methods=['GET', 'POST'])
def fazer_pergunta():
    """Cria a pergunta e dispara o Monitor Virtual (IA-002)."""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        corpo = request.form.get('corpo', '').strip()
        disciplina = request.form.get('disciplina', '').strip()

        print("\n" + "="*50)
        print(f"[REQUISIÇÃO POST] Recebendo dados do formulário do Felipe:")
        print(f"- Título: '{titulo}'")
        print(f"- Corpo: '{corpo}'")
        print(f"- Disciplina: '{disciplina}'")
        print("="*50 + "\n")

        if not titulo or not corpo:
            flash("Por favor, preencha todos os campos obrigatórios.", "aviso")
            return render_template('fazer_pergunta.html', disciplinas=servico.listar_disciplinas())

        texto_completo = f"{titulo} {corpo}"

        # 1. IA-003: Guardrail de Conteúdo (Agora mais restrito contra deboche/ironia)
        if not servico_ia.verificar_conteudo_adequado(texto_completo):
            flash("Sua publicação contém termos inadequados para o ambiente acadêmico.", "perigo")
            return render_template('fazer_pergunta.html', disciplinas=servico.listar_disciplinas())

        # 2. IA-004: Filtro de Coerência Pedagógica
        if not servico_ia.verificar_coerencia_pedagogica(titulo, corpo):
            flash("Sua pergunta parece não ter nexo pedagógico ou está incompleta.", "aviso")
            return render_template('fazer_pergunta.html', disciplinas=servico.listar_disciplinas())

        # 3. IA-001: Trava final de duplicata no servidor
        todas = servico.listar_todas()
        
        # 🚀 ATUALIZADO: Passando título, corpo e disciplina para evitar falsos positivos de outras matérias
        if servico_ia.buscar_duplicatas(titulo, corpo, disciplina, todas):
            flash("Pergunta muito similar nesta mesma disciplina já existe!", "perigo")
            return redirect(url_for('perguntas.fazer_pergunta'))

        dados = {
            'titulo': titulo,
            'corpo': corpo,
            'disciplina': disciplina,
            'usuario_id': session.get('usuario_id')
        }
        
        pergunta = servico.criar_pergunta(dados)

        # 4. IA-002: Monitor Virtual gera e salva a sugestão imediatamente
        try:
            sugestao = servico_ia.gerar_sugestao_monitoria(pergunta)
            if sugestao:
                resposta_ia = Resposta(
                    corpo=sugestao,
                    pergunta_id=pergunta.id,
                    usuario_id=None,
                    eh_ia=True,
                    solucao=False
                )
                banco.session.add(resposta_ia)
                banco.session.commit()
        except Exception as e:
            print(f"Erro ao processar Monitor Virtual: {e}")

        return redirect(url_for('perguntas.ver_pergunta', id=pergunta.id))
    
    return render_template('fazer_pergunta.html', disciplinas=servico.listar_disciplinas())

@blueprint_perguntas.route('/perguntas/<int:id>')
def ver_pergunta(id):
    """Exibe detalhes. O HTML deve tratar o visual de 'eh_ia'."""
    return render_template('ver_pergunta.html', 
                           pergunta=servico.buscar_detalhes(id), 
                           disciplinas=servico.listar_disciplinas())

@blueprint_perguntas.route('/minhas-perguntas')
def minhas_perguntas():
    usuario_id_atual = session.get('usuario_id')
    minhas = [p for p in servico.listar_todas() if p.usuario_id == usuario_id_atual]
    return render_template('minhas_perguntas.html', perguntas=minhas, disciplinas=servico.listar_disciplinas())

@blueprint_perguntas.route('/debug/analisar/<int:id>')
def debug_ia_respostas(id):
    p = servico.buscar_detalhes(id)
    melhor_id = servico_ia.analisar_melhor_resposta(p, p.respostas)
    return f"Sugestão de melhor resposta (ID): {melhor_id}" if melhor_id else "Nenhuma resposta ideal encontrada."

@blueprint_perguntas.route('/modo-monitor')
def modo_monitor():
    if session.get('usuario_papel') != 'monitor':
        flash("Acesso negado.", "erro")
        return redirect(url_for('perguntas.base'))
    
    todas = servico.listar_todas()
    return render_template('Modo_Monitor.html',
                           perguntas=todas,
                           disciplina_ativa=None,
                           disciplinas=servico.listar_disciplinas())