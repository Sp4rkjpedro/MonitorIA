import os
import logging
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv
from modelos.entidades import Resposta

# Configuração do Log de Erros
# Isso vai mostrar no seu terminal mensagens como [ERROR] ou [INFO]
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ServicoIA:
    def __init__(self, repositorio_resposta):
        self.repositorio_resposta = repositorio_resposta
        
        # Carregamento do ambiente
        caminho_env = Path(__file__).parent.parent / '.env'
        load_dotenv(dotenv_path=caminho_env)
        
        self.api_key = os.environ.get("GROQ_API_KEY")
        
        if not self.api_key:
            logger.error("CHAVE NÃO ENCONTRADA: O arquivo .env está ausente ou a GROQ_API_KEY não foi definida.")
            
        self.client = Groq(api_key=self.api_key)

    def gerar_resposta_monitor(self, pergunta):
        """Gera resposta automática e loga falhas na API (IA-002)."""
        if not self.api_key:
            logger.warning(f"Abortando resposta para Pergunta {pergunta.id}: API Key faltando.")
            return None

        system_prompt = (
            f"Você é o Monitor Virtual de {pergunta.disciplina}. "
            "Dê uma explicação didática inicial, use Markdown para código e "
            "avise que um humano revisará esta resposta."
        )

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Dúvida: {pergunta.corpo}"}
                ],
                model="llama-3.1-8b-instant",
                temperature=0.5
            )

            texto_gerado = chat_completion.choices[0].message.content

            nova_resposta = Resposta(
                corpo=texto_gerado,
                pergunta_id=pergunta.id,
                eh_ia=True,
                eh_solucao=False
            )

            logger.info(f"Sucesso: Resposta da IA gerada para a pergunta {pergunta.id}")
            return self.repositorio_resposta.salvar(nova_resposta)

        except Exception as e:
            # Aqui é onde o erro da API é capturado e detalhado no seu terminal
            logger.error(f"FALHA NA API GROQ (Pergunta {pergunta.id}): {str(e)}")
            
            # Opcional: Criar uma resposta de erro amigável para o usuário no banco
            erro_msg = Resposta(
                corpo="O Monitor Virtual teve um problema técnico e não pôde responder agora. Um monitor humano verá sua dúvida em breve.",
                pergunta_id=pergunta.id,
                eh_ia=True
            )
            self.repositorio_resposta.salvar(erro_msg)
            return None

    def buscar_duplicatas(self, rascunho_titulo, lista_perguntas):
        """Busca duplicatas e loga erros de comunicação (IA-001)."""
        if not rascunho_titulo or len(rascunho_titulo) < 10:
            return []

        titulos_existentes = [{"id": p.id, "titulo": p.titulo} for p in lista_perguntas]
        prompt = f"ID da pergunta similar a '{rascunho_titulo}' nesta lista: {titulos_existentes}. Se nada, responda 'ZERO'."

        try:
            completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
                temperature=0
            )
            
            resposta = completion.choices[0].message.content.strip()
            
            if "ZERO" in resposta.upper():
                return []
            
            id_encontrado = int(''.join(filter(str.isdigit, resposta)))
            logger.info(f"Duplicata encontrada: Pergunta digitada remete ao ID {id_encontrado}")
            return [p for p in lista_perguntas if p.id == id_encontrado]

        except Exception as e:
            logger.error(f"ERRO AO BUSCAR DUPLICATAS: {str(e)}")
            return []