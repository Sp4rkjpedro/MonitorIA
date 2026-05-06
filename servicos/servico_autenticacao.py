from werkzeug.security import generate_password_hash, check_password_hash
from modelos.entidades import Usuario
from repositorios.repositorio_usuario import RepositorioUsuario

class ServicoAutenticacao:
    def __init__(self, repositorio: RepositorioUsuario):
        self.repositorio = repositorio

    def registrar_usuario(self, nome: str, email: str, senha: str, papel: str) -> Usuario:
        if not nome or not email or not senha or not papel:
            raise ValueError("Todos os campos são obrigatórios.")
            
        if self.repositorio.buscar_por_email(email):
            raise ValueError("Este e-mail já está em uso. Tente fazer login.")
        
        # Cria o hash da senha para não salvar em texto plano
        senha_criptografada = generate_password_hash(senha)
        
        novo_usuario = Usuario(
            nome=nome, 
            email=email, 
            senha_hash=senha_criptografada, 
            papel=papel
        )
        return self.repositorio.salvar(novo_usuario)

    def autenticar_usuario(self, email: str, senha: str) -> Usuario:
        usuario = self.repositorio.buscar_por_email(email)
        
        # Verifica se o usuário existe e se a senha bate com o hash
        if not usuario or not check_password_hash(usuario.senha_hash, senha):
            raise ValueError("E-mail ou senha incorretos.")
            
        return usuario