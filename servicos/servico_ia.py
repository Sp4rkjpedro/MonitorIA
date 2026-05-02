import os
from groq import Groq
from modelos.entidades import Resposta

class ServicoIA:
    def __init__(self, repositorio_resposta):
        self.repositorio_resposta = repositorio_resposta
        # Certifique-se de ter o 'python-dotenv' instalado e a chave no .env
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    def gerar_resposta_monitor(self, pergunta):
        """
        Gera a 'Primeira Resposta' automática (IA-002).
        Utiliza o Llama 3.1 8B pela velocidade (RNF-002).
        """
        
        # System Prompt: Define a personalidade e evita respostas erradas
        system_prompt = (
            f"Você é o Monitor Virtual da plataforma MonitorIA, especializado em {pergunta.disciplina}. "
            "Sua tarefa é dar uma explicação didática inicial para a dúvida do aluno. "
            "Regras: 1. Seja direto. 2. Se houver código, use markdown. "
            "3. Explique o conceito e não apenas dê a resposta. "
            "4. Avise que você é uma IA e que um monitor humano revisará sua resposta."
        )

        try:
            # Chamada para o Groq
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": pergunta.corpo}
                ],
                model="llama-3.1-8b-instant", # Escolha baseada no nosso debate técnico
                temperature=0.5, # Menor criatividade = maior precisão técnica
                max_tokens=1024
            )

            texto_gerado = chat_completion.choices[0].message.content

            # Criando o objeto de Resposta com a flag eh_ia=True (Requisito IA-002.3)
            nova_resposta = Resposta(
                corpo=texto_gerado,
                pergunta_id=pergunta.id,
                eh_ia=True,      # Crucial para a diferenciação visual no HTML
                eh_solucao=False, # IA nunca pode ser a solução definitiva
                usuario_id=None   # ID nulo pois não é um humano
            )

            return self.repositorio_resposta.salvar(nova_resposta)

        except Exception as e:
            print(f"Erro na integração com Groq: {e}")
            return None