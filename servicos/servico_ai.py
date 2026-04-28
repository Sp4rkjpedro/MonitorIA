import os
from groq import Groq

class ServicoAI:
    def __init__(self):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    def gerar_resposta_monitoria(self, pergunta):
        prompt_sistema = f"Você é um monitor de {pergunta.disciplina}. Seja didático."
        try:
            completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": f"{pergunta.titulo}: {pergunta.corpo}"}
                ],
                model="llama3-8b-8192",
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Erro na IA: {e}"

    def buscar_duplicatas(self, rascunho_titulo, lista_titulos_existentes):
        # Aqui você criará a lógica da IA-001 depois
        pass