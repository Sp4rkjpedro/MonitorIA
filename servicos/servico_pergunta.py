from modelos.entidades import Pergunta
from repositorios.repositorio_pergunta import RepositorioPergunta

class ServicoPergunta:
    def __init__(self, repositorio: RepositorioPergunta):
        self.repositorio = repositorio

    def criar_pergunta(self, dados: dict) -> Pergunta:
        # Fail Fast: Validação básica
        if not dados.get('titulo') or not dados.get('corpo'):
            raise ValueError("Os campos 'titulo' e 'corpo' são obrigatórios.")
        if not dados.get('disciplina'):
            raise ValueError("O campo 'disciplina' é obrigatório.")
            
        nova_pergunta = Pergunta(
            titulo=dados['titulo'],
            corpo=dados['corpo'],
            disciplina=dados['disciplina'],
            usuario_id=dados['usuario_id']
        )
        
        pergunta_salva = self.repositorio.salvar(nova_pergunta)
        
        # [Fase 4] A chamada assíncrona para o Groq (IA-002) será disparada aqui
        # self._disparar_ia_assincrona(pergunta_salva)
        
        return pergunta_salva

    def listar_todas(self) -> list[Pergunta]:
        return self.repositorio.buscar_todas()

    def buscar_detalhes(self, id_pergunta: int) -> Pergunta:
        pergunta = self.repositorio.buscar_por_id(id_pergunta)
        if not pergunta:
            raise ValueError("Pergunta não encontrada.")
        return pergunta