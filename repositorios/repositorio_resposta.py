from modelos.entidades import Resposta
from extensoes import banco

class RepositorioResposta:
    def salvar(self, resposta: Resposta) -> Resposta:
        """Salva uma nova resposta (da IA ou Humana) no banco de dados."""
        banco.session.add(resposta)
        banco.session.commit()
        return resposta