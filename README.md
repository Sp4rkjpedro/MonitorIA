🤖 MonitorIA - Fórum Acadêmico Inteligente com IA
O MonitorIA é uma plataforma de perguntas e respostas (estilo Stack Overflow) desenvolvida especificamente para o ambiente universitário. O grande diferencial do sistema é a integração de um Monitor Virtual baseado em Inteligência Artificial, que realiza um primeiro atendimento instantâneo ao aluno, otimizando o tempo dos monitores humanos e evitando a sobrecarga com dúvidas repetitivas.

🛠️ Tecnologias e Ferramentas
O projeto foi construído utilizando tecnologias modernas e eficientes para garantir performance, escalabilidade e código limpo:

Backend: Python 3 + Flask (Microframework rápido e robusto)

Persistência de Dados: Flask-SQLAlchemy (ORM para mapeamento e manipulação do banco de dados sem necessidade de SQL puro)

Banco de Dados: SQLite (Armazenamento local leve em arquivo dentro da pasta instance, ideal para desenvolvimento e testes rápidos)

Motor de Inteligência Artificial: API do Groq (Modelo Llama 3) para geração de respostas e busca semântica em tempo real

Variáveis de Ambiente: Python-dotenv (Segurança e isolamento de chaves de API e credenciais)

Frontend: HTML5, CSS3 (Interface responsiva com design moderno em Dark Mode roxo) e JavaScript Nativo (Manipulação assíncrona para comunicação com o servidor sem recarregamento de página)

Renderização de Texto: Marked.js (para Markdown) e Highlight.js (para coloração de blocos de código de programação)

🚀 Estrutura Arquitetural (Padrão Clean Code)
O código foi organizado seguindo princípios de arquitetura em camadas, separando responsabilidades para facilitar a manutenção e evolução do sistema:

modelos/ / models/: Contém as definições das tabelas do banco de dados representadas como classes Python (Usuário, Pergunta, Resposta).

repositorios/ / repositories/: Camada responsável por executar operações diretas de leitura e escrita no banco de dados (Queries).

servicos/ / services/: Onde fica a lógica pesada de negócio, incluindo as regras de validação e a comunicação direta com a API do Groq.

controles/ / routes/: Gerencia as rotas das páginas, intercepta as requisições dos usuários e direciona para os serviços corretos.

templates/: Arquivos HTML estruturados da interface do usuário.

🧠 Recursos de Inteligência Artificial
O uso de IA no sistema foi projetado para agregar valor pedagógico e melhorar a experiência do usuário através de dois fluxos principais:

IA-001 (Detecção de Duplicatas): Enquanto o aluno digita o título de uma nova dúvida, o sistema realiza uma varredura semântica utilizando Embeddings no banco de dados para identificar perguntas similares já respondidas, mitigando a criação de tópicos repetidos.

IA-002 (Monitor Virtual Automático): No exato momento em que uma pergunta é publicada, a API do Groq gera uma resposta técnica inicial.

Tratamento de Código: A interface foi desenvolvida utilizando propriedades como white-space: pre-wrap para garantir que quebras de linha e blocos de códigos de programação enviados pela IA mantenham a formatação correta.

Moderação: A resposta da IA fica permanentemente identificada como "Sugestão da MonitorIA" no topo da página, deixando claro ao aluno que o conteúdo ainda não passou por validação humana.

👥 Sistema de Governança e Regras de Negócio
Interação Humana: Alunos e Monitores têm permissão para criar novas perguntas, responder tópicos existentes na comunidade e votar (Upvote/Downvote) nas soluções fornecidas por humanos.

Resolução Oficial: Apenas o Autor da Pergunta ou um Monitor do sistema possuem o privilégio de atribuir o selo de "Solução Oficial" para a resposta que melhor resolveu o problema (exibindo o botão de moderação dinamicamente de acordo com o nível de acesso do usuário).

🔧 Como Iniciar o Projeto Localmente
Siga o passo a passo abaixo para rodar o projeto na sua máquina de desenvolvimento:

1. Clonar o repositório:
Execute os comandos para clonar e acessar a pasta:
git clone https://github.com/Sp4rkjpedro/MonitorIA.git
cd MonitorIA

2. Instalar as dependências:
Instale todos os pacotes necessários diretamente na sua máquina executando:
pip install -r requirements.txt

3. Configurar as Variáveis de Ambiente:
Crie um arquivo chamado .env na raiz do projeto e adicione suas chaves credenciais:
GROQ_API_KEY=sua_chave_da_api_aqui
SECRET_KEY=uma_chave_secreta_para_sessoes_flask

4. Inicializar o Banco de Dados:
Para garantir um banco de dados limpo e estruturado antes de rodar, execute no console do Python:
from app import app, db
with app.app_context():
db.create_all()

5. Executar a Aplicação:
Rode o servidor do Flask com o comando:
python app.py

O servidor iniciará localmente. Abra o navegador e acesse http://127.0.0.1:5000.

🔮 Próximos Passos e Melhorias Futuras
Implementação de um sistema de comentários encadeados ("resposta da resposta") para permitir discussões diretas e réplicas dentro de uma resposta específica sem poluir o feed principal de soluções.