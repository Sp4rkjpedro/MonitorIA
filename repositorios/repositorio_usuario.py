from modelos.entidades import Usuario
from extensoes import banco

class RepositorioUsuario:
    def salvar(self, usuario: Usuario) -> Usuario:
        banco.session.add(usuario)
        banco.session.commit()
        return usuario

    def buscar_por_email(self, email: str) -> Usuario:
        return Usuario.query.filter_by(email=email).first()

    def buscar_por_id(self, id_usuario: int) -> Usuario:
        return Usuario.query.get(id_usuario)