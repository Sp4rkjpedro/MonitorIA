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
        """IA-001: Identifica se o título digitado já existe no banco (Semântica)."""
        if not rascunho_titulo or not lista_perguntas:
            return []

        contexto = [{"id": p.id, "titulo": p.titulo} for p in lista_perguntas]
        prompt = (
            f"Analise o título: '{rascunho_titulo}'.\n"
            f"Lista de existentes: {contexto}\n"
            "Se houver alguma duplicata semântica, responda APENAS o ID numérico. "
            "Se não houver nada similar, responda 'ZERO'."
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
        except Exception as e:
            logger.error(f"Erro ao buscar duplicatas: {e}")
            return []

    def verificar_conteudo_adequado(self, texto: str) -> bool:
        """IA-003: Guardrail - Bloqueia xingamentos, insultos e termos inadequados."""
        if not texto or not texto.strip():
            return False

        prompt = (
            "Você é um sistema automatizado de moderação de conteúdo para um fórum acadêmico universitário.\n"
            "Analise estritamente o texto fornecido abaixo.\n"
            "Se o texto contiver QUALQUER palavrão, xingamento, insulto vulgar, grosseria ou ofensa direcionada, seu veredicto deve ser INVALIDO.\n"
            "Se o texto for totalmente respeitoso e adequado para uma sala de aula, seu veredicto deve ser VALIDO.\n\n"
            "Forneça sua resposta final em letras maiúsculas dentro de colchetes, exatamente como nos exemplos: [VALIDO] ou [INVALIDO].\n"
            f"Texto para análise: \"{texto}\""
        )
        try:
            completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.modelo,
                temperature=0.0
            )
            resultado = completion.choices[0].message.content.strip().upper()
            logger.info(f"[GUARDRAIL IA] Resposta bruta da API: '{resultado}' para o texto: '{texto[:30]}...'")
            
            # Bloqueio garantido: Se a palavra INVALIDO aparecer em qualquer lugar da string, rejeita.
            if "INVALIDO" in resultado:
                return False
            return True
        except Exception as e:
            logger.error(f"Erro no Guardrail da IA: {e}")
            return True

    def verificar_coerencia_pedagogica(self, titulo: str, corpo: str) -> bool:
        """IA-004: Filtro de Sentido - Evita spam ou caracteres aleatórios (ex: 'asdfghjk')."""
        if not titulo or not corpo:
            return False

        prompt = (
            "Você é um avaliador de postagens acadêmicas.\n"
            "Determine se a publicação abaixo é uma dúvida real, legítima ou compreensível de um estudante, "
            "ou se constitui apenas spam de teclado, sequências de caracteres aleatórios sem nexo (ex: 'asdf', 'ghjk', 'teste123'), ou texto completamente sem sentido lógico.\n\n"
            "Regra estrita de saída: Responda obrigatoriamente [COERENTE] se for uma dúvida inteligível ou [INCOERENTE] se for lixo/spam de digitação.\n\n"
            f"Título: {titulo}\n"
            f"Corpo: {corpo}"
        )
        try:
            completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.modelo,
                temperature=0.0
            )
            resultado = completion.choices[0].message.content.strip().upper()
            logger.info(f"[COERÊNCIA IA] Resposta bruta da API: '{resultado}'")
            
            # Bloqueio garantido: Se a IA rotular como INCOERENTE, rejeita.
            if "INCOERENTE" in resultado:
                return False
            return True
        except Exception as e:
            logger.error(f"Erro na verificação de coerência: {e}")
            return True

    def gerar_sugestao_monitoria(self, pergunta):
        """IA-002: Gera resposta curta com blocos de código Markdown."""
        prompt = (
            f"Você é o 'MonitorIA', um monitor acadêmico especialista.\n"
            f"DISCIPLINA: {pergunta.disciplina}\n"
            f"DÚVIDA: {pergunta.titulo}\n"
            f"DESCRIÇÃO: {pergunta.corpo}\n\n"
            "INSTRUÇÕES ESTRITAS:\n"
            "1. Responda em no máximo 2 parágrafos curtos.\n"
            "2. Se a resposta envolver código, use OBRIGATORIAMENTE blocos de código Markdown (ex: ```python ou ```java).\n"
            "3. Seja técnico, mas direto ao ponto.\n"
            "4. Comece com: '🤖 Olá! Sou a MonitorIA e preparei esta sugestão inicial:'"
        )

        try:
            logger.info(f"Gerando sugestão otimizada para a pergunta ID {pergunta.id}")
            completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.modelo,
                temperature=0.3
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Erro ao gerar resposta da IA: {e}")
            return None

    def analisar_melhor_resposta(self, pergunta, lista_respostas):
        """Analisa respostas humanas e sugere a melhor para o monitor."""
        if not lista_respostas:
            return None

        contexto = "\n".join([f"ID {r.id}: {r.corpo}" for r in lista_respostas if not r.eh_ia])
        if not contexto:
            return None

        prompt = (
            f"Você é um Professor avaliador de fóruns.\n"
            f"PERGUNTA ORIGINAL: {pergunta.titulo}\n"
            f"RESPOSTAS DOS ALUNOS:\n{contexto}\n"
            "Escolha a resposta tecnicamente mais correta. Responda APENAS o ID."
        )

        try:
            completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.modelo,
                temperature=0
            )
            res_ia = completion.choices[0].message.content.strip()
            res_id = re.search(r'\d+', res_ia)
            return int(res_id.group()) if res_id and "ZERO" not in res_ia.upper() else None
        except Exception as e:
            logger.error(f"Erro na análise de curadoria: {e}")
            return None