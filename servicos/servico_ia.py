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

    def buscar_duplicatas(self, rascunho_titulo, rascunho_corpo, rascunho_disciplina, lista_perguntas):
        """IA-001: Identifica duplicatas filtrando estritamente por disciplina no Python antes de chamar a IA."""
        if not rascunho_titulo or not lista_perguntas or not rascunho_disciplina:
            return []

        # 🚀 FILTRO ESTRUTURAL EM PYTHON: Isola apenas as dúvidas da matéria correspondente
        perguntas_mesma_disciplina = [
            p for p in lista_perguntas 
            if getattr(p, 'disciplina', '').strip().lower() == rascunho_disciplina.strip().lower()
        ]

        # Se não há registros prévios nesta disciplina, não há o que validar
        if not perguntas_mesma_disciplina:
            logger.info(f"[DUPLICATAS] Nenhuma pergunta existente cadastrada na disciplina '{rascunho_disciplina}'. Aprovado automaticamente.")
            return []

        # Transforma apenas a lista filtrada em entradas limpas de texto
        linhas = []
        for p in perguntas_mesma_disciplina:
            tit = getattr(p, 'titulo', '').strip()
            linhas.append(f"DATABASE_ENTRY -> ID: {p.id} | TITULO: {tit}")
        
        texto_existentes = "\n".join(linhas)

        prompt = (
            "Determine se a nova pergunta é uma duplicata conceitual ou idêntica de algum item da lista abaixo.\n\n"
            "[NOVA PERGUNTA CANDIDATA]\n"
            f"TITULO_SOLICITADO: {rascunho_titulo}\n\n"
            f"[PERGUNTAS EXISTENTES NA DISCIPLINA {rascunho_disciplina.upper()}]\n"
            f"{texto_existentes}\n\n"
            "REGRA DE SAÍDA ESTRITA:\n"
            "- Se encontrar um título com o mesmo conceito ou assunto idêntico, retorne APENAS o número do ID (ex: 10).\n"
            "- Se não houver duplicata idêntica, retorne APENAS: ZERO\n"
            "Proibido adicionar justificativas, pontuações ou explicações. Responda com uma única palavra."
        )

        try:
            completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.modelo,
                temperature=0.0  # Máximo determinismo
            )
            resposta = completion.choices[0].message.content.strip().upper()
            
            logger.info(f"[DUPLICATAS IA] Avaliação de assunto em '{rascunho_disciplina}'. Resposta da Groq: '{resposta}'")
            
            if "ZERO" in resposta or not resposta:
                return []

            id_encontrado = re.search(r'\d+', resposta)
            if not id_encontrado:
                return []

            id_final = int(id_encontrado.group())
            return [p for p in perguntas_mesma_disciplina if p.id == id_final]
        except Exception as e:
            logger.error(f"Erro ao buscar duplicatas: {e}")
            return []

    def verificar_conteudo_adequado(self, texto: str) -> bool:
        """IA-003: Guardrail - Bloqueia rigidamente ofensas, difamações e desrespeito acadêmico."""
        if not texto or not texto.strip():
            return False

        prompt = (
            "Você é um moderador de conteúdo estrito para um fórum universitário.\n"
            "Sua tarefa é avaliar se o texto abaixo viola as regras de respeito e convivência.\n\n"
            "REGRAS DE BLOQUEIO [INVALIDO]:\n"
            "- Bloqueie qualquer texto que contenha xingamentos, insultos (como chamar alguém de mané, burro, incompetente, etc.).\n"
            "- Bloqueie insinuações difamatórias, deboche contra a equipe, professores, monitores ou colegas (ex: 'comprou o diploma', 'essa merda').\n"
            "- Bloqueie agressividade verbal crassa e ataques pessoais.\n\n"
            "REGRAS DE LIBERAÇÃO [VALIDO]:\n"
            "- Permita dúvidas reais mesmo que escritas com erros de português, gírias leves de internet, frustrações estritamente técnicas com o código ou desabafos de cansaço com a matéria (ex: 'não aguento mais esse erro', 'tá muito difícil entender listas').\n\n"
            f"Texto para análise: \"{texto}\"\n\n"
            "Regra de Saída Estrita: Responda APENAS [VALIDO] ou [INVALIDO]. Não adicione nenhuma justificativa ou explicação adicional."
        )
        try:
            completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.modelo,
                temperature=0.0
            )
            resultado = completion.choices[0].message.content.strip().upper()
            logger.info(f"[GUARDRAIL IA] Resposta bruta da API: '{resultado}'")
            
            if "INVALIDO" in resultado and "VALIDO" not in resultado:
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
            "Determine se a publicação abaixo é uma dúvida compreensível de um estudante ou apenas spam de teclado sem nexo (ex: 'asdf', 'ghjk').\n\n"
            f"Título: {titulo}\n"
            f"Corpo: {corpo}\n\n"
            "Regra estrita de saída: Responda obrigatoriamente [COERENTE] se for inteligível ou [INCOERENTE] se for lixo/spam de digitação. Não adicione mais nada."
        )
        try:
            completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.modelo,
                temperature=0.0
            )
            resultado = completion.choices[0].message.content.strip().upper()
            logger.info(f"[COERÊNCIA IA] Resposta bruta da API: '{resultado}'")
            
            if "INCOERENTE" in resultado and "COERENTE" not in resultado:
                return False
            return True
        except Exception as e:
            logger.error(f"Erro na verificação de coerência: {e}")
            return True

    def gerar_sugestao_monitoria(self, pergunta):
        """IA-002: Gera resposta corta com blocos de código Markdown."""
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