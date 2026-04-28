from modelos.entidades import Pergunta
from extensoes import banco

class RepositorioPergunta:
    def salvar(self, pergunta: Pergunta) -> Pergunta:
        banco.session.add(pergunta)
        banco.session.commit()
        return pergunta

    def buscar_todas(self) -> list[Pergunta]:
        return Pergunta.query.order_by(Pergunta.data_criacao.desc()).all()

    def buscar_por_id(self, id_pergunta: int) -> Pergunta:
        return Pergunta.query.get(id_pergunta)