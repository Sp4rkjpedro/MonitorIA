import os
from groq import Groq
from modelos.entidades import Resposta

class ServicoIA:
    def __init__(self, repositorio_resposta):
        self.repositorio_resposta = repositorio_resposta
        # A chave será lida do .env carregado no app.py
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    def gerar_resposta_monitor(self, pergunta):
        """Gera a explicação didática automática (IA-002)."""
        system_prompt = (
            f"Você é o Monitor Virtual da plataforma MonitorIA, especializado em {pergunta.disciplina}. "
            "Sua tarefa é dar uma explicação didática inicial para a dúvida do aluno. "
            "Regras: 1. Seja direto. 2. Use markdown para código. "
            "3. Explique o conceito. 4. Avise que você é uma IA e um humano revisará isso."
        )

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Título: {pergunta.titulo}\nDúvida: {pergunta.corpo}"}
                ],
                model="llama-3.1-8b-instant",
                temperature=0.5,
                max_tokens=1024
            )

            texto_gerado = chat_completion.choices[0].message.content

            # Criando o objeto para o banco de dados
            nova_resposta = Resposta(
                corpo=texto_gerado,
                pergunta_id=pergunta.id,
                eh_ia=True,
                eh_solucao=False,
                usuario_id=None
            )

            return self.repositorio_resposta.salvar(nova_resposta)

        except Exception as e:
            print(f" Erro Groq: {e}")
            return None

    def buscar_duplicatas(self, rascunho_titulo, lista_perguntas):
        """Espaço reservado para a funcionalidade IA-001."""
        pass