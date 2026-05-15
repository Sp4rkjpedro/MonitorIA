from extensoes import banco
from datetime import datetime

class Usuario(banco.Model):
    __tablename__ = 'usuarios'
    
    id = banco.Column(banco.Integer, primary_key=True)
    nome = banco.Column(banco.String(100), nullable=False)
    email = banco.Column(banco.String(100), unique=True, nullable=False)
    senha_hash = banco.Column(banco.String(256), nullable=False)
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

class Voto(banco.Model):
    __tablename__ = 'votos'
    id = banco.Column(banco.Integer, primary_key=True)
    usuario_id = banco.Column(banco.Integer, banco.ForeignKey('usuarios.id'), nullable=False)
    resposta_id = banco.Column(banco.Integer, banco.ForeignKey('respostas.id'), nullable=False)
    valor = banco.Column(banco.Integer, nullable=False) # 1 para upvote, -1 para downvote

    # Garante que um usuário só vote uma vez por resposta
    __table_args__ = (banco.UniqueConstraint('usuario_id', 'resposta_id', name='unico_voto_usuario_resposta'),)

class Resposta(banco.Model):
    __tablename__ = 'respostas'
    
    id = banco.Column(banco.Integer, primary_key=True)
    corpo = banco.Column(banco.Text, nullable=False)
    pergunta_id = banco.Column(banco.Integer, banco.ForeignKey('perguntas.id'), nullable=False)
    usuario_id = banco.Column(banco.Integer, banco.ForeignKey('usuarios.id'), nullable=True) # Nulo se for a IA
    eh_ia = banco.Column(banco.Boolean, default=False)
    solucao = banco.Column(banco.Boolean, default=False)
    data_criacao = banco.Column(banco.DateTime, default=datetime.utcnow)

    votos = banco.relationship('Voto', backref='resposta', lazy=True, cascade="all, delete-orphan")

    @property
    def total_likes(self):
        """Conta quantos votos 1 (Like) essa resposta possui"""
        return sum(1 for voto in self.votos if voto.valor == 1)

    @property
    def total_dislikes(self):
        """Conta quantos votos -1 (Dislike) essa resposta possui"""
        return sum(1 for voto in self.votos if voto.valor == -1)