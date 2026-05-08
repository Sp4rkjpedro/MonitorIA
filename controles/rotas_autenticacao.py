from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from modelos.entidades import Pergunta, Resposta
from servicos.servico_autenticacao import ServicoAutenticacao
from repositorios.repositorio_usuario import RepositorioUsuario

blueprint_auth = Blueprint('auth', __name__)
servico_auth = ServicoAutenticacao(RepositorioUsuario())

# Decorator para proteger rotas (Middlewares)
def login_obrigatorio(f):
    @wraps(f)
    def rota_protegida(*args, **kwargs):
        if 'usuario_id' not in session:
            flash("Acesso negado. Por favor, faça login.", "alerta")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return rota_protegida

@blueprint_auth.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        papel = request.form.get('papel')

        try:
            servico_auth.registrar_usuario(nome, email, senha, papel)
            flash("Cadastro realizado com sucesso! Faça seu login.", "sucesso")
            return redirect(url_for('auth.login'))
        except ValueError as erro:
            flash(str(erro), "erro")
            
    return render_template('cadastro.html')

@blueprint_auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        try:
            usuario = servico_auth.autenticar_usuario(email, senha)
            
            # Criando a sessão do usuário
            session['usuario_id'] = usuario.id
            session['usuario_nome'] = usuario.nome
            session['usuario_papel'] = usuario.papel
            
            return redirect(url_for('auth.dashboard'))
        except ValueError as erro:
            flash(str(erro), "erro")
            
    return render_template('login.html')

@blueprint_auth.route('/logout')
def logout():
    session.clear() # Limpa todos os dados da sessão
    flash("Você saiu da conta com sucesso.", "sucesso")
    return redirect(url_for('auth.login'))

@blueprint_auth.route('/dashboard')
@login_obrigatorio
def dashboard():
    # Passamos os dados da sessão para o template saber quem está logado
    perguntas_pendentes = Pergunta.query.filter(~Pergunta.respostas.any(Resposta.solucao == True)).count()
    return render_template('dashboard.html', 
                           nome=session.get('usuario_nome'), 
                           papel=session.get('usuario_papel'),
                           contagem_pendentes=perguntas_pendentes)