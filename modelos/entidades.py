from extensoes import banco
from datetime import datetime

class Usuario(banco.Model):
    __tablename__ = 'usuarios'
    
    id = banco.Column(banco.Integer, primary_key=True)
    nome = banco.Column(banco.String(100), nullable=False)
    email = banco.Column(banco.String(100), unique=True, nullable=False)
    senha_hash = banco.Column(banco.String(256), nullable=False) # Novo campo
    papel = banco.Column(banco.String(20), nullable=False) # 'aluno' ou 'monitor'

class Pergunta(banco.Model):
    __tablename__ = 'perguntas'
    
    id = banco.Column(banco.Integer, primary_key=True)
    titulo = banco.Column(banco.String(200), nullable=False)
    corpo = banco.Column(banco.Text, nullable=False)
    disciplina = banco.Column(banco.String(100), nullable=False)
    usuario_id = banco.Column(banco.Integer, banco.ForeignKey('usuarios.id'), nullable=False)
    data_criacao = banco.Column(banco.DateTime, default=datetime.utcnow)
    
    # Relacionamento: uma pergunta tem várias respostas
    respostas = banco.relationship('Resposta', backref='pergunta', lazy=True)

class Resposta(banco.Model):
    __tablename__ = 'respostas'
    
    id = banco.Column(banco.Integer, primary_key=True)
    corpo = banco.Column(banco.Text, nullable=False)
    pergunta_id = banco.Column(banco.Integer, banco.ForeignKey('perguntas.id'), nullable=False)
    usuario_id = banco.Column(banco.Integer, banco.ForeignKey('usuarios.id'), nullable=True) # Nulo se for a IA
    eh_ia = banco.Column(banco.Boolean, default=False)
    solucao = banco.Column(banco.Boolean, default=False)
    data_criacao = banco.Column(banco.DateTime, default=datetime.utcnow)