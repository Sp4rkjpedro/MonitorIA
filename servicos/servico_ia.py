import os
import logging
import re
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv
from modelos.entidades import Resposta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ServicoIA:
    def __init__(self, repositorio_resposta, cliente_ia=None):
        self.repositorio_resposta = repositorio_resposta
        caminho_env = Path(__file__).parent.parent / '.env'
        load_dotenv(dotenv_path=caminho_env)
        self.api_key = os.environ.get("GROQ_API_KEY")
        self.client = cliente_ia or Groq(api_key=self.api_key)
        self.modelo = "llama-3.1-8b-instant"

    def buscar_duplicatas(self, rascunho_titulo, lista_perguntas):
        if not rascunho_titulo or not lista_perguntas:
            return []

        contexto = [{"id": p.id, "titulo": p.titulo} for p in lista_perguntas]
        prompt = (
            f"Analise: '{rascunho_titulo}'.\n"
            f"Existentes: {contexto}\n"
            "Se houver duplicata, responda APENAS o ID. Se não, responda 'ZERO'."
        )

        try:
            completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.modelo,
                temperature=0
            )
            resposta = completion.choices[0].message.content.strip()
            id_encontrado = re.search(r'\d+', resposta)
            
            if "ZERO" in resposta.upper() or not id_encontrado:
                return []

            id_final = int(id_encontrado.group())
            return [p for p in lista_perguntas if p.id == id_final]
        except Exception:
            return []

  
    def analisar_melhor_resposta(self, pergunta, lista_respostas):
        if not lista_respostas:
            return None

        # Filtramos para a IA não analisar a própria resposta (se houver)
        contexto = "\n".join([f"ID {r.id}: {r.corpo}" for r in lista_respostas if not r.eh_ia])
        
        if not contexto:
            return None

        prompt = (
            f"Você é um Professor avaliador.\n"
            f"PERGUNTA: {pergunta.titulo} - {pergunta.corpo}\n"
            f"RESPOSTAS CANDIDATAS:\n{contexto}\n"
            "Escolha a resposta mais completa e tecnicamente correta. "
            "Responda APENAS o número do ID escolhido. Se nenhuma prestar, responda ZERO."
        )

        try:
            print(f"\n>>> IA ANALISANDO MELHOR RESPOSTA PARA PERGUNTA: {pergunta.id}")
            
            completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.modelo,
                temperature=0
            )
            
            resposta_ia = completion.choices[0].message.content.strip()
            res_id = re.search(r'\d+', resposta_ia)
            
            resultado = int(res_id.group()) if res_id and "ZERO" not in resposta_ia.upper() else None
            
            print(f">>> IA ESCOLHEU O ID: {resultado}")
            return resultado
            
        except Exception as e:
            print(f">>> ERRO NA ANALISE DE RESPOSTA: {e}")
            return None